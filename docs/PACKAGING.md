# Packaging

GLAW is source-only and ships no Python, npm, or system package dependencies.
CI intentionally rejects `requirements.txt`, `pyproject.toml`, `package.json`,
and lockfiles.

The GitHub Package is therefore an OCI source artifact published to GHCR:

```bash
docker build -f packaging/Containerfile -t ghcr.io/rikitrader/glaw:1.2.0 .
docker tag ghcr.io/rikitrader/glaw:1.2.0 ghcr.io/rikitrader/glaw:latest
docker push ghcr.io/rikitrader/glaw:1.2.0
docker push ghcr.io/rikitrader/glaw:latest
```

The image is `FROM scratch` and contains the repository under `/glaw`; it is a
distribution artifact, not a runtime with installed third-party packages.

The same publish path is automated by `.github/workflows/package-ghcr.yml` on
release publication or manual `workflow_dispatch`.
