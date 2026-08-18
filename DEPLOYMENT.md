# Deployment

The supported baseline is the repository's zero-dependency local/container
execution. `packaging/Containerfile` packages the source tree; no credentials
are included. The Cloudflare Worker serves public intake and must use a secret
for administrative reads.

Optional provider deployment requires explicit configuration and a provider
adapter. Missing credentials or unavailable SDKs must produce `UNAVAILABLE` and
cannot produce PASS.

Run before deployment:

```bash
bin/glaw-policy check --json
bash test/legal_governor_advanced_test.sh
bin/glaw-doctor
```
