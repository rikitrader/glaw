export type D1Statement = {
  bind: (...values: unknown[]) => D1Statement;
  first<T = Record<string, unknown>>(): Promise<T | null>;
  all<T = Record<string, unknown>>(): Promise<{ results: T[] }>;
  run(): Promise<{ success?: boolean; meta?: Record<string, unknown> }>;
};

export type ControlPlaneDb = {
  prepare(sql: string): D1Statement;
  batch<T = Record<string, unknown>>(statements: D1Statement[]): Promise<Array<{ results?: T[]; success?: boolean }>>;
};

export function getControlPlaneDb(env: Record<string, unknown>): ControlPlaneDb {
  const db = env.GLAW_DB as ControlPlaneDb | undefined;
  if (!db) throw new Error("GLAW_DB binding is not configured");
  return db;
}
