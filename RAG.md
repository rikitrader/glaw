# Source-Locked RAG

`lib/legal_governor/provenance.py` records authority metadata, raw text hashes,
retrieval timestamps, provider, version, and jurisdiction in an append-only
source universe. `retrieval.py` provides deterministic lexical and citation-graph
retrieval. Semantic retrieval is an explicit provider boundary: if embeddings
are not configured, status is `UNAVAILABLE`, and completeness cannot become
`COMPLETE`.

No normalized text, chunk, embedding, or generated answer overwrites raw source
text. Every material source must remain traceable to its source ID and hash.
