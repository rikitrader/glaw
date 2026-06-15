"""Federal Trial Counsel Dashboard — FastAPI app.

All routes return JSON except GET / (serves the SPA) and GET /api/export
(streams a .docx). The SPA lives under static/; everything is served from
one process so there are no CORS or cross-origin concerns.
"""
from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Body, Query, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .bridges import ftc as ftc_bridge
from .bridges import pleading as pleading_bridge
from .bridges import courtlistener as cl_bridge

_STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Federal Trial Counsel Dashboard", version="1.0.0")


# ── Helpers ────────────────────────────────────────────────────────────────

def _case(body: dict) -> dict:
    case = body.get("case")
    if not isinstance(case, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid 'case' object")
    return case


def _wrap(fn, *args, **kwargs) -> JSONResponse:
    try:
        return JSONResponse(fn(*args, **kwargs))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


# ── Catalog / meta ─────────────────────────────────────────────────────────

@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "ftc_dashboard"}


@app.get("/api/claims")
def api_claims() -> JSONResponse:
    return _wrap(ftc_bridge.list_claims)


@app.get("/api/claims/{key}")
def api_claim_detail(key: str) -> JSONResponse:
    return _wrap(ftc_bridge.get_claim_detail, key)


@app.get("/api/districts")
def api_districts() -> JSONResponse:
    return _wrap(ftc_bridge.districts)


@app.get("/api/cases")
def api_cases() -> JSONResponse:
    return _wrap(ftc_bridge.cases)


@app.get("/api/sample-case")
def api_sample_case() -> JSONResponse:
    path = Path(__file__).resolve().parent.parent / "ftc_engine" / "sample_case.json"
    with open(path) as f:
        return JSONResponse(json.load(f))


# ── Analysis ───────────────────────────────────────────────────────────────

@app.post("/api/jurisdiction")
def api_jurisdiction(body: dict = Body(...)) -> JSONResponse:
    return _wrap(ftc_bridge.jurisdiction, _case(body))


@app.post("/api/suggest")
def api_suggest(body: dict = Body(...)) -> JSONResponse:
    return _wrap(ftc_bridge.suggest, _case(body))


@app.post("/api/risk")
def api_risk(body: dict = Body(...)) -> JSONResponse:
    claims = body.get("claims") or []
    if not isinstance(claims, list):
        raise HTTPException(400, "'claims' must be an array of claim keys")
    return _wrap(ftc_bridge.risk, _case(body), claims)


@app.post("/api/sol")
def api_sol(body: dict = Body(...)) -> JSONResponse:
    claims = body.get("claims") or []
    injury_date = body.get("injury_date")
    district = body.get("district")
    if not injury_date:
        raise HTTPException(400, "'injury_date' required (YYYY-MM-DD)")
    if not claims:
        raise HTTPException(400, "'claims' required")
    return _wrap(ftc_bridge.sol, claims, injury_date, district)


@app.post("/api/analyze")
def api_analyze(body: dict = Body(...)) -> JSONResponse:
    """Full pipeline in one shot — jurisdiction + suggest + risk(top 3) + SOL."""
    case = _case(body)
    try:
        jx = ftc_bridge.jurisdiction(case)
        suggestions = ftc_bridge.suggest(case)
        # Top 3 non-showstopper suggestions for risk/SOL
        shortlist = [
            s["claim_key"] for s in suggestions["suggestions"]
            if not s.get("showstoppers")
        ][:3]
        requested = case.get("claims_requested") or []
        if requested and requested != ["auto_suggest"]:
            shortlist = [c for c in requested if isinstance(c, str) and c != "auto_suggest"]
        risks = ftc_bridge.risk(case, shortlist) if shortlist else {"scores": []}
        injury_date = (case.get("limitations", {})
                           .get("key_dates", {})
                           .get("injury_date"))
        district_code = (case.get("court", {}) or {}).get("district_code")
        sol_results = (
            ftc_bridge.sol(shortlist, injury_date, district_code)
            if injury_date and shortlist else {"results": []}
        )
        return JSONResponse({
            "jurisdiction": jx,
            "suggestions": suggestions,
            "shortlist": shortlist,
            "risk": risks,
            "sol": sol_results,
        })
    except Exception as e:
        raise HTTPException(500, f"{type(e).__name__}: {e}")


# ── Drafting ───────────────────────────────────────────────────────────────

@app.post("/api/draft")
def api_draft(body: dict = Body(...)) -> JSONResponse:
    return _wrap(ftc_bridge.draft, _case(body))


@app.post("/api/pleading")
def api_pleading(body: dict = Body(...)) -> JSONResponse:
    """Full TypeScript federal_pleading_engine run."""
    return _wrap(
        pleading_bridge.generate,
        _case(body),
        body.get("claims") or None,
        bool(body.get("suggest")),
    )


@app.get("/api/pleading/claims")
def api_pleading_claims() -> JSONResponse:
    return _wrap(pleading_bridge.list_claims)


# ── Calendar / Monitor / Deposition / Exhibits / PACER ─────────────────────

@app.post("/api/calendar")
def api_calendar(body: dict = Body(...)) -> JSONResponse:
    return _wrap(
        ftc_bridge.calendar,
        _case(body),
        body.get("filing_date"),
        body.get("district"),
    )


@app.post("/api/monitor")
def api_monitor(body: dict = Body(...)) -> JSONResponse:
    return _wrap(
        ftc_bridge.monitor,
        _case(body),
        body.get("claims"),
        body.get("mode", "offline"),
    )


@app.post("/api/deposition")
def api_deposition(body: dict = Body(...)) -> JSONResponse:
    witness = body.get("witness")
    if not witness:
        raise HTTPException(400, "'witness' required")
    return _wrap(
        ftc_bridge.deposition,
        _case(body),
        witness,
        body.get("exam_type", "cross"),
        body.get("claims"),
        int(body.get("max_questions", 50)),
    )


@app.post("/api/exhibits")
def api_exhibits(body: dict = Body(...)) -> JSONResponse:
    return _wrap(
        ftc_bridge.exhibits,
        _case(body),
        body.get("scan_directory"),
        body.get("numbering", "alpha"),
        body.get("prefix", ""),
    )


@app.post("/api/pacer")
def api_pacer(body: dict = Body(...)) -> JSONResponse:
    return _wrap(ftc_bridge.pacer, _case(body))


# ── CourtListener research ─────────────────────────────────────────────────

@app.post("/api/courtlistener")
def api_courtlistener(body: dict = Body(...)) -> JSONResponse:
    query = body.get("query") or ""
    return _wrap(
        cl_bridge.search,
        query=query,
        court=body.get("court") or None,
        after=body.get("after"),
        before=body.get("before"),
        sort=body.get("sort"),
        limit=int(body.get("limit", 20)),
        search_type=body.get("type", "opinions"),
        next_url=body.get("next"),
    )


# ── Export to .docx ────────────────────────────────────────────────────────

@app.post("/api/export")
def api_export(body: dict = Body(...)) -> StreamingResponse:
    """Render the case to .docx via ftc_engine.exporter and stream the file."""
    try:
        from ftc_engine.exporter import export_draft
    except Exception as e:
        raise HTTPException(500, f"Exporter unavailable: {e}")

    case = _case(body)
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tf:
        out_path = tf.name
    try:
        export_draft(case, out_path)
        with open(out_path, "rb") as f:
            blob = f.read()
    finally:
        try:
            Path(out_path).unlink()
        except FileNotFoundError:
            pass
    return StreamingResponse(
        io.BytesIO(blob),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="complaint.docx"'},
    )


# ── File I/O for cases ─────────────────────────────────────────────────────

@app.post("/api/case/upload")
async def api_case_upload(file: UploadFile = File(...)) -> JSONResponse:
    try:
        raw = await file.read()
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON: {e}")
    if not isinstance(data, dict):
        raise HTTPException(400, "Case file root must be an object")
    return JSONResponse({"case": data})


# ── Static SPA ─────────────────────────────────────────────────────────────

if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    index_path = _STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(500, "Dashboard UI not installed (static/index.html missing)")
    return FileResponse(index_path)
