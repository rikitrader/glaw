"""Tiny stdlib-only DOCX shim for GLAW zero-dependency mode.

It implements the small subset of python-docx used by GLAW: create/read a
document, add paragraphs/runs, set formatting attributes harmlessly, and save a
minimal valid .docx package. It is intentionally not a full Word API.
"""
from __future__ import annotations

import html
import zipfile
from pathlib import Path
from types import SimpleNamespace
from xml.etree import ElementTree as ET

__version__ = "0.0-glaw-stdlib"


class _Any(SimpleNamespace):
    def __getattr__(self, name):
        value = _Any()
        setattr(self, name, value)
        return value

    def get_or_add_rPr(self):
        return self

    def get_or_add_rFonts(self):
        return self

    def get_or_add_pPr(self):
        return self

    def get_or_add_tcPr(self):
        return self

    def set(self, *args, **kwargs):
        return None

    def append(self, *args, **kwargs):
        return None


class Run:
    def __init__(self, text=""):
        self.text = text
        self.font = _Any()
        self.bold = False
        self.italic = False
        self._element = _Any()


class Paragraph:
    def __init__(self, text=""):
        self.text = text
        self.runs = []
        self.alignment = None
        self.paragraph_format = _Any()
        self._p = _Any()
        if text:
            self.add_run(text)

    def add_run(self, text=""):
        run = Run(text)
        self.runs.append(run)
        self.text += text
        return run


class Cell:
    def __init__(self):
        self.paragraphs = [Paragraph()]
        self._tc = _Any()


class Row:
    def __init__(self, cols):
        self.cells = [Cell() for _ in range(cols)]


class Table:
    def __init__(self, rows, cols):
        self._cols = cols
        self.rows = [Row(cols) for _ in range(rows)]

    def add_row(self):
        row = Row(self._cols)
        self.rows.append(row)
        return row


class DocumentFile:
    def __init__(self, path=None):
        self.paragraphs = []
        self.styles = {"Normal": _Any(font=_Any(), paragraph_format=_Any())}
        self.sections = [_Any()]
        if path:
            self._read(path)

    def _read(self, path):
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        for p in root.findall(".//w:p", ns):
            parts = [t.text or "" for t in p.findall(".//w:t", ns)]
            self.paragraphs.append(Paragraph("".join(parts)))

    def add_paragraph(self, text="", style=None):
        p = Paragraph(text)
        self.paragraphs.append(p)
        return p

    def add_table(self, rows=1, cols=1):
        table = Table(rows, cols)
        self.paragraphs.append(Paragraph(""))
        return table

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        body = []
        for p in self.paragraphs:
            text = p.text or "".join(r.text for r in p.runs)
            body.append(
                "<w:p><w:r><w:t xml:space=\"preserve\">"
                + html.escape(text)
                + "</w:t></w:r></w:p>"
            )
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body>"
            + "".join(body)
            + "<w:sectPr/></w:body></w:document>"
        )
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", _CONTENT_TYPES)
            zf.writestr("_rels/.rels", _RELS)
            zf.writestr("word/document.xml", document)
            zf.writestr("word/_rels/document.xml.rels", _DOC_RELS)


def Document(path=None):
    return DocumentFile(path)


_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

_DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""
