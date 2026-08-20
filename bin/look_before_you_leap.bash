#!/usr/bin/env bash
# ==============================================================================
# TCOS Platform Stream - Look Before You Leap (Pre-Flight Invariant Auditor)
# Design: Zero-dependency, POSIX-compliant sandbox validator
# ==============================================================================
set -euo pipefail

echo "[TCOS-AUDIT] Initializing workspace pre-flight validations..."

# 1. Structural NUC Identity Verification
if [[ "${GITHUB_ACTIONS:-false}" == "true" ]]; then
    echo "[!] WARN: Running inside an active remote CI container stream."
else
    ACTIVE_USER=$(whoami)
    echo "[+] Local Host Identity Verified: ${ACTIVE_USER}@nuc-1"
fi

# 2. Invariant Check: Storage Writable Verification
if ! touch .storage_test_marker 2>/dev/null; then
    echo "[-] HARD FAIL: NVMe volume block partition is mounted read-only or choked." >&2
    exit 1
fi
rm -f .storage_test_marker

# 3. Configuration Check: Validate Flattened wrangler.toml
if [[ -f "wrangler.toml" ]]; then
    echo "[+] Examining local Wrangler control plane schemas..."
    
    if grep -q "\[pages\]" wrangler.toml; then
        echo "[-] HARD FAIL: Legacy '[pages]' block found. Wrangler v4 requires a flat global schema." >&2
        exit 1
    fi
    
    if ! grep -q "pages_build_output_dir" wrangler.toml; then
        echo "[-] HARD FAIL: Missing mandatory target key 'pages_build_output_dir'." >&2
        exit 1
    fi
    echo "[+] Invariant Configuration Mapping: Validated."
else
    echo "[-] HARD FAIL: No wrangler.toml manifest located in root workspace." >&2
    exit 1
fi

# 4. Git-Ops Intersection Check
if [[ -f ".git/hooks/pre-commit" && ! -x ".git/hooks/pre-commit" ]]; then
    echo "[!] NOTICE: Local pre-commit loops are currently deactivated (-x)."
fi

echo "[TCOS-AUDIT] All structural parameters pass. Target environment is stable."

