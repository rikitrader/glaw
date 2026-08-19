# Incident response

1. Freeze and hash the original request, sources, outputs, and Governor record.
2. Classify the failure (`E1` source through `E12` infrastructure).
3. Identify the affected matter/output set from audit IDs and source hashes.
4. Mark affected conclusions `REVALIDATION_REQUIRED`.
5. Add the failure to the benchmark and adversarial regression suite.
6. Fix the failure class, not only the individual answer.
7. Rerun tests and evaluation; block deployment if the 95% upper bound fails.
8. Record human counsel disposition without mutating the machine record.
