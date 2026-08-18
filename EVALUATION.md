# Evaluation and the 3% target

The target is empirical: material error among PASS outputs must have a 95%
Wilson confidence interval whose upper bound is below 3%. It is not a claim that
the model is 97% legally accurate.

```bash
bin/glaw-legal-governor evaluate --input benchmark-results.json
```

Each row must preserve the question, domain, machine decision, and adjudicated
`material_error` label. The evaluator reports PASS precision, abstention rate,
observed material-error rate, and the 95% interval. No benchmark data or gold
labels are fabricated by the system.

The repository does not currently contain a 10,000-question attorney-adjudicated
gold set. Therefore production acceptance remains `REVIEW_REQUIRED` until a
double-blind, domain-stratified benchmark supplies the required evidence.
