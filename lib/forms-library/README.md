# GLAW FORMS LIBRARY — MASTER INDEX

Reusable corporate / securities / fund form bank. Each master is recreated from an SEC filing or the user's own
vetted templates, genericized to `[BRACKETS]`, rendered in the enforced **us-corporate-legal-instrument house style**
(Times New Roman 10pt, ×1.15 leading, justified, ARTICLE I / Section 1. / (a) / (i) outline, run-in bold heads), with a
ROOF10X/RoofAI-filled version where applicable. **~114 masters (Delaware + Florida + Texas) · 2 reference exemplars · 16 filled versions · 50 sources · 1 knowledge wiki.**
ATTORNEY WORK-PRODUCT; a licensed attorney must adapt and sign. Not legal advice.

## How to use
`/glaw-forms` routes a request → right master → fills from the Carta cap table (`fill_from_captable.py`) → renders
house style (`publish_legal.py`) → gates issuance (`/glaw-consensus`, `/glaw-valuation-409a`). Sources in `manifest.json`.

## 1. Formation & Governance
| Form | File | Source |
|---|---|---|
| Amended & Restated Certificate of Incorporation | `glaw-amended-restated-coi-master.md` | Google (1288776) |
| Certificate of Designations (Convertible Preferred) | `glaw-certificate-of-designations-master.md` | Root (1788882) |
| Delaware Formation Certificates (LLC/LP/Corp) | `glaw-delaware-certificate-master.md` | Dropbox + DGCL/DE Acts |
| LLC Operating Agreement (Delaware) | `glaw-llc-operating-agreement-master.md` | your [DESIGNATED MEMBER] template |
| Shareholders Agreement | `glaw-shareholders-agreement-master.md` | your [DESIGNATED MEMBER] template |

## 2. Founder / Employee Day-1
| Restricted Stock Purchase Agreement (+ §83(b)) | `glaw-restricted-stock-purchase-agreement-master.md` | Intelligent Buying (1358633) |
| Confidential Info & Invention Assignment (CIIAA) | `glaw-ciiaa-master.md` | 1513847 |

## 3. Equity Compensation
| Equity Incentive Plan (omnibus) | `glaw-equity-incentive-plan-master.md` | Meta 2025 (1326801) |
| Stock Option Grant Notice & Agreement | `glaw-stock-option-agreement-master.md` | Reddit 2024 (1713445) |
| RSU Award Agreement (double-trigger) | `glaw-rsu-award-agreement-master.md` | Heritage (1788230) |

## 4. Financing — pre-priced
| SAFE (YC post-money) | `glaw-safe-master.md` | YC |
| Convertible Promissory Note | `glaw-convertible-note-master.md` | market |

## 5. Warrants (5 distinct)
| Warrant Agreement (w/ Warrant Agent) | `glaw-warrant-agreement-master.md` | 1803901 |
| Common Stock Purchase Warrant | `glaw-common-stock-warrant-master.md` | 1340652 |
| Warrant to Purchase Stock (standalone) | `glaw-warrant-standalone-master.md` | 1139023 |
| Warrant Exchange Agreement | `glaw-warrant-exchange-agreement-master.md` | 1591956 |
| Warrant Certificate | `glaw-warrant-certificate-master.md` | 1840706 |

## 6. Priced Round (Series A set)
| Investor Rights Agreement | `glaw-investor-rights-agreement-master.md` | iGATE (1024732) |
| ROFR & Co-Sale Agreement | `glaw-rofr-cosale-agreement-master.md` | Nativ Mobile (1748441) |
| Voting Agreement | `glaw-voting-agreement-master.md` | Proto Labs (1443669) |
| Series A Closing Binder & Signing Checklist | `glaw-series-a-closing-binder-master.md` | assembled |
| *(+ Certificate of Designations — §1)* | | |

## 7. M&A / Roll-up
| Share Purchase Agreement (12 Articles) | `glaw-share-purchase-agreement-master.md` | Leggett & Platt (58492) |

## 8. Debt / Security / Escrow
| Pledge & Security Agreement (Mezzanine) | `glaw-pledge-security-agreement-master.md` | RCG Longview (your template) |
| Ownership-Interest Escrow Agreement | `glaw-escrow-agreement-master.md` | your template |
| Release & Indemnity Agreement | `glaw-release-indemnity-agreement-master.md` | your template |

## 9. Fund / Tier-3 (onshore + offshore)
| Limited Partnership Agreement | `glaw-limited-partnership-agreement-master.md` | Blackstone (1930054) |
| Subscription Agreement | `glaw-subscription-agreement-master.md` | Vesper (1818093) |
| Partnership Subscription + Investor Questionnaire | `glaw-partnership-subscription-questionnaire-master.md` | CFI CSFR (1467076) |
| Private Placement Memorandum (onshore PE) | `glaw-ppm-master.md` | 3 SEC PPMs |
| Offshore Fund PPM (master-feeder) | `glaw-offshore-fund-ppm-master.md` | VanEck offshore |
| Selected Dealer Agreement | `glaw-selected-dealer-agreement-master.md` | Blackstone (1930054) |

## 10. Knowledge Wiki
| §12(g) Exchange Act registration & option/RSU exemptions | `knowledge/12g-rsu-option-exchange-act-registration.md` |

## Standing rules
House style enforced (`glaw-document-style.css`); full clauses, never summarized; 100% bracketed master + a filled
corp version. §409A: option/warrant strikes ≥ FMV, escrow until signed 409A. Securities: Reg D/§4(a)(2) + accredited/QP.
UPL footer on every deliverable.

## Gaps to add next
Series A Preferred Stock Purchase Agreement (financing) · Bylaws · Offer Letter / Advisor (FAST) · Executive
Employment + Separation · Commercial (MSA/SaaS, NDA, DPA) · GP/Mgmt-Co operating agreements · Side Letter · IP License.

## Jurisdiction Matrix (auto-generated)

Every form family and the jurisdictions available. ✅ = native/real-statute or governing-law variant present.

| Form | DE | FL | TX |
|---|:--:|:--:|:--:|
| amended restated coi | ✅ | — | — |
| articles of incorporation | — | ✅ | — |
| bylaws | ✅ | ✅ | ✅ |
| certificate of designations | ✅ | ✅ | ✅ |
| certificate of formation | — | — | ✅ |
| ciiaa | ✅ | ✅ | ✅ |
| common stock warrant | ✅ | ✅ | ✅ |
| convertible note | ✅ | ✅ | ✅ |
| delaware certificate | ✅ | — | — |
| do indemnity agreement | — | — | — |
| equity incentive plan | ✅ | ✅ | ✅ |
| escrow agreement | ✅ | ✅ | ✅ |
| indemnification agreement | ✅ | ✅ | ✅ |
| investment advisory agreement | ✅ | ✅ | ✅ |
| investor rights agreement | ✅ | ✅ | ✅ |
| joint written consent board and shareholders | — | ✅ | ✅ |
| joint written consent board and stockholders | ✅ | — | — |
| limited partnership agreement | ✅ | ✅ | ✅ |
| llc operating agreement | ✅ | ✅ | ✅ |
| offshore fund ppm | ✅ | — | — |
| partnership subscription questionnaire | ✅ | ✅ | ✅ |
| pledge security agreement | ✅ | ✅ | ✅ |
| ppm | ✅ | ✅ | ✅ |
| ppm llc operating company | ✅ | ✅ | ✅ |
| ppm real estate | ✅ | ✅ | ✅ |
| release indemnity agreement | ✅ | ✅ | ✅ |
| restricted stock purchase agreement | ✅ | ✅ | ✅ |
| rofr cosale agreement | ✅ | ✅ | ✅ |
| rsu award agreement | ✅ | ✅ | ✅ |
| safe | ✅ | ✅ | ✅ |
| selected dealer agreement | ✅ | ✅ | ✅ |
| series a closing binder | ✅ | ✅ | ✅ |
| share purchase agreement | ✅ | ✅ | ✅ |
| shareholder action by written consent | — | ✅ | ✅ |
| shareholder written consent in lieu | ✅ | ✅ | ✅ |
| shareholders agreement | ✅ | ✅ | ✅ |
| stock option agreement | ✅ | ✅ | ✅ |
| stockholder action by written consent | ✅ | — | — |
| subscription agreement | ✅ | ✅ | ✅ |
| subscription agreement pe fund | ✅ | ✅ | ✅ |
| voting agreement | ✅ | ✅ | ✅ |
| warrant agreement | ✅ | ✅ | ✅ |
| warrant certificate | ✅ | ✅ | ✅ |
| warrant exchange agreement | ✅ | ✅ | ✅ |
| warrant standalone | ✅ | ✅ | ✅ |

**Reference exemplars (not templates):** form-10q-exemplar, retail-fund-prospectus-drafting-guide

> **Naming equivalences (not gaps):** the charter doc is *Amended & Restated Certificate of Incorporation* (DE) = *Articles of Incorporation* (FL) = *Certificate of Formation* (TX); *stockholder* (DE) = *shareholder* (FL/TX) in the written-consent forms. *Delaware certificate* and *offshore fund PPM* are intentionally DE-only.
