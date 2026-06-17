"""Shared accounting-control manifest validation (zero-dependency, stdlib only).

Single source of truth for the accounting / tax / SEC-audit tie-out checks run
by BOTH the file gate (``bin/glaw-gate``) and the final-packet gate
(``bin/glaw-final-packet``). Both gates are binding, so their accounting
validation must never diverge — it lives here once.

The matter directory ``d``, the source-id regex, and the set of profiles that
require an accounting control are injected by the caller so each caller's own
authoritative definitions remain the single source for those values.
"""
import hashlib
import json
from decimal import Decimal, InvalidOperation


def _sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _boolish(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "pass", "passed", "ok"}


def _zeroish(value):
    try:
        return float(str(value).strip()) == 0.0
    except ValueError:
        return False


def _int_value(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def _decimal_present(data, field, label, missing):
    if field not in data:
        missing.append(f"{label}.artifact.{field} decimal")
        return
    try:
        Decimal(str(data.get(field)))
    except InvalidOperation:
        missing.append(f"{label}.artifact.{field} decimal")


def _artifact_hash(path_text, d, label, missing):
    if not str(path_text).strip():
        missing.append(f"{label}.artifact")
        return {"label": label, "path": str(path_text), "sha256": "", "size_bytes": 0}
    path = (d / str(path_text)).resolve()
    try:
        rel_path = str(path.relative_to(d.resolve()))
    except ValueError:
        missing.append(f"{label}.artifact inside matter")
        return {"label": label, "path": str(path_text), "sha256": "", "size_bytes": 0}
    if not path.is_file():
        missing.append(f"{label}.artifact exists")
        return {"label": label, "path": rel_path, "sha256": "", "size_bytes": 0}
    size = path.stat().st_size
    if size <= 0:
        missing.append(f"{label}.artifact nonempty")
    return {"label": label, "path": rel_path, "sha256": _sha256_file(path), "size_bytes": size}


def _read_accounting_artifact(path_text, d, label, missing):
    if not str(path_text).strip():
        return {}
    path = (d / str(path_text)).resolve()
    try:
        path.relative_to(d.resolve())
    except ValueError:
        return {}
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        missing.append(f"{label}.artifact valid JSON")
        return {}
    if not isinstance(data, dict):
        missing.append(f"{label}.artifact JSON object")
        return {}
    return data


def _require_empty_array(data, field, label, missing):
    if field not in data:
        missing.append(f"{label}.artifact.{field} array")
        return
    value = data.get(field)
    if not isinstance(value, list):
        missing.append(f"{label}.artifact.{field} array")
        return
    if value:
        missing.append(f"{label}.artifact.{field} empty")


def _require_artifact_boolish_true(data, field, label, missing):
    if field not in data:
        missing.append(f"{label}.artifact.{field}=true")
        return
    if not _boolish(data.get(field)):
        missing.append(f"{label}.artifact.{field}=true")


def accounting_control_manifest(d, profile, source_manifest, *, source_id_re, accounting_control_profiles):
    required = profile in accounting_control_profiles
    path = d / "accounting_control.json"
    source_ids = [item["id"] for item in source_manifest]
    manifest = {
        "required": required,
        "path": "accounting_control.json",
        "status": "pass",
        "missing": [],
        "sha256": "",
        "artifact_hashes": [],
    }
    if not required:
        manifest["status"] = "not_required"
        return manifest
    if not path.exists():
        manifest["status"] = "fail"
        manifest["missing"].append("accounting_control.json")
        return manifest
    manifest["sha256"] = _sha256_file(path)
    try:
        control = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        manifest["status"] = "fail"
        manifest["missing"].append("valid JSON")
        return manifest

    if control.get("status") != "pass":
        manifest["missing"].append("status=pass")
    source_text = str(control.get("source", ""))
    cited = [sid for sid in source_ids if sid in source_text]
    syntactic = sorted(set(source_id_re.findall(source_text)))
    if not source_id_re.search(source_text):
        manifest["missing"].append("source evidence id (SRC-####)")
    elif not cited:
        manifest["missing"].append("current source evidence id")
    elif sorted(set(syntactic) - set(source_ids)):
        manifest["missing"].append("non-current source evidence id")

    ledger = control.get("ledger", {})
    if ledger.get("status") != "pass":
        manifest["missing"].append("ledger.status=pass")
    manifest["artifact_hashes"].append(
        _artifact_hash(ledger.get("artifact", ""), d, "ledger", manifest["missing"])
    )

    books = control.get("books_doctor", {})
    if books.get("status") != "pass":
        manifest["missing"].append("books_doctor.status=pass")
    if not _boolish(books.get("require_rec")):
        manifest["missing"].append("books_doctor.require_rec=true")
    manifest["artifact_hashes"].append(
        _artifact_hash(books.get("artifact", ""), d, "books_doctor", manifest["missing"])
    )

    rec = control.get("bank_reconciliation", {})
    if rec.get("status") != "pass":
        manifest["missing"].append("bank_reconciliation.status=pass")
    if not _boolish(rec.get("reconciled")):
        manifest["missing"].append("bank_reconciliation.reconciled=true")
    if not _zeroish(rec.get("unreconciled_difference")):
        manifest["missing"].append("bank_reconciliation.unreconciled_difference=0")
    if _int_value(rec.get("book_only_count", 0)) != 0:
        manifest["missing"].append("bank_reconciliation.book_only_count=0")
    if _int_value(rec.get("bank_only_count", 0)) != 0:
        manifest["missing"].append("bank_reconciliation.bank_only_count=0")
    manifest["artifact_hashes"].append(
        _artifact_hash(rec.get("artifact", ""), d, "bank_reconciliation", manifest["missing"])
    )
    rec_artifact = _read_accounting_artifact(
        rec.get("artifact", ""), d, "bank_reconciliation", manifest["missing"]
    )
    if rec_artifact:
        if not _boolish(rec_artifact.get("reconciled")):
            manifest["missing"].append("bank_reconciliation.artifact.reconciled=true")
        if not _zeroish(rec_artifact.get("unreconciled_difference")):
            manifest["missing"].append("bank_reconciliation.artifact.unreconciled_difference=0")
        _require_empty_array(rec_artifact, "book_only", "bank_reconciliation", manifest["missing"])
        _require_empty_array(rec_artifact, "bank_only", "bank_reconciliation", manifest["missing"])

    if profile in {"accounting-tax", "tax"}:
        tax = control.get("tax_tieout", {})
        if tax.get("status") != "pass":
            manifest["missing"].append("tax_tieout.status=pass")
        if not _boolish(tax.get("provision_ties")):
            manifest["missing"].append("tax_tieout.provision_ties=true")
        if not _boolish(tax.get("internal_consistency")):
            manifest["missing"].append("tax_tieout.internal_consistency=true")
        manifest["artifact_hashes"].append(
            _artifact_hash(tax.get("artifact", ""), d, "tax_tieout", manifest["missing"])
        )
        tax_artifact = _read_accounting_artifact(
            tax.get("artifact", ""), d, "tax_tieout", manifest["missing"]
        )
        if tax_artifact:
            if tax_artifact.get("schema_version") != 1:
                manifest["missing"].append("tax_tieout.artifact.schema_version=1")
            if tax_artifact.get("source_tool") != "glaw-tax-tieout":
                manifest["missing"].append("tax_tieout.artifact.source_tool=glaw-tax-tieout")
            if tax_artifact.get("mode") != "recompute":
                manifest["missing"].append("tax_tieout.artifact.mode=recompute")
            _decimal_present(tax_artifact, "recomputed_total_provision", "tax_tieout", manifest["missing"])
            _decimal_present(tax_artifact, "posted_income_tax_expense", "tax_tieout", manifest["missing"])
            _require_artifact_boolish_true(
                tax_artifact, "provision_ties", "tax_tieout", manifest["missing"]
            )
            internal = tax_artifact.get("internal")
            if not isinstance(internal, dict):
                manifest["missing"].append("tax_tieout.artifact.internal object")
            else:
                if internal.get("source_tool") != "glaw-tax-tieout":
                    manifest["missing"].append("tax_tieout.artifact.internal.source_tool=glaw-tax-tieout")
                _decimal_present(internal, "income_tax_expense", "tax_tieout.internal", manifest["missing"])
                _decimal_present(internal, "expense_should_equal", "tax_tieout.internal", manifest["missing"])
                if not _boolish(internal.get("consistent", False)):
                    manifest["missing"].append("tax_tieout.artifact.internal.consistent=true")

    if profile == "sec-reporting":
        audit = control.get("audit_tieout", {})
        if audit.get("status") != "pass":
            manifest["missing"].append("audit_tieout.status=pass")
        if not _boolish(audit.get("financial_statements_tie")):
            manifest["missing"].append("audit_tieout.financial_statements_tie=true")
        if not _boolish(audit.get("icfr_reviewed")):
            manifest["missing"].append("audit_tieout.icfr_reviewed=true")
        if not _boolish(audit.get("pcaob_reviewed")):
            manifest["missing"].append("audit_tieout.pcaob_reviewed=true")
        if _int_value(audit.get("open_deficiencies_count", 0)) != 0:
            manifest["missing"].append("audit_tieout.open_deficiencies_count=0")
        if _int_value(audit.get("material_weaknesses_count", 0)) != 0:
            manifest["missing"].append("audit_tieout.material_weaknesses_count=0")
        if _int_value(audit.get("unresolved_audit_differences_count", 0)) != 0:
            manifest["missing"].append("audit_tieout.unresolved_audit_differences_count=0")
        manifest["artifact_hashes"].append(
            _artifact_hash(audit.get("artifact", ""), d, "audit_tieout", manifest["missing"])
        )
        audit_artifact = _read_accounting_artifact(
            audit.get("artifact", ""), d, "audit_tieout", manifest["missing"]
        )
        if audit_artifact:
            if not _boolish(audit_artifact.get("financial_statements_tie")):
                manifest["missing"].append("audit_tieout.artifact.financial_statements_tie=true")
            if not _boolish(audit_artifact.get("icfr_reviewed")):
                manifest["missing"].append("audit_tieout.artifact.icfr_reviewed=true")
            if not _boolish(audit_artifact.get("pcaob_reviewed")):
                manifest["missing"].append("audit_tieout.artifact.pcaob_reviewed=true")
            _require_empty_array(audit_artifact, "open_deficiencies", "audit_tieout", manifest["missing"])
            _require_empty_array(audit_artifact, "material_weaknesses", "audit_tieout", manifest["missing"])
            _require_empty_array(
                audit_artifact, "unresolved_audit_differences", "audit_tieout", manifest["missing"]
            )

    if manifest["missing"]:
        manifest["status"] = "fail"
    return manifest
