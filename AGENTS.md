# GLAW shared agent instructions

GLAW is agent-neutral: Claude Code and Codex must use the same source checkout, shared lane
manifest (`lib/client-lanes/premium-lanes.json`), CLI commands (`bin/`), and matter state
(`$GLAW_HOME`, normally `~/.glaw`). Do not create agent-specific lane definitions or matter
folders.

For every corp/fund build, route the matter through `founder-unicorn`, `tax-system`, and the
fund/enterprise lanes that the facts require. Add the `founder-governance` lane when the matter
mentions founder consent, reserved matters, protective/veto rights, board nomination or size
protections, Moelis, DGCL §122(18), or a Founder Rights Agreement. This lane is additive and
covers the control-stack, consent matrix, board/committee mechanics, anti-circumvention, sunset,
fiduciary/control-risk, and Delaware-counsel gates.
For a 5.01% economic-ownership control target, prove `pM / (pM + 100 - p) > 50.1%` with
`p = 5.01`, show the minimum multiplier and 20:1/25:1/50:1/100:1 sensitivity, and model
anti-dilution protections against crossing below 5.01%. Treat variable voting formulas as a
separate Delaware-counsel issue.
When the objective is founder control after outside investment, also attach
`founder-control-stack`. It is the intersecting lane for corp-build, PV/VC, PE, fund, tax,
accounting, enterprise, and UHNW work. It covers dual/multi-class stock, Class B super-voting,
separate class votes, supermajority thresholds, board designation, automatic conversion,
permitted transfers, founder succession, round-by-round control math, document allocation,
cap-table/accounting reconciliation, disclosure, and adversarial review.

Use the shared commands:

```bash
bin/glaw-intake premium founder-governance
bin/glaw-premium-lanes attach founder-governance
bin/glaw-premium-lanes validate --json
bin/glaw-doctor
```

After changing a lane, run `./setup` to deploy the same skills to both Claude and Codex roots.
GLAW produces attorney work-product for licensed review; it is not legal advice.
