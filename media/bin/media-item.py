#!/usr/bin/env python3
# Spencer Butler <dev@tcos.us>
# media-item.py -- build one <oper>.media.tcos.us item (a gallery of signed
# files with an EXIF detail page) from a Card-shaped manifest, in the exact
# design of the first real item, tux-tattoo: every file's bytes inlined so
# the page verifies the real detached GPG signature over them in the
# viewer's browser; an EXIF badge per file into exif.html?id=<stem> with
# the complete exiftool output embedded at build time; the media shell
# (shell-theme.css / shell-toggles.js / shell-freshness.js); full Open
# Graph on both pages.
#
# Operator, 2026-09-05: "let's look at the exif for spencer.media.tcos.us/
# tux-tattoo/ and replicate this design (this still needs to be converted
# to Kind: Card, but for now let's just use the same tools)". So: the
# markup, CSS and JS are tux-tattoo's, lifted into media/templates/ with
# only the item-specific strings parametrized; the manifest is already a
# kind: Card so the conversion is done rather than pending.
#
# The tools: hee-exif embed-exif (EXIF_DATA), hee-exif regen-pubkey
# (PUBKEY_ARMORED from github.com/<login>.gpg), and the .asc files
# hee-exif gpg-sign wrote beside each file (SIGNATURES). Found at
# $HEE_REPO_DIR or ~/git/human-execution-engine, never vendored.
#
# Usage:
#   media/bin/media-item.py build <item-dir>        # <item-dir>/item.card.v1.yaml -> index.html + exif.html
#   media/bin/media-item.py build <item-dir> --no-network   # skip regen-pubkey (offline check)
import base64
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from string import Template

import yaml
from PIL import Image

HERE = Path(__file__).resolve().parent
# The org's Google tag, one source for every generator (hee_gtag in
# human-execution-engine); the ID from the branding card via $HEE_BRANDING.
# Immediately after <head> on both pages -- tcos-www#52.
sys.path.insert(0, str(Path(os.environ.get("HEE_REPO_DIR", Path.home() / "git" / "human-execution-engine")) / "library" / "py"))
try:
    import hee_gtag
    GTAG = hee_gtag.snippet_or_empty()
except ImportError:
    print("⚠️  WARNING hee_gtag not importable -- media pages ship without the Google tag", file=sys.stderr); GTAG = ""
TEMPLATES = HERE.parent / "templates"
HEE_EXIF = Path(os.environ.get("HEE_REPO_DIR", Path.home() / "git" / "human-execution-engine")) / "tooling" / "bin" / "hee-exif"
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")


def esc(s):
    return html.escape(str(s), quote=True)


def data_uri(path):
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}[path.suffix.lower()]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


# Inline a file's bytes only up to this size. tux-tattoo inlined everything
# and its photos are small; a 1.9 MB GIF becomes a 2.5 MB data: URI, which
# browsers cap at about 2 MB -- measured 2026-09-05: the GIF was in the
# page byte-for-byte and the operator could not see it. Larger files are
# referenced by URL and the GPG check fetches them instead.
INLINE_MAX = 1024 * 1024


def figure(item, item_dir, signatures):
    f = item_dir / item["file"]
    stem = f.stem
    src = data_uri(f) if f.stat().st_size <= INLINE_MAX else esc(f.name)
    exif_badge = (f'<a class="evidence-hover exif-badge" tabindex="0" href="exif.html?id={esc(stem)}" target="_blank" rel="noopener">'
                  f'EXIF: {esc(item.get("exif_label", "real, embedded"))}</a>')
    gpg = (f'<span class="gpg-badge" data-photo="{esc(stem)}" tabindex="0"><span class="gpg-dot"></span><span class="gpg-text">verifying…</span></span>'
           if stem in signatures else '<span class="exif-badge none">unsigned</span>')
    return f'''    <figure class="photo" data-tag="{esc(item.get("tag", "item"))}" data-date="{esc(item.get("date", ""))}">
      <img id="img-{esc(stem)}" src="{src}" alt="{esc(item["title"])}" loading="lazy" tabindex="0">
      <figcaption>
        <span class="ft">{esc(item["title"])}</span>
        <span class="fc">{esc(item.get("caption", ""))}</span>
        <span class="fmeta">{exif_badge}</span>
        <span class="fmeta">{gpg}</span>
      </figcaption>
    </figure>'''


def build(item_dir, network=True):
    item_dir = Path(item_dir).resolve()
    card_path = item_dir / "item.card.v1.yaml"
    if not card_path.is_file():
        sys.exit(f"media-item: {card_path} missing")
    card = yaml.safe_load(card_path.read_text())
    if card.get("apiVersion") != "hee/v1" or card.get("kind") != "Card":
        sys.exit(f"media-item: {card_path} is not an apiVersion hee/v1 kind Card")
    spec = card["spec"]
    slug = item_dir.name
    if spec.get("consent") not in (None, "approved"):
        print(f"⚠️  WARNING  {slug}: consent is {spec['consent']!r} -- build for lab review only; deploy.sh promote will refuse")
    host = spec["host"]                                  # e.g. spencer.media.tcos.us
    host_short = host.split(".tcos.us")[0]              # spencer.media
    url = f"https://{host}/{slug}/"
    items = spec["items"]
    stems = {}
    for it in items:
        if not (item_dir / it["file"]).is_file():
            sys.exit(f"media-item: {it['file']} named in the card is not in {item_dir}")
        # the file stem is the id everywhere -- exif.html?id=, SIGNATURES,
        # EXIF_DATA, the <img id> -- so two files may not share one
        # (bofh.gif + bofh.jpg would silently drop one from every table)
        st = Path(it["file"]).stem
        if st in stems:
            sys.exit(f"media-item: {it['file']} and {stems[st]} share the stem {st!r}; rename one")
        stems[st] = it["file"]

    # signatures: <file>.asc beside each file, as hee-exif gpg-sign writes them
    signatures = {}
    for it in items:
        asc = item_dir / (it["file"] + ".asc")
        if asc.is_file():
            signatures[Path(it["file"]).stem] = asc.read_text()

    # The og:image is the content, never a generic banner. Operator,
    # 2026-09-05: "make sure that the og image is always pertinent to the
    # content. for this mn2600, og gif should be used." So it must be one
    # of the item's own files; default is the first item.
    og_name = spec.get("og_image", items[0]["file"])
    if og_name not in {it["file"] for it in items}:
        sys.exit(f"media-item: og_image {og_name!r} is not one of this item's files -- the preview must show the content itself")
    og_file = item_dir / og_name
    with Image.open(og_file) as im:
        og_w, og_h = im.size
    stats = ""
    if spec.get("stats"):
        stats = '  <div class="stat-row">\n' + "\n".join(
            f'    <div class="stat"><div class="n">{esc(s["n"])}</div><div class="l">{esc(s["l"])}</div></div>' for s in spec["stats"]) + "\n  </div>\n"
    credit = spec.get("credit", {})
    credit_html = f'    <span class="headline">{credit.get("headline_html") or esc(credit.get("headline", ""))}</span>\n'
    for note in credit.get("notes", []):
        credit_html += f'    <span class="note">{note}</span>\n'
    tags = {it.get("tag", "item"): it.get("tag", "item").replace("-", " ").title() for it in items}
    tags.update(spec.get("tag_labels", {}))
    group_toolbar = ""
    if len(tags) > 1:
        group_toolbar = '''  <div class="group-toolbar" role="group" aria-label="Group items">
    <span class="gt-label">Group:</span>
    <button type="button" class="gt-btn active" data-group="none">None</button>
    <button type="button" class="gt-btn" data-group="date">Date</button>
    <button type="button" class="gt-btn" data-group="tag">Kind</button>
  </div>
'''
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    signer = spec.get("signer", {})
    attester = spec.get("attester", {})
    values = dict(
        TITLE=esc(spec["title"]), OWNER=esc(spec.get("owner", "")), DESCRIPTION=esc(spec["description"]),
        HOST=esc(host), HOST_SHORT=esc(host_short), SLUG=esc(slug), OG_URL=esc(url), OG_URL_EXIF=esc(url + "exif.html"),
        OG_IMAGE=esc(f"https://{host}/{slug}/{og_file.name}"), OG_IMAGE_ALT=esc(spec.get("og_image_alt", spec["title"])),
        OG_IMAGE_W=og_w, OG_IMAGE_H=og_h,
        EYEBROW=esc(spec.get("eyebrow", spec["title"].lower())), SUB=spec.get("sub_html") or esc(spec.get("sub", spec["description"])),
        STATS=stats, CREDIT=credit_html, GENERATED=generated,
        SOURCE_URL=esc(spec.get("source_url", f"https://github.com/Twin-Cities-Open-Systems/resume/blob/main/media/{host.split('.')[0]}/dist/{slug}/item.card.v1.yaml")),
        SOURCE_LABEL=esc(spec.get("source_label", "item.card.v1.yaml")),
        GROUP_TOOLBAR=group_toolbar,
        FIGURES="\n".join(figure(it, item_dir, signatures) for it in items),
        FOOTER=spec.get("footer_html") or esc(spec.get("footer", "")),
        OPENPGP_SRC=esc(spec.get("openpgp_src", "/openpgp.min.js")),
        SIGNER_LABEL=esc(signer.get("label", signer.get("github_login", "signer"))),
        ATTESTER_LABEL=esc(attester.get("label", "")),
        TAG_LABELS_JSON=json.dumps(tags),
        GTAG=GTAG.replace("$", "$$"),
    )
    index = Template((TEMPLATES / "item-index.html.tmpl").read_text()).substitute(values)
    index = index.replace("var SIGNATURES = {};", "var SIGNATURES = " + json.dumps(signatures) + ";")
    (item_dir / "index.html").write_text(index)
    exif_page = Template((TEMPLATES / "item-exif.html.tmpl").read_text()).substitute(values)
    (item_dir / "exif.html").write_text(exif_page)
    print(f"[+] {item_dir / 'index.html'} ({len(items)} item(s), {len(signatures)} signed)")

    # the org's tools fill the two data vars
    exts = ",".join(sorted({Path(it["file"]).suffix.lstrip(".").lower() for it in items}))
    subprocess.run([str(HEE_EXIF), "embed-exif", str(item_dir / "exif.html"), "EXIF_DATA", str(item_dir), "--ext", exts], check=True)
    if network and signer.get("github_login"):
        subprocess.run([str(HEE_EXIF), "regen-pubkey", str(item_dir / "index.html"), "PUBKEY_ARMORED", signer["github_login"]], check=True)
    if network and attester.get("github_login"):
        subprocess.run([str(HEE_EXIF), "regen-pubkey", str(item_dir / "index.html"), "PUBKEY_ARMORED_SPENCER", attester["github_login"]], check=True)

    # the media root lists every item; add this one if it is not there
    root = item_dir.parent / "index.html"
    if root.is_file() and f'href="/{slug}"' not in root.read_text():
        li = (f'    <li>\n      <img class="item-icon" src="/icons/favicon-32.png" alt="">\n      <div>\n'
              f'        <a href="/{esc(slug)}">{esc(spec["title"])}</a>\n        <p>{esc(spec["description"])}</p>\n      </div>\n    </li>\n')
        r = root.read_text()
        r = r.replace("  </ul>\n  <p class=\"note\">", li + "  </ul>\n  <p class=\"note\">", 1)
        root.write_text(r)
        print(f"[+] listed on {root}")
    return 0


def main(argv):
    if len(argv) < 2 or argv[0] != "build":
        print(__doc__ or "usage: media-item.py build <item-dir> [--no-network]"); return 2
    return build(argv[1], network="--no-network" not in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
