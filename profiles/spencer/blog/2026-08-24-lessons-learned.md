# Lessons Learned -- 2026-08-24 session

First pass, general -- meant to be tweaked/expanded later, not a final writeup.

## What shipped

- Real PVE lab buildout: 0 containers to 8 (bastion, DNS, HAProxy, dogfood,
  container-factory, deploy pipeline, thesis-engine, view), all via API,
  no SSH dependency.
- Org-wide CI/CD hardening pass: found and fixed real shellcheck bugs
  blocking `main` on multiple repos, plus a real `mode=warn` exit-code
  bug in `hee-lint` that was silently blocking every commit for anyone
  with the pre-commit hook installed.
- Formalized 0-token tooling (`hee-quota`, `hee-filter`, `hee-publish`,
  `hee-gen-manpages`) so routine work stops costing LLM reasoning budget.
- Real security incident response: caught a live secret leaking into a
  chat relay before it went further, verified a disputed GPG fingerprint
  independently rather than taking either side's word for it.

## Real lessons

- Cross-session coordination works, but costs real approval-gate latency
  -- worth designing around, not just tolerating.
- "Mode=warn" needs an actual test, not just a label -- the hee-lint bug
  proved a tool can claim non-blocking behavior while still blocking.
- Claude usage budget is a real, finite resource now, same as any other
  infra constraint -- the fallback-tier planning (README's Continuity
  section, HEE#365) exists because of this, not hypothetically.

## Skills exercised this session

See `profile.json`'s `badges.session_2026_08_24` for the short list --
kept there so it stays one source of truth instead of drifting from
this post.
