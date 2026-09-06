#!/usr/bin/env python3
# Spencer Butler <dev@tcos.us>
# render-resume.py
# Renders a profile's resume.md as a Gold page (render-review.py's
# render_file_page) with a full Open Graph set and its own social card from
# meme-factory's tile generator -- the same treatment posts and items get.
#
#   bin/render-resume.py <slug> <resume.md> <out.html>
#
# Until 2026-09-06 the resume was pandoc's standalone HTML: a <title> and
# nothing else, which hee check-og showed the moment it moved onto the
# media host. Operator: "how did that slip through?" -- no gate looked at
# it. media-item audit now requires the Open Graph set on every page a
# media host serves; this is what makes the resume pass it.
from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
TILE_PY = Path(os.environ.get("MEME_FACTORY_TILE", Path.home() / "git/fleet-ops/tools/meme-factory/tile/tile.py"))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        sys.exit("usage: bin/render-resume.py <slug> <resume.md> <out.html>")
    slug, src, out = argv[0], Path(argv[1]), Path(argv[2])
    rb = load("render_blog", REPO / "bin" / "render-blog.py")
    rr = rb.load_renderer()
    profile = json.loads((REPO / "profiles" / slug / "profile.json").read_text())
    entity = profile["meta"]["entity"]
    # from the profile, the SSoT -- never dist/people.json, which convert.sh
    # is still writing when this runs inside its loop (worktree build, 2026-09-06)
    media_host = profile["meta"].get("media_routing") or "media.tcos.us"
    title = f"{entity} Resume"

    body = subprocess.run(["pandoc", str(src), "-f", "markdown+autolink_bare_uris", "-t", "html5"],
                          capture_output=True, text=True, check=True).stdout

    card_url = None
    if TILE_PY.is_file():
        sys.path.insert(0, str(TILE_PY.parent)); tile = importlib.import_module("tile")
        words = [w for w in re.split(r"[^A-Za-z0-9]+", entity) if w]
        card = out.with_suffix(".og.jpg")
        try:
            role = profile["language_profiles"]["payloads"]["professional"]["title"]
        except KeyError:
            role = "resume"
        tile.render_job({"output": str(card), "card": True, "palette": tile.PALETTES["teal"],
                         "seed": f"{slug}-resume", "title": entity, "subtitle": "(resume)", "tagline": role,
                         "eyebrow": media_host, "text": "".join(w[0] for w in words[:2]).upper()})
        card_url = f"https://{media_host}/resume.og.jpg"
    else:
        print(f"  WARN: meme-factory tile generator not at {TILE_PY}; resume ships with no og:image", file=sys.stderr)

    # the description is the person's title from their own profile, never
    # the resume's first paragraph (that is the contact block)
    try:
        role = profile["language_profiles"]["payloads"]["professional"]["title"]
        description = f"{entity}, {role} -- resume: work history, contracts and contact, at Twin Cities Open Systems."
    except KeyError:
        description = f"{entity}'s resume at Twin Cities Open Systems."
    page = rr.render_file_page(
        str(REPO), str(src.relative_to(REPO)) if src.is_relative_to(REPO) else str(src),
        title=title, status_class="browse", status_label="resume",
        generated_iso=rb.datetime.now(rb.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        og_description=description, og_url=f"https://{media_host}/resume.html",
        pretty_html=body, site_name=media_host, active_tab="pretty",
        github_url=f"https://github.com/{rr.GITHUB_ORG}/resume/blob/main/{src.relative_to(REPO) if src.is_relative_to(REPO) else src}",
        label_url="/", og_image=card_url, og_image_alt=title,
        extra_head=rb.gtag_snippet())
    out.write_text(page, encoding="utf-8")
    print(f"  [+] {out}" + (f" + {card.name}" if card_url else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
