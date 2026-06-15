"""
Document-flavored MCP handlers — drafting, exporting, calendars, depositions.

Tools handled here:
  - ftc_draft          : generate complaint skeleton
  - ftc_export         : export to court-formatted .docx (draft / template / list)
  - ftc_template_list  : list court-ready templates
  - ftc_deposition     : generate deposition outline
  - ftc_exhibits       : generate exhibit index
  - ftc_pacer          : PACER/ECF filing package
  - ftc_calendar       : FRCP filing calendar
"""
from __future__ import annotations


def handle_ftc_draft(args: dict) -> dict:
    from ..drafter import generate_complaint
    complaint = generate_complaint(args["case_data"])
    return {"complaint": complaint, "length": len(complaint)}


def handle_ftc_deposition(args: dict) -> dict:
    from ..deposition import generate_deposition_outline, format_deposition_outline
    outline = generate_deposition_outline(
        args["case_data"],
        witness_name=args["witness_name"],
        exam_type=args.get("exam_type", "cross"),
        claim_keys=args.get("claim_keys"),
        max_questions=args.get("max_questions", 50),
    )
    return {"outline": format_deposition_outline(outline), "total_questions": outline.total_questions}


def handle_ftc_exhibits(args: dict) -> dict:
    from ..exhibits import generate_exhibit_index, format_exhibit_index
    index = generate_exhibit_index(
        args["case_data"],
        numbering=args.get("numbering", "alpha"),
        prefix=args.get("prefix", ""),
    )
    return {"index": format_exhibit_index(index), "total_exhibits": index.total_exhibits}


def handle_ftc_pacer(args: dict) -> dict:
    from ..pacer_meta import generate_filing_package, generate_js44, generate_all_summonses, generate_all_disclosures, format_filing_package, format_js44, format_summons
    component = args.get("component", "all")
    case_data = args["case_data"]

    if component == "js44":
        sheet = generate_js44(case_data)
        return {"js44": format_js44(sheet)}
    elif component == "summons":
        summonses = generate_all_summonses(case_data)
        return {"summonses": [format_summons(s) for s in summonses]}
    elif component == "disclosure":
        disclosures = generate_all_disclosures(case_data)
        return {"disclosures": [{"party": d.party_name, "parent": d.parent_corporation, "holder_10pct": d.publicly_held_10pct} for d in disclosures]}
    else:
        pkg = generate_filing_package(case_data)
        return {"package": format_filing_package(pkg)}


def handle_ftc_calendar(args: dict) -> dict:
    from ..filing_calendar import generate_filing_calendar, format_filing_calendar
    calendar = generate_filing_calendar(
        args["case_data"],
        filing_date_str=args.get("filing_date"),
        district_code=args.get("district_code"),
    )
    return {"calendar": format_filing_calendar(calendar, fmt="detailed"), "total_documents": calendar.total_documents, "critical_deadlines": calendar.critical_deadlines}


def handle_ftc_export(args: dict) -> dict:
    from ..exporter import export_draft, export_template, list_templates
    mode = args.get("mode", "draft")

    if mode == "list_templates":
        templates = list_templates()
        return {"templates": templates, "total": len(templates)}
    elif mode == "template":
        case_data = args.get("case_data", {})
        output = args.get("output_path", "output.docx")
        result = export_template(args["template_name"], case_data, output)
        return {"output_path": result.output_path, "sections": result.sections}
    else:
        case_data = args.get("case_data", {})
        output = args.get("output_path", "output.docx")
        result = export_draft(case_data, output)
        return {"output_path": result.output_path, "sections": result.sections}


def handle_ftc_template_list(args: dict) -> dict:
    from ..exporter import list_templates
    templates = list_templates()
    return {"templates": templates, "total": len(templates)}
