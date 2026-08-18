# Legal Governor API boundary

The existing Cloudflare Worker is the public intake API. Legal analysis is
currently local, command-driven, and source-controlled because no authenticated
provider/database deployment has been configured. The supported service boundary
is:

```text
POST /legal/analyze      -> create a source-backed matter request
POST /legal/research     -> enqueue retrieval work
POST /legal/verify       -> write a verification bundle
POST /legal/red-team     -> record adverse/red-team work
GET  /legal/requests/:id/governor -> return final gate status
POST /legal/review/:id   -> append human counsel review
```

These routes are an interface contract, not a claim that an unauthenticated
public endpoint currently executes them. Until an authenticated API service is
deployed, use the `bin/glaw-legal-governor` commands. Credentials and live
provider endpoints must be configured before enabling remote execution.
