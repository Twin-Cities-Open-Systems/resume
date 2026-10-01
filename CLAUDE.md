# resume

Org governance is canonical in `human-execution-engine`'s
`prompts/PROMPTING_RULES.md`. It is delivered to every session by the
`SessionStart` hook installed from the `dotfiles` repo:

    make claude-hooks

It is deliberately **not** `@import`-ed here. Measured 2026-08-31, with
sentinel strings probed from real sessions:

| mechanism | resolves? |
|---|---|
| `@import` whose path is inside this repo | yes |
| `@import` whose path resolves outside this repo | **no** |
| `.claude/rules/` symlink pointing outside this repo | **no** |
| `@https://` or `@http://` URL | **no** |
| `SessionStart` hook | yes |

All three failures are **silent** -- they look like they worked. So an
import line here would be decoration, not delivery.

The hook also carries no assumption about where your checkouts live. It
honours `HEE_REPO_DIR`, so an operator using `~/projects/` or anything
else works without editing a repo.

If the org rules are not in `/context`, the hook is not installed.

<!-- Repo-specific guidance belongs below this line, never above it. -->

## The shared shell (tcos-app)

tcos-app owns the look of every TCOS web page (operator, 2026-10-01). This repo
serves two kinds of host, so `sh sync-shell.sh` copies tcos-app's `shell.manifest`
into both `media/shared/` (staged at the root of every `<who>.media` host) and
`dist/` (the blog and media hubs); CI fails when either copy drifts from tcos-app's
main. Never edit those copies. `media/shared/shell-theme.css` and the hub's inline
styles map their own token names onto the shell's, so the theme selector's named
themes repaint them; the theme key is the shell's `tc-theme`, and each page's
pre-paint script carries an old `tcos-theme` choice over once. The text size stays
this repo's own (`tcos-fontsize`). `media/shared/shell-toggles.js` adds the shell's
way-back pill to every media page.

A template change under `media/templates/` reaches the committed media pages only
when they are rebuilt; `media-item.py build` also re-renders each item's images,
so a markup-only change can be applied to the committed pages directly, as the
2026-10-01 shell change was.

`bin/deploy-pages.sh lab` rsyncs `dist/` into the lab share
(`$HEE_LAB_WWW/spencer-blog`), the same no-ssh path as `media/bin/deploy.sh`.
