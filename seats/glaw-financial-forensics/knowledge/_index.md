# Knowledge Base Catalog

18 source documents, extracted **verbatim** from the original PDFs via `opendataloader-pdf`
(Apache-2.0, faithful text+table parser). These are the skill's ground truth. **Search them
before asserting any rule** — `bash ../scripts/search_kb.sh "<query>"`.

> Integrity: text is mechanically extracted, not paraphrased. Cite as
> `(KB: <file>.md — "<quote>")`. If a needed fact isn't in the KB, say so and label any
> outside assertion as general knowledge, not sourced.

## IRS / Tax authority
| File | What it covers — search it for… |
|------|----------------------------------|
| `irs-construction-industry-audit-technique-guide.md` | **THE IRS ATG** — how revenue agents actually audit contractors: participants, contracting process, contract income, contract types, bonding, permits, examination techniques. Primary source for the Adversarial IRS Agent. |
| `irs-pub5522-small-biz-self-employed.md` | IRS Small Business/Self-Employed construction audit guide companion. |
| `irs-fs-2007-22-construction-tax-gap.md` | IRS fact sheet on under-reported construction income, cash vs accrual, deductible expenses, the "tax gap." |
| `irs-rev-proc-16-29-accounting-method-changes.md` | Rev. Proc. 2016-29 — automatic accounting-method changes by IRC §: bad debts (§166), interest (§163), depreciation (§167/168/179), R&E (§174), §460 long-term contracts. Use for method-change analysis. |
| `irs-land-developers-subcontractors.md` | LB&I concept unit: land developers & subcontractors — cost allocation, §263A capitalization. |
| `tax-accounting-methods-construction-contractors.md` | Cash vs accrual vs hybrid; **Completed Contract Method (CCM)** vs **Percentage-of-Completion (PCM/cost-to-cost) under IRC §460**; which method complies with GAAP. |

## Construction / contractor accounting (the engine)
| File | What it covers |
|------|----------------|
| `peterson-construction-accounting-fin-mgmt.md` | **Peterson, *Construction Accounting & Financial Management* (Pearson, 2nd ed.)** — the deepest text here (~199K words). Full ledger, job costing, financial statements, ratios, cash flow, equipment, EVA, profit. Primary methodology source. |
| `fin-mgmt-accounting-fundamentals-construction.md` | Financial Management & Accounting Fundamentals for Construction — understanding/analyzing financial statements, accounting basics, project cost control, forecasting, TVM, investment evaluation. |
| `cicpac-contractor-financial-statements-whitepaper.md` | CICPAC whitepaper: **construction financial statements, schedules, and disclosures** — WIP schedule, over/under-billings, required disclosures. |
| `asc606-revenue-recognition-construction.md` | **ASC 606** revenue recognition for contractors — the 5-step model, contract costs, balance-sheet presentation, disclosures, transition. |
| `impact-accounting-methodology-building-construction.md` | Impact-accounting methodology for building construction. |
| `construction-accounting-capitalization-policy.md` | Sample capitalization policy — what to capitalize vs expense; materiality thresholds. |
| `builders-guide-continuous-improvement.md` | Home Builder's Guide to Continuous Improvement — cycle-time, problem-solving, root-cause, corrective action (operational/forensic root-cause framing). |

## Sample / reference financial statements (format models)
| File | What it covers |
|------|----------------|
| `sample-contractor-financial-statement-stambaugh-ness.md` | **Model contractor financial statement** (Stambaugh Ness, PC) — exact CPA-format layout to emulate for deliverables. |
| `nrca-2021-22-audited-financial-statements.md` | NRCA audited financial statements — real audited-report structure & notes. |
| `sample-commercial-roofing-business-for-sale-cim.md` | Real commercial-roofing CIM: gross sales, cash flow, WIP, backlog, A/R, asset schedule — a worked example of roofing financials & valuation. |

## Industry / valuation context
| File | What it covers |
|------|----------------|
| `roofing-contracting-industry-q2-2024.md` | KPMG roofing M&A market update — multiples, transaction context for valuation. |
| `ong-nonprofit-accounting-guide.md` | Nonprofit/board accounting guide — board responsibilities, tax-exempt status, donor restrictions, budgeting, **internal accounting controls** (control framework transfers to fraud review). |

---

### Quick routing
- **"Is this method allowed / which method?"** → tax-accounting-methods, irs-rev-proc-16-29, asc606.
- **"How would an IRS agent attack this?"** → irs-construction-industry-audit-technique-guide, irs-fs-2007-22.
- **"How do I build the statements / WIP / over-under billing?"** → peterson, cicpac, fin-mgmt-fundamentals, sample-contractor-financial-statement.
- **"What's the right format?"** → sample-contractor-financial-statement, nrca-audited.
- **"Internal controls / fraud framework?"** → ong-nonprofit-accounting-guide, builders-guide.
