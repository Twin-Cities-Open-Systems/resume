#!/usr/bin/env python3
"""ham/bin/build-pools.py: the pool parser and validator, against inline text
fixtures shaped like the NCVEC documents -- never the network, never the
committed tree.

Run: python3 -m unittest tests/test_ham_build_pools.py
"""
import copy
import hashlib
import importlib.util
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_pools", ROOT / "ham" / "bin" / "build-pools.py")
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

# Shapes met in the real documents: an errata preamble whose "to read:" line
# carries the replacement text on the next paragraph; a syllabus header with a
# question count and a body header without one; a rule citation with no space
# before its bracket (T1D12 in the 2026-2030 Technician pool); an answer with
# no space after its letter (G2D in the General pool); a figure named with a
# non-breaking hyphen (E7G07 in the Extra pool); a withdrawn question.
FIXTURE = [
    "2026-2030 Technician Class Pool Errata", "Issued February 19, 2026", "",
    "In the pool itself, 1 question modified:", "T1A01 – change the question to read:", "Which is the right one?", "",
    "2026-2030 Technician Class", "FCC Element 2 Question Pool Syllabus", "Effective 7/01/2026 – 6/30/2030",
    "SUBELEMENT T1 - COMMISSION’S RULES [1 Exam Questions - 1 Groups]  3 Questions",
    "T1A Purpose and permissible use", "",
    "SUBELEMENT T1 - COMMISSION’S RULES [1 Exam Questions - 1 Groups]",
    "T1A Purpose and permissible use",
    "T1A01 (C) [97.1]", "Which is the right one?", "A. One", "B. Two", "C. Three", "D. Four", "~~", "",
    "T1A02 (A)[97.119(a)]", "What is component 1 in figure T‑1?", "A. A resistor", "B.A switch", "C. A lamp", "D. A cell", "~~",
    "T1A03  Question Deleted (section not renumbered)", "~~",
    "~~~~End of question pool text~~~~",
]
FIGS = {"T-1": "T-1.jpg"}


def levels(findings, level):
    return [m for lv, m in findings if lv == level]


class TestParse(unittest.TestCase):

    def setUp(self):
        self.m = bp.parse(FIXTURE)

    def test_structure(self):
        subs = self.m["subelements"]
        self.assertEqual([s["id"] for s in subs], ["T1"])
        self.assertEqual(subs[0]["title"], "COMMISSION’S RULES")
        g = subs[0]["groups"][0]
        self.assertEqual((g["id"], g["title"]), ("T1A", "Purpose and permissible use"))
        self.assertEqual([q["id"] for q in g["questions"]], ["T1A01", "T1A02"])
        self.assertEqual([w["id"] for w in g["withdrawn"]], ["T1A03"])
        self.assertEqual(self.m["syllabus"], {"T1": {"questions": 3, "groups": ["T1A"]}})
        self.assertEqual(self.m["effective"], "7/01/2026 – 6/30/2030")
        self.assertEqual(self.m["problems"], [])

    def test_edge_cases_from_the_real_pools(self):
        q1, q2 = self.m["subelements"][0]["groups"][0]["questions"]
        self.assertEqual((q1["correct"], q1["rule_ref"]), ("C", "97.1"))
        self.assertEqual((q2["correct"], q2["rule_ref"]), ("A", "97.119(a)"))
        self.assertEqual(dict(q2["choices"])["B"], "A switch")
        self.assertEqual(bp.question_figure(q2["question"]), ("T-1", "figure T‑1"))
        self.assertEqual(q1["errata"][0]["reads"], "Which is the right one?")
        self.assertEqual(q1["errata"][0]["issued"], "February 19, 2026")

    def test_paragraphs_keep_the_non_breaking_hyphen(self):
        w = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        xml = (f'<w:document {w}><w:body><w:p><w:r><w:t>Figure E7</w:t><w:noBreakHyphen/><w:t>3</w:t>'
               f'<w:tab/><w:t>  here</w:t></w:r></w:p></w:body></w:document>')
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("word/document.xml", xml)
        self.assertEqual(bp.paragraphs(buf.getvalue()), ["Figure E7‑3 here"])

    def test_no_body_is_an_error(self):
        with self.assertRaises(ValueError):
            bp.parse(["SUBELEMENT T1 - RULES [1 Exam Questions - 1 Groups]  3 Questions", "nothing else"])


class TestValidate(unittest.TestCase):

    def setUp(self):
        self.m = bp.parse(FIXTURE)
        self.rule = mock.patch.dict(bp.EXAM_RULE, {2: (1, 1)})
        self.rule.start()

    def tearDown(self):
        self.rule.stop()

    def run_v(self, model=None, figs=FIGS, known=None):
        return bp.validate("fixture", model or self.m, 2, figs, known or {})

    def test_clean_fixture_passes(self):
        self.assertEqual([f for f in self.run_v() if f[0] != bp.OK], [])

    def test_exam_size_must_match_97_503(self):
        with mock.patch.dict(bp.EXAM_RULE, {2: (35, 26)}):
            self.assertIn("47 CFR 97.503 says 35", " ".join(levels(self.run_v(), bp.CRITICAL)))

    def test_missing_choice_is_critical(self):
        m = copy.deepcopy(self.m)
        m["subelements"][0]["groups"][0]["questions"][0]["choices"].pop()
        self.assertIn("T1A01: choices", " ".join(levels(self.run_v(m), bp.CRITICAL)))

    def test_duplicate_id_is_critical(self):
        m = bp.parse(FIXTURE[:-1] + ["T1A01 (B)", "Again?", "A. a", "B. b", "C. c", "D. d", "~~", FIXTURE[-1]])
        self.assertIn("T1A01: duplicate id", " ".join(levels(self.run_v(m), bp.CRITICAL)))

    def test_missing_figure_is_critical(self):
        self.assertIn("figure T-1, which does not exist", " ".join(levels(self.run_v(figs={}), bp.CRITICAL)))

    def test_unused_figure_is_a_warning(self):
        self.assertIn("figure T-9 is named by no question", " ".join(levels(self.run_v(figs={**FIGS, "T-9": "T-9.jpg"}), bp.WARNING)))

    def test_stated_count_mismatch_is_critical_unless_a_known_source_defect(self):
        m = copy.deepcopy(self.m)
        m["syllabus"]["T1"]["questions"] = 7
        self.assertIn("syllabus states 7 questions", " ".join(levels(self.run_v(m), bp.CRITICAL)))
        found = self.run_v(m, known={("fixture", "T1"): "stated wrong in the source"})
        self.assertEqual(levels(found, bp.CRITICAL), [])
        self.assertIn("source defect -- stated wrong in the source", " ".join(levels(found, bp.WARNING)))

    def test_count_including_withdrawn_is_ok(self):
        self.assertEqual(self.m["syllabus"]["T1"]["questions"], 3)   # 2 live + 1 withdrawn
        self.assertEqual(levels(self.run_v(), bp.CRITICAL) + levels(self.run_v(), bp.WARNING), [])

    def test_group_without_questions_and_group_count(self):
        m = copy.deepcopy(self.m)
        m["subelements"][0]["groups"].append({"id": "T1B", "title": "Empty", "questions": [], "withdrawn": []})
        crit = " ".join(levels(self.run_v(m), bp.CRITICAL))
        self.assertIn("T1B: group has no questions", crit)
        self.assertIn("header states 1 groups, the pool has 2", crit)
        self.assertIn("syllabus groups", crit)

    def test_errata_text_not_carried_is_a_warning(self):
        m = copy.deepcopy(self.m)
        m["subelements"][0]["groups"][0]["questions"][0]["question"] = "The old wording?"
        self.assertIn("says 'Which is the right one?'", " ".join(levels(self.run_v(m), bp.WARNING)))


class TestSources(unittest.TestCase):

    def test_sha_mismatch_is_refused_and_missing_is_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            cache = Path(d)
            (cache / "pool.docx").write_bytes(b"real bytes")
            files = [("a-docx", "fixture", "pool", "https://example.org/pool.docx")]
            good = {"a-docx": {"file": "pool.docx", "sha256": hashlib.sha256(b"real bytes").hexdigest()}}
            with mock.patch.object(bp, "FILES", files):
                self.assertEqual(bp.verified(cache, good)[0], bp.OK)
                self.assertEqual(bp.verified(cache, {"a-docx": {"file": "pool.docx", "sha256": "0" * 64}})[0], bp.CRITICAL)
                (cache / "pool.docx").unlink()
                self.assertEqual(bp.verified(cache, good)[0], bp.UNKNOWN)

    def test_read_sources_round_trips_the_committed_file(self):
        src = bp.read_sources(ROOT / "ham" / "pools" / "sources.yaml")
        self.assertEqual(len(src), len(bp.FILES))
        self.assertEqual(len(src["technician-pool-docx"]["sha256"]), 64)
        self.assertIsInstance(src["technician-pool-docx"]["bytes"], int)


if __name__ == "__main__":
    unittest.main()
