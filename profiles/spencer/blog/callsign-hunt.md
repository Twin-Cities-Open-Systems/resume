# HwOps Log: Hunting a Real Vanity Call Sign, Soup to Nuts
**Date:** 2026-08-28 (living draft -- updated as the real process actually happens)
**Author:** Spencer Butler (with the fleet)
**Tag:** HWOps For Life

---

## Where this actually starts

Real FCC Registration Number already in hand: **FRN 0038834909**, tied
to `fcc@tcos.us`. Not a placeholder, not "will register eventually" --
that step is done. Everything below builds on that real registration,
in the order it actually happened, not reconstructed after the fact.

## The ask

Two real org identities -- **TCOS** (Twin Cities Open Systems) and
**HEE** (Human Execution Engine, whose own stated top priority is
"correctness over consensus, structure over vibes, determinism over
convenience") -- and a real question: which vanity call signs can
Spencer actually get, ranked, ready to paste into a real FCC Form 605
Schedule D application.

Real constraint discovered immediately: an operator can hold exactly
**two** call signs -- one personal vanity call, one club-station call
as trustee (since 2011-02-14, one club per trustee, one vanity call per
club). Beyond that, only temporary 1x1 special-event calls, coordinated
and time-limited. HEE isn't a club entity, so it gets nothing directly
-- the real split is personal call = Spencer, club call = TCOS.

## Real blocker #1, and how it actually got resolved

A prior session had zero usable network egress -- every real callsign
lookup source (ae7q, QRZ, callook, HamDB, and every `www.fcc.gov` path
tried) came back blocked. Web search was the only escape, and it
proved genuinely untrustworthy: asked about specific real call signs,
it returned *near-miss* answers (W5RK, W2ORK, N0OD, N2DE when asked
about real, different calls) -- close enough to look plausible, wrong
enough to burn a real preference slot on a Form 605 if trusted.

This session confirmed the real, working path: `data.fcc.gov` (the
actual bulk-download host) answers fine. `www.fcc.gov` -- the
informational pages, including the real "Amateur Call Sign Systems"
reference table and `PUBACC_INTRO.pdf` -- returns a real, consistent
Akamai 403 in this environment. Two real files, downloaded live, not
synthetic: `l_amat.zip` (the complete license dump, ~197MB) and
`a_amat.zip` (pending applications, ~320MB).

## Real blocker #2: no schema doc, so cross-validate against live data instead

With the reference page blocked, the real `.dat` file schema (which
pipe-delimited field is the call sign, which is the status code, which
are the real dates) got derived by reading the actual live rows and
cross-checking against known, decades-stable public regulation (47 CFR
97.119), not assumed from memory alone.

The real proof this worked: the spec named one already-known fact --
**K0TC is taken, held by Ronald Dodge in Roseville, MN**. Pulling K0TC's
real record out of the live `HD.dat` gave back exactly that: status
`A` (active), holder name **RONALD E DODGE**. Exact match, first try,
against real government data -- the strongest real signal the parsing
was actually correct before trusting it with anything else.

A real bug got caught the same way: an early draft generated the
"Group B" 2x2 K/N/W-prefix format with only one prefix letter (same
shape as the simpler 1x2 group). Grepping the live data for the real
pattern turned up real calls like `KA1BA`/`KA1BB` -- two prefix
letters, not one. Fixed before the format table was trusted for real
candidate generation.

## What the real data actually said

Zero of the 10 hand-picked seed calls (K0TC, N0DE, W0RK, K0SB, AA0OS,
W0PEN, KC0DER, N0HEE, K0DET, W0TCO) are currently assignable. Four are
held by real active licensees. Six already have a real pending vanity
application against them -- `W0RK` alone has **20** real, distinct
pending requests on file, which says less about TCOS branding and more
about how many people just want the word "work."

The real available candidates all live in the pool the spec predicted
would be the exploitable one: never-issued 2x3 calls, no waiting
period at all because nobody has ever held them. Top real pick from
this run: **NE0HEE** -- confirmed, directly against the raw data, to
appear in neither the license file nor the pending-applications file.

## Still open, as of this entry

- Spencer's real current FCC license class isn't confirmed yet, which
  gates which format groups are even eligible. The tool takes it as a
  required input rather than assuming Extra.
- The real 605 filing itself hasn't happened. This post gets updated
  when it does, not rewritten after the fact to sound like it always
  knew the ending.

Real code, real commits, real PR:
[tcos-plan-private#40](https://github.com/Twin-Cities-Open-Systems/tcos-plan-private/pull/40).
