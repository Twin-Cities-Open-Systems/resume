#!/usr/bin/env python3
# Spencer Butler <dev@tcos.us>
# render-blog.py -- render every profiles/<slug>/blog/*.md into a real Gold
# HTML page at dist/profiles/<slug>/blog/<post>.html, next to the .md it
# came from. Called by convert.sh after blog_manifest.json exists; adds an
# "html" field to each manifest entry pointing at the rendered page.
#
# Real trigger, Spencer, 2026-09-05: "we need to fix the blogs next, this
# is just raw markdown" -- https://spencer.blog.tcos.us/profiles/spencer/
# blog/001-why-didnt-you-use-dryrun.md was served as text/markdown,
# because index.html linked straight at the source file and nothing ever
# rendered it. resume#36 item 4 had already flagged the open decision.
#
# The renderer is NOT here. Gold's rule (.github profile/GLOSSARY.md):
# every surface's Gold code is ported from .github/bin/render-review.py
# directly, never hand-copied -- so this imports that file as a library
# and calls its render_file_page(). The checkout is found the org's way
# (~/git/.github, overridable with TCOS_GITHUB_DIR), never vendored.
#
# Usage: bin/render-blog.py [--check]   (run from the repo root)
#   --check   also run .github's check_render_review_compliance.py on
#             every page produced and fail if any page fails
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

GITHUB_DIR = Path(os.environ.get("TCOS_GITHUB_DIR", Path.home() / "git" / ".github"))
RENDER = GITHUB_DIR / "bin" / "render-review.py"
CHECK = GITHUB_DIR / "bin" / "check_render_review_compliance.py"
DIST = Path("dist")
MANIFEST = DIST / "blog_manifest.json"


def load_renderer():
    if not RENDER.is_file():
        sys.exit(f"render-blog: {RENDER} not found -- check out Twin-Cities-Open-Systems/.github under ~/git "
                 f"or set TCOS_GITHUB_DIR")
    spec = importlib.util.spec_from_file_location("render_review", RENDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "render_file_page"):
        sys.exit("render-blog: this render-review.py has no render_file_page() -- update the .github checkout")
    return mod


def people_by_slug():
    return {p["slug"]: p for p in json.loads((DIST / "people.json").read_text())}


def place_gold_favicons():
    """Gold's template loads /favicon.ico and /assets/favicon-{16,32,180}.png
    and says to put files at those paths rather than edit page HTML. This
    site keeps its icons in dist/icons/, so the build provides them at
    Gold's paths too -- a build step, never a hand copy."""
    src = {"favicon-16.png": "favicon-16.png", "favicon-32.png": "favicon-32.png",
           "favicon-180.png": "apple-touch-icon.png"}
    (DIST / "assets").mkdir(parents=True, exist_ok=True)
    for dst, name in src.items():
        f = DIST / "icons" / name
        if f.is_file():
            (DIST / "assets" / dst).write_bytes(f.read_bytes())


def main(argv):
    place_gold_favicons()
    if not MANIFEST.is_file():
        sys.exit("render-blog: dist/blog_manifest.json missing -- run convert.sh first")
    rr = load_renderer()
    people = people_by_slug()
    posts = json.loads(MANIFEST.read_text())
    generated_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    repo = str(Path(".").resolve())
    produced = []
    for post in posts:
        src = Path(post["path"])                       # profiles/<slug>/blog/<post>.md
        slug = src.parts[1]
        host = people.get(slug, {}).get("public_dns") or "blog.tcos.us"
        out = DIST / src.with_suffix(".html")
        out.parent.mkdir(parents=True, exist_ok=True)
        page = rr.render_file_page(
            repo, str(src),
            title=post["title"],
            status_class="browse", status_label="post",
            generated_iso=generated_iso,
            og_description=f"{post['title']} -- {slug}'s blog, {post['date']}.",
            og_url=f"https://{host}/{out.relative_to(DIST)}",
            site_name=host,
            active_tab="pretty",
            github_url=f"https://github.com/{rr.GITHUB_ORG}/resume/blob/main/{src}",
        )
        out.write_text(page, encoding="utf-8")
        post["html"] = str(out.relative_to(DIST))
        produced.append(out)
        print(f"  [+] {out}")
    MANIFEST.write_text(json.dumps(posts, indent=0).replace("\n{", "{") + "\n")
    print(f"  [i] {len(produced)} post(s) rendered through {RENDER}")
    if "--check" in argv:
        r = subprocess.run([sys.executable, str(CHECK), *map(str, produced)])
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
