#!/usr/bin/env python3
"""build-pools.py -- the NCVEC amateur radio question pools as HEE Pills and Cards.

Every question and answer in the three current pools (Technician, General,
Amateur Extra), one Pill per question, in directories that follow the pool's
own structure: ham/pools/<pool>/<subelement>/<group>/<id>.pill.v1.yaml, with
a Card for each group, each subelement and each pool.

NCVEC's Question Pool Committee releases each pool into the public domain;
the statement is quoted in ham/pools/sources.yaml, beside the URL, size and
sha256 of every file used.

USAGE
  ham/bin/build-pools.py --record-sources   hash the downloaded files and write sources.yaml
  ham/bin/build-pools.py                    build the tree from the downloaded files
  ham/bin/build-pools.py --check            build into a temp dir and compare with the committed tree

  The files are read from ${XDG_CACHE_HOME:-$HOME/.cache}/ham-pools/files/
  (--cache overrides), never from the repo. A file whose sha256 does not
  match sources.yaml is refused.

VALIDATION (both modes)
  every question has choices A-D and a key among them; ids are unique and
  sit under their own group and subelement; every group the syllabus names
  exists with its questions, and each subelement has the group count its
  header states; each subelement's question count matches the syllabus
  (a count that includes withdrawn questions is noted, a known defect in
  NCVEC's document is a WARNING, anything else CRITICAL); exam questions sum
  to the 47 CFR 97.503 exam size; every figure a question names exists; the
  docx's question ids and keys match pdftotext of the pool PDF.

EXIT STATUS
  0 OK   1 WARNING   2 CRITICAL (validation failure or drift)   3 UNKNOWN (sources missing)
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REL_OUT = "ham/pools"
CACHE = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "ham-pools" / "files"

OK, WARNING, CRITICAL, UNKNOWN = 0, 1, 2, 3
LABEL = {OK: "OK", WARNING: "WARNING", CRITICAL: "CRITICAL", UNKNOWN: "UNKNOWN"}
ICON = {OK: "✅", WARNING: "⚠️", CRITICAL: "❌", UNKNOWN: "❓"}

# 47 CFR 97.503: exam size and minimum passing score per element. The pools
# state the exam questions per subelement but not the passing score.
EXAM_RULE_URL = "https://www.law.cornell.edu/cfr/text/47/97.503"
EXAM_RULE = {2: (35, 26), 3: (35, 26), 4: (50, 37)}

POOLS = {
    "technician-2026-2030": {
        "element": "technician", "fcc_element": 2, "title": "2026-2030 Technician Class",
        "page": "https://ncvec.org/index.php/2026-2030-technician-question-pool",
        "statement": "The NCVEC Question Pool Committee (QPC) hereby releases the 2026-2030 Technician "
                     "Class (Element 2) Question Pool into the public domain.",
        "docx": "technician-pool-docx", "pdf": "technician-pool-pdf",
        "valid_to": "2030-06-30",
        "figures": [("T-1", "T-1.jpg", "technician-diagram-t1-jpg", None, None),
                    ("T-2", "T-2.jpg", "technician-diagram-t2-jpg", None, None),
                    ("T-3", "T-3.jpg", "technician-diagram-t3-jpg", None, None)],
    },
    "general-2023-2027": {
        "element": "general", "fcc_element": 3, "title": "2023-2027 General Class",
        "page": "https://ncvec.org/index.php/2023-2027-general-question-pool-release",
        "statement": "The NCVEC Question Pool Committee hereby releases into public domain the 2023-2027 "
                     "General, Element 3, Question pool.",
        "docx": "general-pool-docx", "pdf": "general-pool-pdf",
        "valid_to": "2027-06-30",
        "figures": [("G7-1", "G7-1.pdf", "general-figure-g7-1-pdf", None, None),
                    ("G7-1", "G7-1.png", "general-figure-g7-1-pdf", None, "pdftoppm -r 200 -png -singlefile")],
    },
    "extra-2024-2028": {
        "element": "extra", "fcc_element": 4, "title": "2024-2028 Amateur Extra Class",
        "page": "https://ncvec.org/index.php/2024-2028-extra-class-question-pool-release",
        "statement": "The NCVEC Question Pool Committee hereby releases into public domain the 2024-2028 "
                     "Element 4 Extra Class Question Pool.",
        "docx": "extra-pool-docx", "pdf": "extra-pool-pdf",
        "valid_to": "2028-06-30",
        "figures": [(f, f"{f}.svg", "extra-figures-svg-zip", f"{f}.svg", None)
                    for f in ("E5-1", "E6-1", "E6-2", "E6-3", "E7-1", "E7-2", "E7-3", "E9-1", "E9-2", "E9-3")],
    },
}

# Every file downloaded, as linked from the NCVEC release pages on 2026-09-12.
# "committed" says whether its bytes (or a figure from it) land in the tree.
DL = "https://ncvec.org/downloads/"
FILES = [
    ("technician-pool-docx", "technician-2026-2030", "pool", DL + "2026-2030 Technician Pool and Syllabus Public Release Feb 19 2026.docx"),
    ("technician-pool-pdf", "technician-2026-2030", "pool cross-check", DL + "2026-2030 Technician Pool and Syllabus Public Release Feb 19 2026.pdf"),
    ("technician-diagrams-pdf", "technician-2026-2030", "figures, all three (not committed; the JPGs are)", DL + "TECH_2026/2026-2030%20Technician%20Pool%203%20Diagrams.pdf"),
    ("technician-diagram-t1-jpg", "technician-2026-2030", "figure T-1", DL + "TECH_2026/Technician%20Diagram%20T1.jpg"),
    ("technician-diagram-t2-jpg", "technician-2026-2030", "figure T-2", DL + "TECH_2026/Technician%20Diagram%20T2.jpg"),
    ("technician-diagram-t3-jpg", "technician-2026-2030", "figure T-3", DL + "TECH_2026/Technician%20Diagram%20T3.jpg"),
    ("general-pool-docx", "general-2023-2027", "pool", DL + "General Class Pool and Syllabus 2023-2027 Public Release with 6th Errata Feb 4 2026.docx"),
    ("general-pool-pdf", "general-2023-2027", "pool cross-check", DL + "General Class Pool and Syllabus 2023-2027 Public Release with 6th Errata Feb 4 2026.pdf"),
    ("general-figure-g7-1-pdf", "general-2023-2027", "figure G7-1", "http://www.ncvec.org/downloads/G7-1.pdf"),
    ("extra-pool-docx", "extra-2024-2028", "pool", DL + "2024-2028 Extra Class Question Pool and Syllabus Public Release with 4th Errata Feb 4 2026.docx"),
    ("extra-pool-pdf", "extra-2024-2028", "pool cross-check", DL + "2024-2028 Extra Class Question Pool and Syllabus Public Release with 4th Errata Feb 4 2026.pdf"),
    ("extra-figures-pdf", "extra-2024-2028", "figures, all ten (not committed; the SVGs are)", "http://www.ncvec.org/downloads/Extra_Figures_2024-2028-1.pdf"),
    ("extra-diagrams-page-1-jpg", "extra-2024-2028", "figures page 1 (not committed)", "http://www.ncvec.org/downloads/2024-2028 Amateur Extra Class Pool Diagrams_Page_1.jpg"),
    ("extra-diagrams-page-2-jpg", "extra-2024-2028", "figures page 2 (not committed)", "http://www.ncvec.org/downloads/2024-2028 Amateur Extra Class Pool Diagrams_Page_2.jpg"),
    ("extra-diagrams-page-3-jpg", "extra-2024-2028", "figures page 3 (not committed)", "http://www.ncvec.org/downloads/2024-2028 Amateur Extra Class Pool Diagrams_Page_3_V2.jpg"),
    ("extra-figures-svg-zip", "extra-2024-2028", "figures, all ten as SVG", "http://www.ncvec.org/downloads/e4_2024-svgs.zip"),
]
UNAVAILABLE = [
    ("general-2023-2027", "http://www.ncvec.org/downloads/G7-1 diagram 2023 Figure G7-1.jpg",
     "HTTP 404 on 2026-09-12, linked from the General release page as General Question Pool Graphics.jpg; "
     "the figure is used from G7-1.pdf instead"),
]

# Defects in NCVEC's own documents, found by the validator and reported as
# found. A listed defect is a WARNING; a new mismatch is CRITICAL.
KNOWN_SOURCE_DEFECTS = {
    ("general-2023-2027", "G1"): "the syllabus header states 54 questions, but the pool holds 52 live questions and 5 "
                                 "withdrawn (G1A04, G1C08, G1C09, G1C10, G1E09): the stated count matches neither",
}

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
ID_RE = re.compile(r"^([TGE]\d[A-Z]\d\d)\s*\(([A-D])\)\s*(?:\[([^\]]*)\])?\s*$")
DEL_RE = re.compile(r"^([TGE]\d[A-Z]\d\d)\s+Question Deleted\b", re.I)
SUB_RE = re.compile(r"^SUBELEMENT ([TGE]\d)\s*[–-]\s*(.*?)\s*-?\s*\[(\d+) exam questions?\s*[–-]\s*(\d+) groups?\]"
                    r"\s*(?:(\d+)\s+Questions?)?\s*$", re.I)
GROUP_RE = re.compile(r"^([TGE]\d[A-Z])\s*[–-]?\s+(\S.*)$")
ANS_RE = re.compile(r"^([A-D])\.\s*(.*)$")
# NCVEC types some figure names with a non-breaking hyphen (U+2011): "Figure E7‑3".
FIG_RE = re.compile(r"\b[Ff]igure\s+([TGE])[-‑–]?(\d)(?:[-‑–]?(\d))?\b")
END_RE = re.compile(r"end of question pool text", re.I)
EDIT_RE = re.compile(r"^([TGE]\d[A-Z]\d\d)\s*[–-]\s*(\S.*)$")
MONTHS = {m: i for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"), 1)}


def line(level, msg):
    style = os.environ.get("HEE_STATUS_STYLE", "icon")
    text = f"{LABEL[level]} {msg}" if style in ("plain", "ascii") else f"{ICON[level]} {LABEL[level]} {msg}"
    print(text, file=sys.stdout if level == OK else sys.stderr)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# Superscript and subscript runs (<w:vertAlign w:val="superscript"/>) become
# Unicode characters, never flattened: "I<sup>2</sup>" is I², and "I2" would be
# a different formula. Text with no Unicode form is kept visibly marked as
# ⟦superscript:text⟧ and is CRITICAL in validation. Measured 2026-09-12: the
# Technician docx has 5 superscript runs (T5C08, T5D01, T5D02); General and
# Extra have none.
SUPERSCRIPT = dict(zip("0123456789+-−", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁻"))
SUBSCRIPT = dict(zip("0123456789", "₀₁₂₃₄₅₆₇₈₉"))
SUPSUB_CHARS = set(SUPERSCRIPT.values()) | set(SUBSCRIPT.values())
UNMAPPED = re.compile(r"⟦(superscript|subscript):([^⟧]*)⟧")


def shift(text: str, align: str) -> tuple[str, int]:
    """(text in Unicode superscript or subscript, characters mapped), or a ⟦marker⟧ and -1 if any character has no form."""
    table = SUPERSCRIPT if align == "superscript" else SUBSCRIPT
    if all(c in table or c.isspace() for c in text):
        return "".join(table.get(c, c) for c in text), sum(1 for c in text if c in table)
    return f"⟦{align}:{text}⟧", -1


def paragraphs(docx: bytes, stats: dict | None = None) -> list[str]:
    """Paragraph text from word/document.xml. A non-breaking hyphen stays U+2011; tabs and breaks are whitespace;
    superscript and subscript runs become Unicode (see SUPERSCRIPT). stats, if given, receives runs, mapped,
    unmappable [(paragraph, align, text)], mapped_by_para and literal_by_para."""
    root = ET.fromstring(zipfile.ZipFile(io.BytesIO(docx)).read("word/document.xml"))
    st = stats if stats is not None else {}
    st.update(runs=0, mapped=0, unmappable=[], mapped_by_para={}, literal_by_para={})
    out = []
    for idx, p in enumerate(root.iter(W + "p")):
        parts = []
        for r in p.iter(W + "r"):
            va = r.find(f"{W}rPr/{W}vertAlign")
            align = va.get(W + "val") if va is not None else None
            buf = []
            for n in r:
                if n.tag == W + "t":
                    buf.append(n.text or "")
                elif n.tag in (W + "tab", W + "ptab", W + "br", W + "cr"):
                    buf.append(" ")
                elif n.tag == W + "noBreakHyphen":
                    buf.append("‑")
            text = "".join(buf)
            if align in ("superscript", "subscript") and text.strip():
                st["runs"] += 1
                shifted, n_mapped = shift(text, align)
                if n_mapped < 0:
                    st["unmappable"].append((idx, align, text))
                else:
                    st["mapped"] += n_mapped
                    st["mapped_by_para"][idx] = st["mapped_by_para"].get(idx, 0) + n_mapped
                parts.append(shifted)
            else:
                literal = sum(1 for c in text if c in SUPSUB_CHARS)
                if literal:
                    st["literal_by_para"][idx] = st["literal_by_para"].get(idx, 0) + literal
                parts.append(text)
        out.append(norm("".join(parts)))
    return out


def iso_date(text: str) -> str | None:
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text.strip())
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.fullmatch(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})", text.strip())
    if m and m.group(1) in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"
    return None


def parse(paras: list[str]) -> dict:
    """The pool model from paragraph text: errata, syllabus, subelements, groups, questions, problems."""
    nb = [i for i, t in enumerate(paras) if t]
    problems = []
    body = None
    for k, i in enumerate(nb):
        m = SUB_RE.match(paras[i])
        if m and m.group(5) is None and k + 2 < len(nb) and GROUP_RE.match(paras[nb[k + 1]]) \
                and (ID_RE.match(paras[nb[k + 2]]) or DEL_RE.match(paras[nb[k + 2]])):
            body = i
            break
    if body is None:
        raise ValueError("no question pool body found: no SUBELEMENT header followed by a group and a question")
    end = next((i for i in range(body, len(paras)) if END_RE.search(paras[i])), len(paras))

    n_body_subs = sum(1 for i in range(body, end) if SUB_RE.match(paras[i]))
    syl_idx = [i for i in nb if i < body and (m := SUB_RE.match(paras[i])) and m.group(5)][-n_body_subs:]
    syllabus = {}
    for j, i in enumerate(syl_idx):
        m = SUB_RE.match(paras[i])
        stop = syl_idx[j + 1] if j + 1 < len(syl_idx) else body
        groups = [g.group(1) for t in paras[i + 1:stop] if (g := GROUP_RE.match(t)) and g.group(1).startswith(m.group(1))]
        syllabus[m.group(1)] = {"questions": int(m.group(5)), "groups": groups}
    effective = next((paras[i][len("Effective "):] for i in reversed(nb) if i < body and paras[i].startswith("Effective ")), None)

    errata, header, issued, owner = {}, None, None, {}
    for i in nb:
        if i >= (syl_idx[0] if syl_idx else body):
            break
        t = paras[i]
        if t.endswith("Errata"):
            header, issued = t, None
        elif t.startswith("Issued "):
            issued = t[len("Issued "):]
        elif (m := EDIT_RE.match(t)) and header:
            entry = {"errata": header, "issued": issued, "change": t, "reads": None}
            if t.rstrip().endswith("to read:"):
                j = next((j for j in nb if j > i), None)
                nxt = paras[j] if j is not None else ""
                if nxt and not EDIT_RE.match(nxt) and not nxt.endswith("Errata"):
                    entry["reads"] = nxt
                    owner[j] = m.group(1)
            errata.setdefault(m.group(1), []).append(entry)

    subs, q, cur_sub, cur_group, seen = [], None, None, None, {}

    def finish():
        nonlocal q
        if q is None:
            return
        lines, choices, question = q.pop("lines"), [], []
        for t in lines:
            m = ANS_RE.match(t)
            if m and (choices or question):
                choices.append([m.group(1), m.group(2)])
            elif choices:
                choices[-1][1] = f"{choices[-1][1]} {t}"
            else:
                question.append(t)
        q["question"], q["choices"] = " ".join(question), choices
        cur_group["questions"].append(q)
        q = None

    for i in range(body, end):
        t = paras[i]
        if not t:
            continue
        if t.startswith("~~"):
            finish()
            continue
        if m := SUB_RE.match(t):
            finish()
            cur_sub = {"id": m.group(1), "title": m.group(2), "exam": int(m.group(3)), "groups_stated": int(m.group(4)), "groups": []}
            subs.append(cur_sub)
            cur_group = None
            continue
        if (m := ID_RE.match(t)) or (d := DEL_RE.match(t)):
            finish()
            qid = (m or d).group(1)
            if cur_group is None:
                problems.append((CRITICAL, f"{qid}: a question before any group header (paragraph {i})"))
                continue
            if qid in seen:
                problems.append((CRITICAL, f"{qid}: duplicate id (paragraphs {seen[qid]} and {i})"))
            seen[qid] = i
            if m:
                q = {"id": qid, "correct": m.group(2), "rule_ref": m.group(3), "lines": [], "errata": errata.get(qid, [])}
            else:
                cur_group["withdrawn"].append({"id": qid, "errata": errata.get(qid, [])})
            continue
        if q is not None:
            q["lines"].append(t)
            owner[i] = q["id"]
            continue
        if (m := GROUP_RE.match(t)) and cur_sub:
            cur_group = {"id": m.group(1), "title": m.group(2).strip(), "questions": [], "withdrawn": []}
            cur_sub["groups"].append(cur_group)
            continue
        problems.append((CRITICAL, f"unparsed paragraph {i}: {t[:80]!r}"))
    finish()
    return {"subelements": subs, "syllabus": syllabus, "effective": effective, "errata": errata, "problems": problems,
            "owner": owner}


def figure_key(letter, d1, d2):
    if letter == "T":
        return f"T-{d1}"
    return f"{letter}{d1}-{d2}" if d2 else None


def question_figure(question: str):
    """(figure id, the text as printed) for a question that names a figure, else (None, None)."""
    m = FIG_RE.search(question)
    if not m:
        return None, None
    return figure_key(*m.groups()), m.group(0)


def errata_missing(q: dict, e: dict):
    """The errata's replacement text if the pool does not carry it, else None. Only 'to read:' changes are checkable."""
    reads = e.get("reads")
    if not reads:
        return None
    if m := ANS_RE.match(reads):
        return None if dict(q["choices"]).get(m.group(1)) == m.group(2) else reads
    if m := ID_RE.match(reads):
        return None if (m.group(2), m.group(3)) == (q["correct"], q["rule_ref"]) else reads
    return None if q["question"] == reads else reads


def validate(pool: str, model: dict, fcc_element: int, figure_files: dict, known=KNOWN_SOURCE_DEFECTS) -> list:
    """(level, message) findings. figure_files maps a figure id to its file name, or is empty if none exist."""
    out = list(model["problems"])
    exam_total = 0
    for sub in model["subelements"]:
        sid = sub["id"]
        exam_total += sub["exam"]
        syl = model["syllabus"].get(sid)
        body_groups = [g["id"] for g in sub["groups"]]
        if syl is None:
            out.append((CRITICAL, f"{pool} {sid}: in the pool but not in the syllabus"))
        elif syl["groups"] != body_groups:
            out.append((CRITICAL, f"{pool} {sid}: syllabus groups {syl['groups']} differ from the pool's {body_groups}"))
        if len(body_groups) != sub["groups_stated"]:
            out.append((CRITICAL, f"{pool} {sid}: header states {sub['groups_stated']} groups, the pool has {len(body_groups)}"))
        live = wd = 0
        for g in sub["groups"]:
            if not g["id"].startswith(sid):
                out.append((CRITICAL, f"{pool} {g['id']}: group sits under subelement {sid}"))
            if not g["questions"]:
                out.append((CRITICAL, f"{pool} {g['id']}: group has no questions"))
            live += len(g["questions"])
            wd += len(g["withdrawn"])
            for q in g["questions"]:
                if not q["id"].startswith(g["id"]):
                    out.append((CRITICAL, f"{pool} {q['id']}: question sits under group {g['id']}"))
                if [c[0] for c in q["choices"]] != list("ABCD"):
                    out.append((CRITICAL, f"{pool} {q['id']}: choices {[c[0] for c in q['choices']]}, not A-D"))
                if q["correct"] not in "ABCD":
                    out.append((CRITICAL, f"{pool} {q['id']}: key {q['correct']} is not A-D"))
                if not q["question"]:
                    out.append((CRITICAL, f"{pool} {q['id']}: no question text"))
                for field, text in [("question", q["question"])] + [(f"choice {k}", v) for k, v in q["choices"]]:
                    for mm in UNMAPPED.finditer(text):
                        out.append((CRITICAL, f"{pool} {q['id']}: {field} has a {mm.group(1)} run {mm.group(2)!r} with no Unicode form"))
                for e in q["errata"]:
                    miss = errata_missing(q, e)
                    if miss:
                        out.append((WARNING, f"{pool} {q['id']}: {e['errata']} ({e['issued']}) says {miss!r}, which the pool text does not carry"))
                fid, printed = question_figure(q["question"])
                if printed and fid is None:
                    out.append((CRITICAL, f"{pool} {q['id']}: names {printed!r}, which is no figure id"))
                elif fid and fid not in figure_files:
                    out.append((CRITICAL, f"{pool} {q['id']}: names figure {fid}, which does not exist"))
        if syl is not None:
            stated = syl["questions"]
            if stated == live or stated == live + wd:
                pass
            elif (pool, sid) in known:
                out.append((WARNING, f"{pool} {sid}: source defect -- {known[(pool, sid)]}"))
            else:
                out.append((CRITICAL, f"{pool} {sid}: syllabus states {stated} questions; the pool has {live} live, {wd} withdrawn"))
    size = EXAM_RULE[fcc_element][0]
    if exam_total != size:
        out.append((CRITICAL, f"{pool}: subelement exam questions sum to {exam_total}, 47 CFR 97.503 says {size}"))
    used = {question_figure(q["question"])[0] for s in model["subelements"] for g in s["groups"] for q in g["questions"]}
    for fid in sorted(set(figure_files) - used):
        out.append((WARNING, f"{pool}: figure {fid} is named by no question"))
    return out


SUPSUB_FIELD = re.compile(r"^\s*(question|[ABCD]|reads): ")


def supsub_check(pool: str, stats: dict, model: dict, files: dict) -> list:
    """The docx's superscript/subscript runs against the Unicode characters written into questions, choices
    and errata replacement text. pdftotext flattens superscripts too, so the PDF cross-check cannot see this."""
    out = []
    owner = model.get("owner", {})
    for idx, align, text in stats["unmappable"]:
        who = owner.get(idx, f"paragraph {idx}")
        out.append((CRITICAL, f"{pool} {who}: {align} run {text!r} has no Unicode form"))
    consumed = set(owner)
    expected = sum(stats["mapped_by_para"].get(i, 0) + stats["literal_by_para"].get(i, 0) for i in consumed)
    outside = sum(n for i, n in stats["mapped_by_para"].items() if i not in consumed)
    written = sum(sum(1 for c in ln if c in SUPSUB_CHARS)
                  for rel, text in files.items() if rel.endswith(".pill.v1.yaml")
                  for ln in text.splitlines() if SUPSUB_FIELD.match(ln))
    if not stats["runs"]:
        out.append((OK, f"{pool}: no superscript or subscript runs in the docx"))
    elif written != expected:
        out.append((CRITICAL, f"{pool}: {stats['runs']} superscript/subscript run(s), {expected} character(s) expected in "
                              f"questions and choices, {written} written"))
    else:
        where = sorted({owner[i] for i in stats["mapped_by_para"] if i in owner})
        extra = f"; {outside} outside the questions" if outside else ""
        out.append((OK, f"{pool}: {stats['runs']} superscript/subscript run(s) in the docx, {stats['mapped']} character(s) "
                        f"mapped to Unicode, {written} written ({', '.join(where)}){extra}"))
    return out


def pdf_crosscheck(pool: str, model: dict, pdf: Path) -> list:
    if not shutil.which("pdftotext"):
        return [(WARNING, f"{pool}: pdftotext not installed -- the PDF cross-check did not run")]
    text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
    pdf_pairs = set(re.findall(r"(?m)^\s*([TGE]\d[A-Z]\d\d)\s*\(([A-D])\)", text))
    doc_pairs = {(q["id"], q["correct"]) for s in model["subelements"] for g in s["groups"] for q in g["questions"]}
    if pdf_pairs != doc_pairs:
        return [(WARNING, f"{pool}: PDF and docx disagree on ids/keys -- only in PDF {sorted(pdf_pairs - doc_pairs)[:10]}, "
                          f"only in docx {sorted(doc_pairs - pdf_pairs)[:10]}")]
    return [(OK, f"{pool}: pdftotext of the pool PDF has the same {len(pdf_pairs)} question ids and keys")]


# ---- rendering ---------------------------------------------------------------------------------------------

def q(v) -> str:
    return "null" if v is None else json.dumps(v, ensure_ascii=False)


def envelope(kind, name, description, labels):
    y = ["apiVersion: hee/v1", f"kind: {kind}", "metadata:", f"  name: {name}", f"  description: {q(description)}",
         "  labels:", '    hee.object: "true"', "    domain: ham"]
    y += [f"    {k}: {v}" for k, v in labels]
    y += ["  annotations:", "    inuid: null", "    inuid_null_reason: generated from the NCVEC pool", "spec:"]
    return y


def errata_block(entries, indent):
    if not entries:
        return []
    p = " " * indent
    y = [f"{p}errata:"]
    for e in entries:
        y += [f"{p}  - errata: {q(e['errata'])}", f"{p}    issued: {q(e['issued'])}", f"{p}    change: {q(e['change'])}"]
        if e.get("reads"):
            y += [f"{p}    reads: {q(e['reads'])}"]
    return y


def render_pool(pool: str, meta: dict, model: dict, src: dict, figure_files: dict) -> dict:
    """{repo-relative path: text} for one pool's YAML."""
    el, base = meta["element"], f"{REL_OUT}/{pool}"
    docx = src[meta["docx"]]
    files = {}
    subs = model["subelements"]
    for sub in subs:
        sid = sub["id"]
        for g in sub["groups"]:
            gid = g["id"]
            for qq in g["questions"]:
                fid, printed = question_figure(qq["question"])
                choices = dict(qq["choices"])
                y = envelope("Pill", f"ham-{el}-{qq['id'].lower()}", f"{meta['title']} question {qq['id']}, NCVEC question pool",
                             [("element", el), ("pool", pool), ("subelement", sid), ("group", gid)])
                y += [f"  question: {q(qq['question'])}", f"  answer: {q(choices[qq['correct']])}", f"  id: {qq['id']}",
                      f"  correct: {qq['correct']}", "  choices:"] + [f"    {k}: {q(v)}" for k, v in qq["choices"]]
                y += [f"  rule_ref: {q(qq['rule_ref'])}", f"  figure: {q(f'{base}/figures/{figure_files[fid]}' if fid else None)}"]
                if printed and re.sub(r"[‑–]", "-", printed.split()[-1]) != fid:
                    y += [f"  figure_printed_as: {q(printed)}"]
                y += errata_block(qq["errata"], 2)
                y += ["  source:", f"    file: {q(docx['file'])}", f"    sha256: {q(docx['sha256'])}"]
                files[f"{base}/{sid}/{gid}/{qq['id']}.pill.v1.yaml"] = "\n".join(y) + "\n"
            y = envelope("Card", f"ham-{el}-{gid.lower()}", f"{meta['title']} group {gid}: {g['title']}",
                         [("element", el), ("pool", pool), ("subelement", sid), ("group", gid)])
            y += [f"  group: {gid}", f"  title: {q(g['title'])}", f"  subelement: {sid}", f"  questions: {len(g['questions'])}",
                  "  question_ids:"] + [f"    - {qq['id']}" for qq in g["questions"]]
            if g["withdrawn"]:
                y += ["  withdrawn:"]
                for w in g["withdrawn"]:
                    y += [f"    - id: {w['id']}"] + errata_block(w["errata"], 6)
            files[f"{base}/{sid}/{gid}/{gid}.card.v1.yaml"] = "\n".join(y) + "\n"
        syl = model["syllabus"].get(sid, {})
        live = sum(len(g["questions"]) for g in sub["groups"])
        wd = [w["id"] for g in sub["groups"] for w in g["withdrawn"]]
        note = None
        if syl.get("questions") == live + len(wd) and wd:
            note = f"the syllabus count includes {len(wd)} withdrawn question(s)"
        elif syl.get("questions") not in (None, live, live + len(wd)):
            note = KNOWN_SOURCE_DEFECTS.get((pool, sid), "the syllabus count matches neither the live nor the withdrawn-inclusive count")
        y = envelope("Card", f"ham-{el}-{sid.lower()}", f"{meta['title']} subelement {sid}: {sub['title']}",
                     [("element", el), ("pool", pool), ("subelement", sid)])
        y += [f"  subelement: {sid}", f"  title: {q(sub['title'])}", f"  exam_questions: {sub['exam']}",
              f"  groups_stated: {sub['groups_stated']}", f"  questions_stated: {q(syl.get('questions'))}",
              f"  questions: {live}", "  withdrawn: [" + ", ".join(wd) + "]", f"  count_note: {q(note)}", "  groups:"]
        for g in sub["groups"]:
            y += [f"    - id: {g['id']}", f"      title: {q(g['title'])}", f"      questions: {len(g['questions'])}"]
        files[f"{base}/{sid}/{sid}.card.v1.yaml"] = "\n".join(y) + "\n"

    size, passing = EXAM_RULE[meta["fcc_element"]]
    eff = model["effective"] or ""
    parts = re.split(r"\s+[–-]\s+", eff)
    valid_from = iso_date(parts[0]) if parts else None
    stated_to = iso_date(parts[1]) if len(parts) > 1 else None
    live_all = sum(len(g["questions"]) for s in subs for g in s["groups"])
    wd_all = [w["id"] for s in subs for g in s["groups"] for w in g["withdrawn"]]
    latest = max((e for es in model["errata"].values() for e in es), key=lambda e: iso_date(e["issued"] or "") or "", default=None)
    y = envelope("Card", f"ham-{pool}", f"NCVEC {meta['title']} question pool (FCC Element {meta['fcc_element']})",
                 [("element", el), ("pool", pool)])
    y += [f"  pool: {pool}", f"  element: {el}", f"  fcc_element: {meta['fcc_element']}", f"  title: {q(meta['title'])}",
          f"  syllabus_effective: {q(eff)}", f"  valid_from: {q(valid_from)}", f"  valid_to: {q(stated_to or meta['valid_to'])}",
          f"  valid_to_source: {q('the syllabus' if stated_to else 'the pool name; the syllabus states no end date')}",
          f"  questions: {live_all}", "  withdrawn: [" + ", ".join(wd_all) + "]",
          f"  questions_stated: {sum(v['questions'] for v in model['syllabus'].values())}",
          f"  exam_questions: {sum(s['exam'] for s in subs)}", f"  exam_size: {size}", f"  passing_score: {passing}",
          f"  exam_rule: {q('47 CFR 97.503; the pool states exam questions per subelement, not the passing score')}",
          f"  exam_rule_url: {q(EXAM_RULE_URL)}",
          f"  latest_errata: {q(latest['errata'] if latest else None)}", f"  latest_errata_issued: {q(latest['issued'] if latest else None)}",
          "  subelements:"] + [f"    - {s['id']}" for s in subs]
    y += ["  figures:"]
    for fid, fname, sid_, member, derived in meta["figures"]:
        path = f"{base}/figures/{fname}"
        y += [f"    - id: {fid}", f"      file: {q(path)}", f"      from: {sid_}",
              f"      shipped: {'false' if derived else 'true'}", f"      derived_by: {q(derived)}"]
    y += ["  public_domain:", f"    statement: {q(meta['statement'])}", f"    page: {q(meta['page'])}",
          "  source:", f"    sources: {q(REL_OUT + '/sources.yaml')}", f"    file: {q(docx['file'])}", f"    sha256: {q(docx['sha256'])}"]
    files[f"{base}/pool.card.v1.yaml"] = "\n".join(y) + "\n"
    return files


def write_figures(pool: str, meta: dict, cache: Path, dest: Path) -> list:
    """Copy or derive each figure into dest/<pool>/figures. Returns findings."""
    out = []
    figdir = dest / pool / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    src_files = {f[0]: f for f in FILES}
    for fid, fname, sid, member, derived in meta["figures"]:
        src = cache / Path(src_files[sid][3].rsplit("/", 1)[1].replace("%20", " "))
        if derived:
            if not shutil.which("pdftoppm"):
                out.append((WARNING, f"{pool}: pdftoppm not installed -- {fname} not derived"))
                continue
            stem = figdir / Path(fname).stem
            subprocess.run(["pdftoppm", "-r", "200", "-png", "-singlefile", str(src), str(stem)], check=True)
        elif member:
            (figdir / fname).write_bytes(zipfile.ZipFile(src).read(member))
        else:
            shutil.copyfile(src, figdir / fname)
    return out


# ---- sources -----------------------------------------------------------------------------------------------

def cache_name(url: str) -> str:
    return url.rsplit("/", 1)[1].replace("%20", " ")


def record_sources(cache: Path, path: Path) -> int:
    y = ["apiVersion: hee/v1", "kind: Registry", "metadata:", "  name: ham-pools-sources",
         f"  description: {q('Every NCVEC file the ham question pool tree is built from: where it came from, its size and sha256, and the public-domain release that covers it.')}",
         "  labels:", '    hee.object: "true"', "    domain: ham", "  annotations:", "    inuid: null",
         "    inuid_null_reason: generated from the NCVEC pool", "spec:",
         f"  cache: {q('${XDG_CACHE_HOME:-$HOME/.cache}/ham-pools/files')}", "  pools:"]
    for pool, meta in POOLS.items():
        y += [f"    - pool: {pool}", f"      page: {q(meta['page'])}", f"      public_domain_statement: {q(meta['statement'])}"]
    y += ["  files:"]
    for fid, pool, role, url in FILES:
        f = cache / cache_name(url)
        if not f.is_file():
            line(UNKNOWN, f"missing download: {f}")
            return UNKNOWN
        b = f.read_bytes()
        fetched = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        y += [f"    - id: {fid}", f"      pool: {pool}", f"      role: {q(role)}", f"      url: {q(url)}",
              f"      file: {q(f.name)}", f"      bytes: {len(b)}", f"      sha256: {q(hashlib.sha256(b).hexdigest())}",
              f"      fetched_at: {q(fetched)}"]
    y += ["  unavailable:"]
    for pool, url, status in UNAVAILABLE:
        y += [f"    - pool: {pool}", f"      url: {q(url)}", f"      status: {q(status)}"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(y) + "\n", encoding="utf-8")
    line(OK, f"wrote {path.relative_to(REPO) if path.is_relative_to(REPO) else path}")
    return OK


def read_sources(path: Path) -> dict:
    """{id: {file, sha256, bytes, ...}} from the files section of sources.yaml, the format record_sources writes."""
    out, cur, section = {}, None, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^  \w+:", raw):
            section = raw.strip().rstrip(":").split(":")[0]
            continue
        if section != "files":
            continue
        m = re.match(r"^\s{4}(?:- )?\s*(\w+): (.*)$", raw)
        if not m:
            continue
        k, v = m.group(1), m.group(2)
        v = json.loads(v) if v[:1] in '"-0123456789' or v == "null" else v
        if raw.lstrip().startswith("- id:"):
            cur = out.setdefault(v, {})
        if cur is not None:
            cur[k] = v
    return out


def verified(cache: Path, sources: dict) -> tuple[int, str]:
    for fid, _pool, _role, url in FILES:
        rec = sources.get(fid)
        f = cache / cache_name(url)
        if rec is None:
            return CRITICAL, f"{fid}: not in sources.yaml -- run --record-sources after checking the download"
        if not f.is_file():
            return UNKNOWN, f"missing download: {f}"
        got = hashlib.sha256(f.read_bytes()).hexdigest()
        if got != rec["sha256"]:
            return CRITICAL, f"{f.name}: sha256 {got} does not match sources.yaml {rec['sha256']} -- refusing"
    return OK, ""


def build(cache: Path, dest_root: Path) -> tuple[int, dict]:
    """Build every pool under dest_root/ham/pools. Returns (worst level, stats)."""
    src_path = REPO / REL_OUT / "sources.yaml"
    if not src_path.is_file():
        line(UNKNOWN, f"no {REL_OUT}/sources.yaml -- run --record-sources")
        return UNKNOWN, {}
    sources = read_sources(src_path)
    lvl, msg = verified(cache, sources)
    if lvl:
        line(lvl, msg)
        return lvl, {}
    worst, stats = OK, {}
    dest = dest_root / REL_OUT
    for pool, meta in POOLS.items():
        docx = cache / sources[meta["docx"]]["file"]
        stats = {}
        model = parse(paragraphs(docx.read_bytes(), stats))
        figure_files = {}
        for fid, fname, _s, _m, derived in meta["figures"]:
            if derived and not shutil.which("pdftoppm"):
                continue
            figure_files[fid] = fname
        if (dest / pool).exists():
            shutil.rmtree(dest / pool)
        findings = write_figures(pool, meta, cache, dest)
        findings += validate(pool, model, meta["fcc_element"], figure_files)
        findings += pdf_crosscheck(pool, model, cache / sources[meta["pdf"]]["file"])
        rendered = render_pool(pool, meta, model, sources, figure_files)
        findings += supsub_check(pool, stats, model, rendered)
        for rel, text in rendered.items():
            p = dest_root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        for fid, fname, *_ in meta["figures"]:
            if fid in figure_files and not (dest / pool / "figures" / fname).is_file():
                findings.append((CRITICAL, f"{pool}: figure file {fname} was not written"))
        subs = model["subelements"]
        n = sum(len(g["questions"]) for s in subs for g in s["groups"])
        wd = sum(len(g["withdrawn"]) for s in subs for g in s["groups"])
        stats[pool] = {"questions": n, "withdrawn": wd, "groups": sum(len(s["groups"]) for s in subs),
                       "subelements": len(subs), "figures": len({f[0] for f in meta["figures"]}),
                       "exam": sum(s["exam"] for s in subs)}
        for level, msg in findings:
            line(level, msg)
            worst = max(worst, level)
        line(OK, f"{pool}: {n} questions ({wd} withdrawn), {stats[pool]['groups']} groups, {len(subs)} subelements, "
                 f"exam {stats[pool]['exam']}, {stats[pool]['figures']} figures")
    return worst, stats


def tree(root: Path) -> dict:
    base = root / REL_OUT
    return {p.relative_to(root).as_posix(): p for p in base.rglob("*") if p.is_file() and p.name != "sources.yaml"} if base.exists() else {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="build-pools.py", description="the NCVEC question pools as HEE Pills and Cards")
    ap.add_argument("--check", action="store_true", help="build into a temp dir and compare with the committed tree")
    ap.add_argument("--record-sources", action="store_true", help="hash the downloads and write sources.yaml")
    ap.add_argument("--cache", type=Path, default=CACHE)
    a = ap.parse_args(argv)
    if a.record_sources:
        return record_sources(a.cache, REPO / REL_OUT / "sources.yaml")
    if not a.check:
        worst, stats = build(a.cache, REPO)
        return worst
    with tempfile.TemporaryDirectory() as tmp:
        worst, stats = build(a.cache, Path(tmp))
        if worst == UNKNOWN:
            return worst
        new, old = tree(Path(tmp)), tree(REPO)
        drift = sorted(set(new) ^ set(old))
        for rel in sorted(set(new) & set(old)):
            if rel.endswith(".png"):   # derived by pdftoppm: its bytes depend on the poppler version, so existence only
                continue
            if not filecmp.cmp(new[rel], old[rel], shallow=False):
                drift.append(rel)
        if drift:
            line(CRITICAL, f"drift: {len(drift)} file(s) differ from a fresh build, e.g. {drift[:5]}")
            return CRITICAL
        line(OK, f"no drift: {len(new)} files match a fresh build (derived PNGs compared by existence)")
        return worst


if __name__ == "__main__":
    sys.exit(main())
