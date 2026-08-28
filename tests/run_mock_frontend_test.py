#!/usr/bin/env python3
# ==============================================================================
# TCOS Tooling Ecosystem — Project #5: Frontend Data Binding Test Suite
# Script Type: Portable Python3 Userland Verification Utility
# Invariant: Enforces strict data contract validation across schema mappings
# ==============================================================================
import os
import sys
import json
import re

def execute_simulation_pass():
    profile_path = "profiles/spencer/profile.json"
    html_path = "dist/index.html"
    manifest_path = "dist/blog_manifest.json"

    if not (os.path.exists(profile_path) and os.path.exists(html_path) and os.path.exists(manifest_path)):
        print("[-] Simulation Failure: Authorization layout components are missing from workspace.")
        sys.exit(1)

    print("[+] Component footprint verified. Validating master core JSON schemas...")
    try:
        with open(profile_path, "r") as f:
            profile_data = json.load(f)
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
    except Exception as e:
        print(f"[-] Schema Failure: Parsing error encountered -> {str(e)}")
        sys.exit(1)

    print("[+] Core profiles parsed cleanly. Verifying specific language mode bindings...")
    payloads = profile_data.get("language_profiles", {}).get("payloads", {})
    required_modes = ["professional", "spencer", "ninja", "pirate", "HwOps"]
    
    for mode in required_modes:
        if mode not in payloads:
            print(f"[-] Binding Failure: Required language payload [{mode}] is missing from registry.")
            sys.exit(1)

    print("[+] Mode layout verified. Inspecting front-end runtime profile rendering...")
    with open(html_path, "r") as f:
        html_content = f.read()

    # Real design change, 2026-08-28 (Spencer, direct: "all of the dropdown
    # for lang spencer, hwops, etc is not to be there"): modes are no longer
    # statically injected as <select><option value="mode"> markup -- the
    # public switcher UI was removed. The page still renders whichever mode
    # profile.json's own active_default names, purely via runtime JS
    # (coreProfiles[mode] lookup against the fetched profile.json), so what
    # this test can actually still verify is that the dynamic-rendering
    # machinery is present, not any particular mode's static markup.
    # Real design change, 2026-08-28 (Spencer, direct: "ditch all the
    # persona shit"): no more coreProfiles/active_default multi-mode
    # selection either -- one real, fixed identity per person, sourced
    # directly from profile.json's own "professional" payload.
    required_runtime_hooks = ["payloads.professional", "profile-title", "profile-paradigm"]
    for hook in required_runtime_hooks:
        if hook not in html_content:
            print(f"[-] DOM Binding Failure: Front-end is missing real runtime hook [{hook}].")
            sys.exit(1)

    print("[+] Select elements mapped. Validating responsive dark-mode styling variables...")
    required_style_tokens = ["--bg", "--pane-bg", "--text", "--accent", "--border", "--muted"]
    for token in required_style_tokens:
        if token not in html_content:
            print(f"[-] UI Token Failure: Element container is missing theme variable definition: [{token}].")
            sys.exit(1)

    print("[+] Testing data model array binding vectors across stream entries...")
    # Real design change, 2026-08-26 (Spencer, direct: "keep json to a
    # minimum ... too much bloat to parse"): blog_manifest.json used to
    # embed every post's full text, 5 persona variants each -- retired in
    # favor of a thin index (slug/date/title/path); real content lives in
    # profiles/<slug>/blog/*.md, fetched on demand. This test still checked
    # for the retired localized_content shape, which no longer exists on
    # any real post -- never updated after that redesign landed. Checking
    # the real, current required fields instead.
    required_post_fields = ["slug", "date", "title", "path"]
    for post in manifest_data:
        for field in required_post_fields:
            if field not in post:
                print(f"[-] Stream Manifest Failure: Post [{post.get('slug', '?')}] is missing required field [{field}].")
                sys.exit(1)

    print("[+] All verification passes successfully completed. Integration is stable.")
    sys.exit(0)

if __name__ == "__main__":
    execute_simulation_pass()

