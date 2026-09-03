# Hanke book corpus

This directory is the logical book corpus for HAEIS. It records authoritative
metadata, lawful full-text availability, source provenance, and the analytical
role of each work. A metadata record is not treated as book-text evidence.

`METADATA_VERIFIED` means an authoritative author or Johns Hopkins record
confirms the bibliographic entry. `FULL_TEXT_VERIFIED` requires a locally
acquired artifact, integrity hash, and citation-anchor review. Copyrighted
commercial books remain metadata-indexed unless lawful full text is available.

The source-of-truth records are in `index.json`. Public PDFs are acquired through
the HAEIS source boundary and remain `FOUND` until independently verified.
