"""Approved legal authority source domains for citation verification.

These domains are intentionally code-reviewed, not environment-configured. A
caller must not be able to turn an arbitrary host into an authoritative legal
corpus source at runtime.
"""
from __future__ import annotations

from urllib.parse import urlparse


AUTHORITY_SOURCE_CATALOG = (
    {
        "id": "us-code",
        "name": "Office of the Law Revision Counsel U.S. Code",
        "kind": "statute",
        "domains": ("uscode.house.gov",),
        "profiles": ("legal-research", "tax", "accounting-tax", "public-law"),
        "notes": "Federal statutory text; use for U.S.C. citations.",
    },
    {
        "id": "ecfr",
        "name": "Electronic Code of Federal Regulations",
        "kind": "regulation",
        "domains": ("ecfr.gov", "www.ecfr.gov"),
        "profiles": ("legal-research", "tax", "sec-reporting", "public-law"),
        "notes": "Current CFR text; use for Treasury, SEC, and agency rules.",
    },
    {
        "id": "govinfo",
        "name": "GovInfo",
        "kind": "official-publication",
        "domains": ("govinfo.gov", "www.govinfo.gov"),
        "profiles": ("legal-research", "public-law", "sec-reporting"),
        "notes": "Federal Register, CFR annual editions, statutes, reports, and official PDFs.",
    },
    {
        "id": "federal-register",
        "name": "Federal Register",
        "kind": "rulemaking",
        "domains": ("federalregister.gov", "www.federalregister.gov"),
        "profiles": ("legal-research", "public-law", "sec-reporting"),
        "notes": "Agency notices, proposed rules, final rules, and rulemaking history.",
    },
    {
        "id": "irs",
        "name": "Internal Revenue Service",
        "kind": "tax-authority",
        "domains": ("irs.gov", "www.irs.gov"),
        "profiles": ("tax", "accounting-tax"),
        "notes": "IRS forms, instructions, publications, revenue procedures, and guidance.",
    },
    {
        "id": "sec",
        "name": "U.S. Securities and Exchange Commission",
        "kind": "securities-authority",
        "domains": ("sec.gov", "www.sec.gov"),
        "profiles": ("sec-reporting", "accounting-tax", "legal-research"),
        "notes": "EDGAR, SEC rules, releases, forms, and staff materials.",
    },
    {
        "id": "pcaob",
        "name": "Public Company Accounting Oversight Board",
        "kind": "audit-authority",
        "domains": ("pcaobus.org", "www.pcaobus.org"),
        "profiles": ("sec-reporting", "accounting-tax"),
        "notes": "Auditing standards, inspection materials, and public-company audit guidance.",
    },
    {
        "id": "fasb",
        "name": "Financial Accounting Standards Board",
        "kind": "accounting-authority",
        "domains": ("fasb.org", "www.fasb.org", "asc.fasb.org"),
        "profiles": ("accounting", "accounting-tax", "sec-reporting"),
        "notes": "U.S. GAAP standards and codification materials where access permits.",
    },
    {
        "id": "congress",
        "name": "Congress.gov",
        "kind": "legislative-history",
        "domains": ("congress.gov", "www.congress.gov"),
        "profiles": ("legal-research", "public-law"),
        "notes": "Bills, public laws, legislative history, and congressional materials.",
    },
    {
        "id": "supreme-court",
        "name": "Supreme Court of the United States",
        "kind": "case-law",
        "domains": ("supremecourt.gov", "www.supremecourt.gov"),
        "profiles": ("legal-research", "public-law"),
        "notes": "Official Supreme Court opinions, orders, and docket materials.",
    },
    {
        "id": "courtlistener",
        "name": "CourtListener",
        "kind": "case-law",
        "domains": ("courtlistener.com", "www.courtlistener.com"),
        "profiles": ("legal-research", "public-law"),
        "notes": "Free opinion and docket access used as a public case-law adapter.",
    },
    {
        "id": "lii",
        "name": "Legal Information Institute",
        "kind": "secondary-access",
        "domains": ("law.cornell.edu", "www.law.cornell.edu"),
        "profiles": ("legal-research", "public-law"),
        "notes": "Public legal-text access; prefer official sources when available.",
    },
)

APPROVED_AUTHORITY_DOMAINS = frozenset(
    domain
    for source in AUTHORITY_SOURCE_CATALOG
    for domain in source["domains"]
)


def authority_domain(value: str) -> str:
    return (urlparse(str(value).strip()).hostname or "").lower()


def authority_source_for_url(value: str) -> dict:
    host = authority_domain(value)
    for source in AUTHORITY_SOURCE_CATALOG:
        for domain in source["domains"]:
            if host == domain or (
                host.endswith("." + domain) and not domain.startswith("www.")
            ):
                return dict(source)
    return {}


def approved_authority_url(value: str) -> bool:
    return bool(authority_source_for_url(value))


def authority_sources(profile: str = "") -> list[dict]:
    wanted = profile.strip().lower().replace("_", "-")
    rows = []
    for source in AUTHORITY_SOURCE_CATALOG:
        if wanted and wanted not in source["profiles"]:
            continue
        rows.append(dict(source))
    return rows
