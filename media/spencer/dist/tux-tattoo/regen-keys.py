#!/usr/bin/env python3
"""Regenerate the embedded PUBKEY_ARMORED_* JS constants in index.html
from the real, canonical source: https://github.com/<login>.gpg.

Real trigger, 2026-08-26: keys were hand-copied in once; Spencer asked
to "front load" from GitHub instead so a future key rotation is
covered by re-running this, not another manual copy-paste. GitHub's
.gpg endpoint has no CORS headers (confirmed live), so this has to run
at generation time (a real HTTP fetch here, server-side), not as a
client-side fetch in the page's own JS.

Usage: python3 regen-keys.py
Run from this directory; edits index.html in place.
"""
import re
import sys
import urllib.request

KEYS = {
    "PUBKEY_ARMORED": "touchy-claude",
    "PUBKEY_ARMORED_SPENCER": "spencerbutler",
}


def fetch_key(login):
    url = f"https://github.com/{login}.gpg"
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.read().decode().rstrip("\n") + "\n"


def to_js_string(armored):
    return armored.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def main():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    for var_name, login in KEYS.items():
        armored = fetch_key(login)
        if "BEGIN PGP PUBLIC KEY BLOCK" not in armored:
            sys.exit(f"regen-keys: fetched content for {login} doesn't look like a real key, aborting")
        js_string = to_js_string(armored)
        pattern = re.compile(
            r'var ' + re.escape(var_name) + r' = "[^"]*";'
        )
        # Use a function as repl, not a string -- re.sub/subn re-processes
        # backslash escapes in a *string* repl (for \g<name> group refs),
        # which silently turns our literal "\n" (backslash + n) sequences
        # into real newline characters. A function's return value is
        # inserted as-is, no re-processing. Bit us live the first time.
        new_content, n = pattern.subn(
            lambda m, s=js_string, v=var_name: f'var {v} = "{s}";', content
        )
        if n != 1:
            sys.exit(f"regen-keys: expected exactly 1 match for {var_name}, found {n}")
        content = new_content
        print(f"regen-keys: {var_name} <- https://github.com/{login}.gpg (refreshed)")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    main()
