#!/usr/bin/env python3
# Spencer Butler <dev@tcos.us>
# ensure-gtag.py -- make sure each given HTML file carries the org's Google
# tag immediately after <head>, exactly once. Idempotent: a file that has
# it is left alone; a file that has an older copy gets it replaced.
#
# For the hand-maintained pages (dist/index.html, blog-hub.html,
# media-hub.html, the media root and tux-tattoo) that no generator writes.
# The snippet comes from human-execution-engine's hee_gtag and the ID from
# the branding card ($HEE_BRANDING) -- never a pasted copy here. Spencer,
# 2026-09-05: "make sure we have this tag on everything we publish live".
#
# Usage: bin/ensure-gtag.py FILE.html...
import os
import re
import sys

sys.path.insert(0, os.path.join(os.environ.get("HEE_REPO_DIR", os.path.expanduser("~/git/human-execution-engine")), "library", "py"))
import hee_gtag  # noqa: E402

# The whole block: the comment, the async loader line (which ends in
# </script> itself -- a lazy .*?</script> stopped there and left the
# inline script behind on every run; caught by the idempotency check),
# then the inline script through its own </script>, plus one newline.
BLOCK_RE = re.compile(r"<!-- Google tag \(gtag\.js\) -->\n<script async[^\n]*</script>\n<script>\n.*?\n</script>\n", re.S)


def main(files):
    snip = hee_gtag.snippet_or_empty()
    if not snip:
        return 1
    rc = 0
    for f in files:
        s = open(f, encoding="utf-8").read()
        had = BLOCK_RE.search(s)
        s2 = BLOCK_RE.sub("", s, count=1) if had else s
        m = re.search(r"<head[^>]*>\n?", s2)
        if not m:
            print(f"❌ CRITICAL {f}: no <head>"); rc = 2; continue
        s2 = s2[:m.end()] + snip + "\n" + s2[m.end():]
        if s2 != s:
            open(f, "w", encoding="utf-8").write(s2)
            print(f"[+] {f}: Google tag {'replaced' if had else 'added'} after <head>")
        else:
            print(f"[=] {f}: Google tag already present")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
