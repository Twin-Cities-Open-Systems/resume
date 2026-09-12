# ham -- the amateur radio question pools, as Pills and Cards

Every question and answer in the three current NCVEC question pools, for the
ham license soup-to-nuts series
([episode one](https://github.com/Twin-Cities-Open-Systems/resume/blob/main/docs/history/held-posts/ham-license-soup-to-nuts-01.md)).
One HEE Pill per question, in directories that follow the pool's own
structure:

    ham/pools/<pool>/<subelement>/<group>/<id>.pill.v1.yaml     one question
    ham/pools/<pool>/<subelement>/<group>/<group>.card.v1.yaml  the group: title, question ids, withdrawn ids
    ham/pools/<pool>/<subelement>/<subelement>.card.v1.yaml     the subelement: exam questions, groups, counts
    ham/pools/<pool>/pool.card.v1.yaml                          the pool: dates, exam size, passing score, figures
    ham/pools/<pool>/figures/                                   the pool's diagrams, as NCVEC ships them

| pool | FCC element | valid | questions | exam | pass |
|---|---|---|---|---|---|
| `technician-2026-2030` | 2 | 2026-07-01 to 2030-06-30 | 409 | 35 | 26 |
| `general-2023-2027` | 3 | 2023-07-01 to 2027-06-30 | 423 | 35 | 26 |
| `extra-2024-2028` | 4 | 2024-07-01 to 2028-06-30 | 599 | 50 | 37 |

A Pill's `spec` opens with `question` and `answer` -- the question text and
the correct choice's text -- then `id`, `correct`, `choices` A-D, `rule_ref`
(the pool's bracketed FCC citation, or null), `figure`, any `errata` that
touched the question, and `source` (the pool document and its sha256). For
example, `ham/pools/technician-2026-2030/T5/T5D/T5D01.pill.v1.yaml`.

## Public domain

NCVEC's Question Pool Committee releases each pool into the public domain.
The statements, quoted verbatim from each pool's release page, are in
`ham/pools/sources.yaml` beside every file used. The passing score is not in
the pools; it is 47 CFR 97.503.

## Regenerate

The pool documents are downloaded to `${XDG_CACHE_HOME:-$HOME/.cache}/ham-pools/files/`,
never into this repository. The URLs are in `ham/pools/sources.yaml`; the
release pages refuse a request without a browser User-Agent.

    python3 ham/bin/build-pools.py --record-sources   # after a new download: size, sha256, fetch time
    python3 ham/bin/build-pools.py                    # rebuild the tree
    python3 ham/bin/build-pools.py --check            # rebuild into a temp dir and compare
    python3 -m unittest tests/test_ham_build_pools.py

The build refuses a downloaded file whose sha256 does not match
`sources.yaml`. It reads each pool's .docx and cross-checks every question
id and answer key against `pdftotext` of the same pool's PDF.

Exit status follows the Nagios convention: 0 OK, 1 WARNING, 2 CRITICAL
(validation failure or drift), 3 UNKNOWN (sources missing).

## What the validator found in NCVEC's documents

- **General, G1:** the syllabus states 54 questions. The pool holds 52 live
  questions and 5 withdrawn, so the stated count matches neither. This is
  listed in `KNOWN_SOURCE_DEFECTS` and reported as a WARNING on every build.
  Any other count mismatch is CRITICAL.
- **Extra:** the syllabus counts for E2, E4 and E9 include their withdrawn
  question; E6's does not. Both forms are accepted and noted on the
  subelement card.
- **General, figure G7-1:** the JPG linked from the release page returned
  HTTP 404. The figure comes from `G7-1.pdf`, with a PNG derived by
  `pdftoppm -r 200`. The PNG is marked `shipped: false` on the pool card.
- **Errata:** every "to read:" replacement in the three errata preambles was
  checked against the pool text. All of them are carried.

## Not here yet

- the view page that shows each group as a card of question/answer pills;
- our own graphics (Ohm's law and the like), drawn in MT-logo or Unicode.
