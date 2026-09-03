import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { basename, dirname, extname, join, relative, resolve } from "node:path";

const HOME = "/Users/ricardoprieto";
const PROJECTS = join(HOME, "projects");
const OUT = join(process.cwd(), "exports", "project-inventory");
const NOW = new Date().toISOString();
const SKIP = new Set([
  ".git", ".svn", ".hg", "node_modules", ".wrangler", "dist", "build", ".next", ".astro",
  ".cache", ".turbo", ".venv", "venv", "target", "coverage", "Library", "Downloads",
  ".cloudflare-tokens", ".api-tokens", ".ssh", ".aws", ".npm", ".codex", ".agents",
]);
const MANIFESTS = new Map([
  ["package.json", "javascript"], ["wrangler.jsonc", "cloudflare-worker"], ["wrangler.toml", "cloudflare-worker"],
  ["pyproject.toml", "python"], ["Cargo.toml", "rust"], ["go.mod", "go"], ["composer.json", "php"],
  ["Gemfile", "ruby"], ["astro.config.mjs", "astro"], ["astro.config.ts", "astro"],
]);

mkdirSync(OUT, { recursive: true });

function command(file, args, cwd = HOME) {
  try {
    return execFileSync(file, args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], maxBuffer: 40 * 1024 * 1024 });
  } catch (error) {
    return error.stdout?.toString() || "";
  }
}

function safeJson(text, fallback = []) {
  try { return JSON.parse(text); } catch { return fallback; }
}

function snapshot(name, fallback = "") {
  const file = join(OUT, name);
  return existsSync(file) ? readFileSync(file, "utf8") : fallback;
}

function cloudflareOutput(name, args) {
  const file = join(OUT, name);
  return existsSync(file) ? readFileSync(file, "utf8") : command("npx", ["wrangler", ...args, ...cfConfig]);
}

function csvCell(value) {
  const text = value === null || value === undefined ? "" : typeof value === "object" ? JSON.stringify(value) : String(value);
  return `"${text.replaceAll('"', '""').replaceAll("\n", "\\n")}"`;
}

function hash(value) { return createHash("sha256").update(value).digest("hex").slice(0, 16); }

function readManifest(dir, file) {
  try {
    const raw = readFileSync(join(dir, file), "utf8");
    if (file === "package.json") {
      const pkg = safeJson(raw, {});
      return { name: pkg.name || basename(dir), description: pkg.description || null, version: pkg.version || null, private: pkg.private === true };
    }
    return { name: basename(dir), description: null, version: null, private: null };
  } catch { return { name: basename(dir), description: null, version: null, private: null }; }
}

function manifestLocations(root) {
  const args = ["--files"];
  for (const manifest of MANIFESTS.keys()) args.push("-g", manifest);
  for (const excluded of SKIP) args.push("-g", `!**/${excluded}/**`, "-g", `!${excluded}/**`);
  const output = command("rg", args, root);
  return output.split("\n").filter(Boolean).map((file) => join(root, file));
}

function gitMetadata(dir) {
  if (!existsSync(join(dir, ".git"))) return {};
  const remote = command("git", ["config", "--get", "remote.origin.url"], dir).trim();
  const branch = command("git", ["branch", "--show-current"], dir).trim();
  const status = command("git", ["status", "--porcelain"], dir).trim();
  const remoteUrl = remote.replace(/^git@github\.com:/, "https://github.com/").replace(/\.git$/, "");
  return { git: true, remoteUrl: remoteUrl || null, branch: branch || null, dirty: status.length > 0 };
}

const projects = [];
const seen = new Set();
for (const base of [HOME]) {
  const byDirectory = new Map();
  for (const file of manifestLocations(base)) {
    const dir = dirname(file);
    const manifestName = basename(file);
    if (!byDirectory.has(dir)) byDirectory.set(dir, []);
    byDirectory.get(dir).push(manifestName);
  }
  for (const [dir, manifests] of byDirectory) {
    const key = resolve(dir);
    if (seen.has(key)) continue;
    seen.add(key);
    const primary = manifests.find((file) => file === "package.json") || manifests[0];
    const manifest = readManifest(dir, primary);
    const git = gitMetadata(dir);
    const rel = relative(HOME, dir);
    projects.push({
      id: `local-${hash(key)}`, source: "local", type: MANIFESTS.get(primary), name: manifest.name,
      parent_id: dirname(dir) === HOME ? null : `local-${hash(resolve(dirname(dir)))}`,
      root_path: dir, relative_path: rel, url: git.remoteUrl || null, status: "discovered",
      description: manifest.description, version: manifest.version, private: manifest.private,
      manifests, git: git.git === true, git_branch: git.branch || null, dirty: git.dirty || false,
      discovered_at: NOW,
    });
  }
}

const githubSnapshot = join(OUT, "github-repositories.json");
const github = existsSync(githubSnapshot)
  ? safeJson(readFileSync(githubSnapshot, "utf8"))
  : safeJson(command("gh", ["repo", "list", "--limit", "1000", "--json", "nameWithOwner,name,isPrivate,defaultBranchRef,updatedAt,description,url,sshUrl,owner,licenseInfo"]));
const githubProjects = github.map((repo) => ({
  id: `github-${hash(repo.nameWithOwner)}`, source: "github", type: "repository", name: repo.name,
  parent_id: null, root_path: null, relative_path: null, url: repo.url || null, status: "accessible",
  description: repo.description || null, version: null, private: repo.isPrivate === true,
  manifests: [], git: true, git_branch: repo.defaultBranchRef?.name || null, dirty: null,
  discovered_at: NOW, github_owner: repo.owner?.login || null, github_name_with_owner: repo.nameWithOwner,
  updated_at: repo.updatedAt || null, ssh_url: repo.sshUrl || null, license: repo.licenseInfo?.name || null,
}));
const githubAccount = {
  id: `github-${github[0]?.owner?.login || "unknown"}`,
  provider: "github",
  label: github[0]?.owner?.login || "unknown",
  email: null,
  account_id: github[0]?.owner?.id || null,
  login: github[0]?.owner?.login || null,
  auth_status: github.length > 0 ? "authenticated" : "not_enumerable",
  secrets_exported: false,
};

function parseTable(text, headers) {
  const lines = text.split("\n").map((line) => line.replaceAll(/\u001b\[[0-9;]*m/g, "")).filter((line) => line.includes("│"));
  const rows = [];
  for (const line of lines.slice(1)) {
    const cells = line.split("│").slice(1, -1).map((cell) => cell.trim());
    if (cells.length !== headers.length || cells.every((cell) => !cell)) continue;
    if (cells.every((cell) => /^[-─]+$/.test(cell))) continue;
    rows.push(Object.fromEntries(headers.map((header, index) => [header, cells[index] || null])));
  }
  return rows;
}

const cfConfig = ["--config", "wrangler.local.jsonc"];
const account = { id: "cf-e9a13cb086224245b63e1e902c7afc64", provider: "cloudflare", label: "Rikitrader Gmail Account", email: "rikitrader@gmail.com", account_id: "e9a13cb086224245b63e1e902c7afc64", auth_status: "authenticated", secrets_exported: false };
const resources = [];
const cfProject = `cloudflare-account-${account.account_id}`;
function addResources(type, rows, fields) {
  for (const row of rows) resources.push({ id: `cloudflare-${type}-${hash(JSON.stringify(row))}`, project_id: cfProject, account_id: account.id, provider: "cloudflare", resource_type: type, name: row[fields.name] || null, resource_id: row[fields.id] || null, status: "accessible", metadata: row });
}
if (process.env.INVENTORY_SKIP_CLOUDFLARE !== "1") {
  addResources("d1", parseTable(cloudflareOutput("cloudflare-d1.txt", ["d1", "list"]), ["uuid", "name", "created_at", "version", "num_tables", "file_size", "jurisdiction"]), { name: "name", id: "uuid" });
  addResources("kv", safeJson(cloudflareOutput("cloudflare-kv.json", ["kv", "namespace", "list"])), { name: "title", id: "id" });
  addResources("queue", parseTable(cloudflareOutput("cloudflare-queues.txt", ["queues", "list"]), ["id", "name", "created_on", "modified_on", "producers", "consumers"]), { name: "name", id: "id" });
  addResources("vectorize", parseTable(cloudflareOutput("cloudflare-vectorize.txt", ["vectorize", "list"]), ["name", "dimensions", "metric", "description", "created", "modified"]), { name: "name", id: "name" });
  addResources("pages", parseTable(cloudflareOutput("cloudflare-pages.txt", ["pages", "project", "list"]), ["project_name", "domains", "git_provider", "last_modified"]), { name: "project_name", id: "project_name" });
  resources.push({ id: `cloudflare-r2-unavailable-${hash(account.account_id)}`, project_id: cfProject, account_id: account.id, provider: "cloudflare", resource_type: "r2", name: null, resource_id: null, status: "not_enumerable", metadata: { reason: "Cloudflare API reported R2 is not enabled for this account", secrets_exported: false } });
}

const allProjects = [
  ...projects,
  ...githubProjects,
  { id: cfProject, source: "cloudflare", type: "account", name: account.label, parent_id: null, root_path: null, relative_path: null, url: "https://dash.cloudflare.com/" + account.account_id, status: "accessible", description: "Cloudflare account resource inventory", version: null, private: true, manifests: [], git: false, git_branch: null, dirty: null, discovered_at: NOW },
];
const projectIds = new Set(allProjects.map((project) => project.id));
for (const project of allProjects) if (project.parent_id && !projectIds.has(project.parent_id)) project.parent_id = null;
allProjects.sort((a, b) => (a.root_path || "").split("/").length - (b.root_path || "").split("/").length);
const accounts = [githubAccount, account];
const inventory = { schema_version: "1.0.0", generated_at: NOW, scope: { local_roots: [PROJECTS, join(HOME, "code"), join(HOME, "apps")], github: "authenticated gh account repositories", cloudflare: "authenticated Wrangler account resources" }, safety: { secrets_exported: false, excluded: ["tokens", "passwords", "cookies", "private keys", "API key values", ".env contents", "Cloudflare encrypted credential files"] }, accounts, projects: allProjects, resources, counts: { local_projects: projects.length, github_repositories: githubProjects.length, cloudflare_resources: resources.length } };

writeFileSync(join(OUT, "inventory.json"), JSON.stringify(inventory, null, 2) + "\n");
writeFileSync(join(OUT, "projects.csv"), ["id,source,type,name,parent_id,root_path,url,status,private,description,git_branch,dirty,updated_at", ...allProjects.map((p) => [p.id,p.source,p.type,p.name,p.parent_id,p.root_path,p.url,p.status,p.private,p.description,p.git_branch,p.dirty,p.updated_at].map(csvCell).join(","))].join("\n") + "\n");
writeFileSync(join(OUT, "resources.csv"), ["id,project_id,account_id,provider,resource_type,name,resource_id,status,metadata", ...resources.map((r) => [r.id,r.project_id,r.account_id,r.provider,r.resource_type,r.name,r.resource_id,r.status,r.metadata].map(csvCell).join(","))].join("\n") + "\n");
writeFileSync(join(OUT, "accounts.csv"), ["id,provider,label,email,account_id,auth_status,secrets_exported", ...accounts.map((a) => [a.id,a.provider,a.label,a.email,a.account_id,a.auth_status,a.secrets_exported].map(csvCell).join(","))].join("\n") + "\n");

const sql = [
  "PRAGMA foreign_keys = ON;",
  "DROP TABLE IF EXISTS resources;",
  "DROP TABLE IF EXISTS projects;",
  "DROP TABLE IF EXISTS accounts;",
  "CREATE TABLE accounts (id TEXT PRIMARY KEY, provider TEXT NOT NULL, label TEXT, email TEXT, account_id TEXT, auth_status TEXT, secrets_exported INTEGER NOT NULL);",
  "CREATE TABLE projects (id TEXT PRIMARY KEY, source TEXT NOT NULL, type TEXT NOT NULL, name TEXT NOT NULL, parent_id TEXT, root_path TEXT, url TEXT, status TEXT, private INTEGER, description TEXT, metadata_json TEXT NOT NULL, FOREIGN KEY(parent_id) REFERENCES projects(id));",
  "CREATE TABLE resources (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, account_id TEXT, provider TEXT NOT NULL, resource_type TEXT NOT NULL, name TEXT, resource_id TEXT, status TEXT, metadata_json TEXT NOT NULL, FOREIGN KEY(project_id) REFERENCES projects(id), FOREIGN KEY(account_id) REFERENCES accounts(id));",
  ...accounts.map((a) => `INSERT INTO accounts VALUES (${[a.id,a.provider,a.label,a.email,a.account_id,a.auth_status,a.secrets_exported ? 1 : 0].map((v) => `'${String(v ?? "").replaceAll("'", "''")}'`).join(",")});`),
  ...allProjects.map((p) => `INSERT INTO projects VALUES (${[p.id,p.source,p.type,p.name,p.parent_id,p.root_path,p.url,p.status,p.private == null ? null : p.private ? 1 : 0, p.description, JSON.stringify(p)].map((v) => v === null ? "NULL" : `'${String(v).replaceAll("'", "''")}'`).join(",")});`),
  ...resources.map((r) => `INSERT INTO resources VALUES (${[r.id,r.project_id,r.account_id,r.provider,r.resource_type,r.name,r.resource_id,r.status,JSON.stringify(r.metadata)].map((v) => `'${String(v ?? "").replaceAll("'", "''")}'`).join(",")});`),
].join("\n") + "\n";
writeFileSync(join(OUT, "inventory.sql"), sql);
try { execFileSync("sqlite3", [join(OUT, "inventory.sqlite"), `.read ${join(OUT, "inventory.sql")}`], { encoding: "utf8" }); } catch { /* SQL export remains available if sqlite3 is unavailable. */ }

const readme = `# GLAW project inventory\n\nGenerated: ${NOW}\n\nThis export is a metadata-only inventory for upload or reconciliation. It includes local projects discovered from manifests under \`${HOME}\`, GitHub repositories visible to the active \`gh\` account, and Cloudflare resources visible to the active Wrangler account.\n\n## Files\n\n- \`inventory.sqlite\`: relational database with accounts, projects, and resources.\n- \`inventory.json\`: lossless structured export.\n- \`projects.csv\`, \`resources.csv\`, \`accounts.csv\`: flat-file imports.\n- \`inventory.sql\`: portable SQLite DDL/data.\n\n## Safety\n\nNo secret values are exported. Tokens, passwords, cookies, private keys, API-key values, .env contents, and encrypted credential files are excluded. The account ID, email, repository URLs, resource IDs, and non-secret access status are operational metadata.\n\n## Coverage\n\nLocal scan root: \`${HOME}\`; dependency, cache, credential, build, hidden-system, and VCS internals are skipped. GitHub includes repositories returned by the authenticated \`gh repo list\` account. Cloudflare includes D1, KV, Queues, Vectorize, and Pages resources returned by Wrangler. R2 is recorded as \`not_enumerable\` because the API reported that R2 is not enabled.\n\nThis is a point-in-time snapshot, not a live synchronization. Re-run \`node scripts/build-inventory.mjs\` after authenticating another GitHub or Cloudflare account to create another account-specific snapshot.\n`;
writeFileSync(join(OUT, "README.md"), readme);
console.log(JSON.stringify({ output: OUT, ...inventory.counts, accounts: inventory.accounts.map(({ provider, email, account_id }) => ({ provider, email, account_id })), generated_at: NOW }, null, 2));
