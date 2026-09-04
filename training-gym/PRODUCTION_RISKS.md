# Production Risks

| Severity | Risk | Mitigation | Status |
|---|---|---|---|
| Critical | Durable queue/database adapters not connected | Implement repository-specific adapters and crash-recovery tests | Open |
| Critical | Browser sandbox not yet deployed | Isolate browser workers, deny host/network access, reset per episode | Open |
| High | Real provider adapters and secret management absent | Add provider adapters behind `ModelProvider` and external secrets | Open |
| High | Cross-application shared state absent in `CompositeGym` | Add a shared world-state service and equivalence tests | Open |
| High | 100k-scale behavior unmeasured | Run staged load/chaos tests and publish measured results | Open |
| Medium | Dashboard and operational health UI absent | Add authenticated researcher console | Open |
