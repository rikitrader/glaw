"""Document generation commands: export, exhibits, deposition, pacer, calendar."""
from __future__ import annotations

import sys
from pathlib import Path

from ._shared import _load_case


def cmd_export(args):
    """Export to court-formatted .docx (Word/Google Docs/PDF-ready)."""
    from ..exporter import export_draft, export_template, export_text, list_templates

    if args.list_templates:
        templates = list_templates()
        print(f"{'Category':<15} {'Template Name':<40} {'Path'}")
        print("-" * 80)
        for t in templates:
            print(f"{t['category']:<15} {t['name']:<40} {t['path']}")
        return

    output = args.output or "output.docx"

    if args.draft:
        case_data = _load_case(args.input)
        result = export_draft(case_data, output)
        print(f"Complaint draft exported to: {result.output_path}")
        print(f"  Format: .docx (Times New Roman 12pt, double-spaced, 1\" margins)")
        print(f"  Sections: {result.sections}")
        print(f"  Open in: Microsoft Word, Google Docs, or LibreOffice")
        print(f"  To PDF: File > Export/Print as PDF from any of the above")
    elif args.template:
        case_data = _load_case(args.input) if args.input else {}
        result = export_template(args.template, case_data, output)
        print(f"Template exported to: {result.output_path}")
        print(f"  Template: {args.template}")
        print(f"  Format: .docx (Times New Roman 12pt, double-spaced, 1\" margins)")
        print(f"  Sections: {result.sections}")
    elif args.text:
        from pathlib import Path as P
        text = P(args.text).read_text()
        result = export_text(text, output)
        print(f"Text exported to: {result.output_path}")
        print(f"  Format: .docx (court-formatted)")
    else:
        print("Error: specify --draft, --template, --text, or --list-templates", file=sys.stderr)
        sys.exit(1)

    if getattr(args, "questions", False) and hasattr(args, "input") and args.input:
        from ..questions import generate_questions, format_questions
        case_data = _load_case(args.input)
        qs = generate_questions(case_data, doc_type="export")
        print(format_questions(qs, verbose=getattr(args, "verbose", False)))


def cmd_deposition(args):
    """Generate deposition question outlines."""
    from ..deposition import generate_deposition_outline, format_deposition_outline
    case_data = _load_case(args.input)

    claim_keys = args.claims.split(",") if args.claims else None
    outline = generate_deposition_outline(
        case_data,
        witness_name=args.witness,
        exam_type=args.type,
        claim_keys=claim_keys,
        max_questions=args.max or 50,
    )

    output_text = format_deposition_outline(outline, verbose=args.verbose)

    if args.output:
        Path(args.output).write_text(output_text)
        print(f"Deposition outline written to {args.output}")
    else:
        print(output_text)


def cmd_exhibits(args):
    """Generate exhibit index."""
    from ..exhibits import generate_exhibit_index, format_exhibit_index
    case_data = _load_case(args.input)

    index = generate_exhibit_index(
        case_data,
        scan_directory=args.scan,
        numbering=args.numbering,
        prefix=args.prefix or "",
    )

    output_text = format_exhibit_index(index, fmt=args.format)

    if args.output:
        Path(args.output).write_text(output_text)
        print(f"Exhibit index written to {args.output}")
    else:
        print(output_text)


def cmd_pacer(args):
    """Generate PACER/ECF filing package."""
    from ..pacer_meta import (
        generate_filing_package, generate_js44, generate_all_summonses,
        generate_all_disclosures, format_js44, format_summons, format_filing_package,
    )
    case_data = _load_case(args.input)

    if args.all:
        pkg = generate_filing_package(case_data)
        print(format_filing_package(pkg))
    elif args.js44:
        sheet = generate_js44(case_data)
        print(format_js44(sheet))
    elif args.summons:
        summonses = generate_all_summonses(case_data)
        for s in summonses:
            print(format_summons(s))
            print()
    elif args.disclosure:
        disclosures = generate_all_disclosures(case_data)
        if not disclosures:
            print("No corporate parties requiring FRCP 7.1 disclosure.")
        for d in disclosures:
            print(f"{d.party_name} ({d.party_type})")
            print(f"  Parent: {d.parent_corporation}")
            print(f"  10%+ Holder: {d.publicly_held_10pct}")
            print()
    else:
        pkg = generate_filing_package(case_data)
        print(format_filing_package(pkg))


def cmd_calendar(args):
    """Generate case filing calendar."""
    from ..filing_calendar import generate_filing_calendar, format_filing_calendar
    case_data = _load_case(args.input)

    calendar = generate_filing_calendar(
        case_data,
        filing_date_str=args.filing_date,
        district_code=args.district,
    )

    output_text = format_filing_calendar(calendar, fmt=args.format)

    if args.output:
        Path(args.output).write_text(output_text)
        print(f"Filing calendar written to {args.output}")
    else:
        print(output_text)
