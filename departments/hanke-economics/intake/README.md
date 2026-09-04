# HAEIS intake

Start every engagement by copying `template.json` into a dated intake file. Do not begin policy analysis from a narrative prompt alone.

## Intake sequence

1. Define the exact economic question and decision horizon.
2. Select the country and episode from `country-cases/index.json`, or create a new case marked `SOURCE_REQUIRED`.
3. State the user hypothesis without treating it as fact.
4. Select the required output mode and policy alternatives.
5. List the data requested and classify each item as `KNOWN`, `ESTIMATED`, `DISPUTED`, or `UNAVAILABLE`.
6. Attach source records or document IDs. A URL by itself is not verification.
7. Run the intake validator.
8. Only then start the HAEIS workflow: corpus search → source audit → data forensics → specialist analysis → postures → RED → BLUE → RED II → audits → Chief arbitration.

## Venezuela first test

Use `venezuela-dollarization.json`. It intentionally contains no invented values. Replace each `null` only with a sourced observation and preserve the source ID, unit, date, release date, revision, and confidence.

An intake can be accepted for research with missing data, but a final recommendation is blocked while critical data, citations, mathematics, or adversarial review remain unresolved.
