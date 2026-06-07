# IRS Forms Catalog & Download Patterns

All IRS forms are published as PDFs at stable URLs. **Download the current version live every
time** (`scripts/download_forms.py`) — never reuse a saved copy; the IRS revises forms yearly
and filing a superseded version causes rejections.

## URL patterns (verified)

| Need | Pattern | Example |
|---|---|---|
| **Current form** | `https://www.irs.gov/pub/irs-pdf/f{code}.pdf` | `f843.pdf`, `f9465.pdf`, `f656.pdf` |
| **Current instructions** | `https://www.irs.gov/pub/irs-pdf/i{code}.pdf` | `i9465.pdf`, `i1040gi.pdf` |
| **Prior-year return** | `https://www.irs.gov/pub/irs-prior/f1040--{YEAR}.pdf` | `f1040--2021.pdf`, `f1040--2022.pdf` |
| **Prior-year instructions** | `https://www.irs.gov/pub/irs-prior/i1040--{YEAR}.pdf` | `i1040--2021.pdf` |

`download_forms.py` token forms: `f843` (current), `i9465` (current instr), `1040:2021`
(prior-year return), `i1040:2021` (prior-year instr), and **`1040:2021-2025`** (a year **range** —
expands to one download per year).

## Personal + business, full year range (e.g. 2021 → today)

A non-filer is often behind on **both** a personal return and one or more **entity** returns. Pull
the whole range in one command (verified — 30 forms, TY2021–2025, zero failures):

```bash
python3 scripts/download_forms.py ./packet \
  1040:2021-2025  1040sc:2021-2025  1040se:2021-2025 \   # personal: 1040 + Sch C + Sch E
  1120s:2021-2025  f1120ssk:2021-2025 \                  # S-corp return + Sch K-1
  1065:2021-2025   f1065sk1:2021-2025 \                  # partnership return + Sch K-1
  1120:2021-2025                                          # C-corp return
```

| Track | Forms (token) |
|---|---|
| **Personal** | `1040`, Schedule 1/2/3 (`1040s1`/`1040s2`/`1040s3`), Schedule C `1040sc`, Schedule E `1040se` |
| **S-corp** | `1120s` + Schedule K-1 `f1120ssk` (one K-1 per shareholder) |
| **Partnership / multi-LLC** | `1065` + Schedule K-1 `f1065sk1` (one K-1 per partner) |
| **C-corp** | `1120` |

Sequence: **entity returns + K-1s before the owners' 1040s** (see `business-payroll-track.md`).

### ⚠ Field names vary by year — inspect every form

Verified across the 1040: **TY2021 wraps fields in groups** (`FilingStatus[0]`, `YourSocial[0]`,
`Address[0]`) while **TY2025 uses flat names** (`f1_01`, `f1_04`…). A fill map built for one year
will silently miss fields on another. **Always run `inspect_fields.py` on each downloaded form and
build a per-year map.** Never reuse a map across years or assume names are stable.

## Common forms by purpose

| Form | Purpose | Code | Auto-fillable? |
|---|---|---|---|
| **843** | Claim for Refund and Request for Abatement (penalties) | `f843` | ✅ simple |
| **9465** | Installment Agreement Request | `f9465` | ✅ simple |
| **656** + **433-A(OIC)** | Offer in Compromise + collection info (individual) | `f656`, `f433aoi` | ⚠ complex — review carefully |
| **433-B(OIC)** | OIC collection info (business) | `f433boi` | ⚠ complex |
| **433-F** | Collection Information Statement (IA / CNC) | `f433f` | ⚠ complex |
| **12153** | Request for a Collection Due Process hearing | `f12153` | ✅ simple |
| **911** | Request for Taxpayer Advocate assistance | `f911` | ✅ simple |
| **2848** | Power of Attorney (representation) | `f2848` | ✅ simple |
| **8821** | Tax Information Authorization | `f8821` | ✅ simple |
| **4506-T** | Request for Transcript | `f4506t` | ✅ simple |
| **8857** | Innocent Spouse relief | `f8857` | ⚠ narrative |
| **8379** | Injured Spouse allocation | `f8379` | ✅ simple |
| **14653 / 14654** | Streamlined certification (foreign / domestic) | `f14653`, `f14654` | ⚠ narrative |
| **656-L** | Offer in Compromise — doubt as to liability | `f656l` | ⚠ |
| **940 / 941 / 1040 / 1120 / 1120S / 1065** | Returns | `f940`,`f941`,`1040:YEAR`, etc. | ⚠ returns — prepare on the correct year's form |

> **Auto-fill scope:** the helper safely pre-populates the **simple, stable** forms (843, 9465,
> 12153, 911, 2848, 8821, 4506-T, 8379). **Returns and OIC financials** (1040, 433-x, 656) carry
> calculations and judgment — pre-populate identifying fields only and have a preparer/taxpayer
> complete and verify the substance. Never auto-fill a number you can't substantiate.

## Mailing addresses — do NOT hardcode

The correct address **varies by form, by the taxpayer's state, and by year**, and changes often.
Always pull it from:
- the **form's own instructions** (downloaded alongside the form), or
- the IRS **"Where to File"** pages (`https://www.irs.gov/filing/where-to-file-paper-tax-returns-with-or-without-a-payment`), or
- the **address printed on the CP notice** the taxpayer received (for notice responses).

Put the *source of truth* (not a guessed address) in the dossier manifest's `mail_to` field, and
recommend **certified mail, return receipt requested**, for every paper filing.
