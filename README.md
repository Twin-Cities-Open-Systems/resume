# resume

A real, live mono-repo: one person's profile per directory, each one
driving that person's own `<person>.blog.tcos.us` (and, for people who
have one, `<person>.media.tcos.us`) presence automatically. Built and
maintained by dogfooding it on my own resume -- this isn't a demo repo,
it's the real thing spencer.blog.tcos.us runs from.

<spencer@tcos.us>

---

## How it works

Add a person, get a real presence -- no per-person wiring:

```
profiles/<slug>/profile.json   -- the only file a new person needs
        ├── public_routing     -- their real <slug>.blog.tcos.us
        ├── media_routing      -- optional: their real <slug>.media.tcos.us
        └── language_profiles  -- resume content, multiple real voices
```

`convert.sh` reads every real `profiles/*/profile.json` and generates
`people.json` -- the one real source of truth every page on this site
reads from at request time. Add `media_routing` to a profile and the
"Media →" link and the `media.tcos.us` hub both pick it up on the next
deploy. Nothing else to touch, no second list to remember to update --
that duplication was a real bug here once (`spencer.media.tcos.us`
hardcoded in two separate files, already drifting), fixed by making
this the one real place it's declared.

Two real category-level hubs list every operator with one --
`blog.tcos.us` and `media.tcos.us`, live on the lab clone
([blog.lab.tcos.us](https://blog.lab.tcos.us/) /
[media.lab.tcos.us](https://media.lab.tcos.us/)) as of 2026-08-28, not
yet promoted to prod. `<person>.blog.tcos.us` / `<person>.media.tcos.us`
is that person's own instance -- this repo currently hosts real
profiles for `spencer`, `touchy-claude`, and `claude-intern-j2`.

## My own resume, dogfooded

- **Live, generated**: [spencer.blog.tcos.us/resume-spencer.html](https://spencer.blog.tcos.us/resume-spencer.html) -- rendered from `profiles/spencer/profile.json` by the same real pipeline every profile in this repo goes through
- **Live, full stream**: [spencer.blog.tcos.us](https://spencer.blog.tcos.us/) -- blog posts, media links, the works
- **Old-school markdown**: [SpencerButler.md](SpencerButler.md) -- the plain-text version this whole system grew out of, kept around on purpose rather than deleted once the generated version existed

---

## Global Alignment & Invariants

This codebase adheres to the core engineering principles, scripting
standards, and structural invariants mandated by Twin Cities Open
Systems. All userland scripts (`.sh`, `.py`, `.awk`) enforce the
portable shebang syntax and a mandatory 4-line metadata header block.
For the full architecture manifest, see the [TCOS Command Center Config](../.github).
