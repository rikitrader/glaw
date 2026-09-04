# Test Coverage Map

## Current evidence

- Repository contains substantial shell, Python, JavaScript, benchmark, and
  sandbox artifacts.
- Legal-10K benchmark packs and red/blue/governor run artifacts exist.
- `control-plane` includes local smoke/test scripts.
- `glaw-doctor` and hard gates provide broad health checks.

## Coverage requiring explicit expansion

- cross-tenant, privilege, and ethical-wall negative tests;
- duplicate commands, duplicate webhooks, restart, timeout-before/after-effect;
- workflow replay and reconciliation;
- registry schema compatibility;
- model canary rollback;
- malicious documents and prompt/tool injection;
- accessibility and authenticated UI end-to-end flows;
- multi-region and restore testing.

The file count is not treated as coverage quality until tests are classified and
executed by subsystem.
