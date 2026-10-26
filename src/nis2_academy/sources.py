"""Offline source verification and minimal XLSX parsing (no HQ imports)."""

import hashlib
import json
import posixpath
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

RESOURCES = Path(__file__).parent / "resources"
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def read(name, root=RESOURCES):
    return json.loads((root / name).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_hash(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def workbook(path, sheet):
    def tag(t):
        return f"{{{NS}}}{t}"

    with ZipFile(path) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = [
                "".join(t.text or "" for t in si.iter(tag("t")))
                for si in ET.fromstring(z.read("xl/sharedStrings.xml"))
            ]
        sheets = ET.fromstring(z.read("xl/workbook.xml"))
        rels = {
            r.attrib["Id"]: r.attrib["Target"]
            for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        }
        selected = next(s for s in sheets.iter(tag("sheet")) if s.attrib["name"] == sheet)
        target = rels[
            selected.attrib[
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            ]
        ]
        path_in_zip = (
            target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
        )
        result = []
        for row in ET.fromstring(z.read(path_in_zip)).iter(tag("row")):
            number = int(row.attrib["r"])
            if number <= 2:
                continue
            cells = {}
            for cell in row:
                key = re.sub(r"\d", "", cell.attrib["r"])
                if cell.attrib.get("t") == "inlineStr":
                    value = "".join(t.text or "" for t in cell.iter(tag("t")))
                else:
                    v = cell.find(tag("v"))
                    value = v.text if v is not None else ""
                    if cell.attrib.get("t") == "s":
                        value = strings[int(value)]
                cells[key] = value
            if not cells.get("C"):
                continue
            code, point = cells["C"].strip(), int(cells["E"])
            result.append(
                {
                    "id": f"{code}_P{point}",
                    "text": cells["F"],
                    "measure_code": code,
                    "point_number": point,
                    "measure_description": cells["D"],
                    "function": cells["A"],
                    "category": cells["B"],
                    "policy_areas": cells.get("G", ""),
                    "sheet": sheet,
                    "row": number,
                }
            )
        return result


def verify_integrity(root=RESOURCES):
    manifest = read("integrity.json", root)
    for name, expected in manifest.items():
        if sha(root / name) != expected:
            raise ValueError(f"Source integrity mismatch: {name}")
    return manifest


def verify_pdf(root=RESOURCES):
    import pymupdf

    pack = read("enisa-passages.json", root)
    if sha(root / "enisa.pdf") != pack["source_pdf_sha256"]:
        raise ValueError("ENISA PDF identity differs")

    def normalize(s):
        return " ".join(s.split())

    with pymupdf.open(root / "enisa.pdf") as pdf:
        for p in pack["passages"]:
            if not (1 <= p["page"] <= len(pdf)):
                raise ValueError(f"Invalid PDF page: {p['passage_id']}")
            if normalize(p["excerpt"]) not in normalize(pdf[p["page"] - 1].get_text()):
                raise ValueError(f"Excerpt absent on page: {p['passage_id']}")
    return {
        "verified_passages": len(pack["passages"]),
        "method": "Normalized contiguous substring on 1-based physical PDF page",
        "semantic_review": "Still required: textual identity does not establish pertinence or compliance",
    }
