"""Approved legal authority source domains for citation verification.

These domains are intentionally code-reviewed, not environment-configured. A
caller must not be able to turn an arbitrary host into an authoritative legal
corpus source at runtime.
"""
from __future__ import annotations

from urllib.parse import urlparse


APPROVED_AUTHORITY_DOMAINS = frozenset({
    "uscode.house.gov",
    "ecfr.gov",
    "www.ecfr.gov",
    "federalregister.gov",
    "www.federalregister.gov",
    "govinfo.gov",
    "www.govinfo.gov",
    "irs.gov",
    "www.irs.gov",
    "sec.gov",
    "www.sec.gov",
    "congress.gov",
    "www.congress.gov",
    "supremecourt.gov",
    "www.supremecourt.gov",
    "courtlistener.com",
    "www.courtlistener.com",
    "law.cornell.edu",
    "www.law.cornell.edu",
})


def authority_domain(value: str) -> str:
    return (urlparse(str(value).strip()).hostname or "").lower()


def approved_authority_url(value: str) -> bool:
    host = authority_domain(value)
    return host in APPROVED_AUTHORITY_DOMAINS or any(
        host.endswith("." + domain)
        for domain in APPROVED_AUTHORITY_DOMAINS
        if not domain.startswith("www.")
    )
