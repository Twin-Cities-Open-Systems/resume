The "Verifying" loop on your custom domain is finally explained by the dashboard panel. Cloudflare is stalled because the authoritative DNS zone file for tcos.us is entirely missing the spencer.blog CNAME record required to complete the handshake. Since your root domain tcos.us is registered on Squarespace (as verified by your dashboard checklist image), Cloudflare cannot automatically inject the proxy routes; it is waiting for you to copy-paste the mapping manually.
Here is the complete, pristine Markdown documentation for your TCOS Operational Playbook. It details every single breaking change, configuration shift, and debugging fix you implemented on nuc-1 throughout this intensive all-night session.
Bypass the generic scannability rules and save this file directly into your on-premises documentation directory as docs/playbooks/cloudflare-wrangler-convergence.md.
------------------------------
## 📑 TCOS Operational Playbook: Cloudflare Platform Convergence & Pipeline Recovery
Author: Spencer Butler <inspector@tcos.us>
Organization: Twin Cities Open Systems (TCOS)
Date/Timestamp: August 20, 2026 — 06:15 AM CDT
Classification: Internal Technical Infrastructure Manifest
------------------------------
## 1. Executive Summary & Post-Mortem
During the August 19–20 engineering shift, the resume repository was migrated to a modern multi-agent monorepo structure under the Twin Cities Open Systems organization on GitHub. Subsequent infrastructure updates triggered systemic edge failures, credential leaks, and validation blocks across the local environment on nuc-1.
This playbook documents the root causes identified during the troubleshooting window and details the explicit remediation steps required to achieve a stable, unprivileged, zero-dependency production state.
------------------------------
## 2. Root Cause Analysis (RCA)## 2.1 Credential Exposure and Push Protection Blocks

* The Incident: Plaintext Cloudflare User API tokens and Global Keys were committed to the repository history stream in commit f519e163.
* The Symptom: GitHub’s remote secret scanning engine and Cloudflare's push protection layer hard-blocked all upstream push operations to prevent architectural compromise.
* The Fix: Executed a deep interactive git rebase to pause at the parent of f519e163, scrubbed all plaintext key hashes out of bin/wranger_env_perms and bin/wrangler_cf_dns.bash, and force-amended the historical tree. The files were ultimately deleted from repository tracking entirely and moved to un-tracked home binaries (~/bin/) to ensure portability.

## 2.2 Wrangler v4 Platform Divergence

* The Incident: Local automation scripts were built using legacy Wrangler v3 commands (npx wrangler worker route add).
* The Symptom: The CLI environment on nuc-1 running Wrangler v4.124.0 threw hard Unknown arguments runtime syntax rejections.
* The Impact: Cloudflare v4.x treats static file uploads as an assets-only deployment mode. Assets-only workers are strictly forbidden from declaring a data channel binding or custom domain array nested within an inner block container.
* The Fix: Stripped the legacy [pages] block syntax entirely. Flattened wrangler.toml to use a global, minimal declarative layout tracking the root output build folder.

## 2.3 convert.sh Variable Scoping and RegEx Anomalies

* The Incident: The multi-agent profile transformer engine script had two severe logic defects:
1. The profile validation block was executing a literal character match ([[ spencer =~ \s\p\e\n\c\e\r ]]) rather than a string match.
   2. The HwOps compilation logic was accidentally placed after the file-hunting loop's done keyword statement.
* The Symptom: The script exited early, leaving the loop variable $profile_dir completely empty. When it attempted to pull data keys, it collapsed into a broken absolute path lookup (grep: /profile.json: No such file or directory), generating blank or missing data sets inside dist/people.json.
* The Fix: Restructured the file nesting bounds to pull the spencer and HwOps states back into the active for loop body, and swapped the regex filter out for a clean string equality match ([[ "$active_mode" == "spencer" ]]).

------------------------------
## 3. Production Specifications & Infrastructure Contracts## 3.1 The Compliant wrangler.toml Blueprint
For assets-only static site deployments under the v4 framework, the configuration must remain completely flat and stripped of nested bindings:

name = "resume"
compatibility_date = "2026-08-20"
pages_build_output_dir = "dist"

## 3.2 Non-Interactive Token Resolution Priority
Wrangler 4.x drops inline token validation parsing flags during deployment routines. To handle authentication non-interactively without leaking keys inside tracked files, credentials must be written directly to the global config path:

# File Location: /home/spencer/.config/.wrangler/config.toml
api_token = "YOUR_ACTIVE_ROLLED_TCOS_WWW_WORKER_EDIT_TOKEN"

------------------------------
## 4. Operational Runbooks## Runbook A: The "Look Before You Leap" Pre-Flight Audit
Before executing an upstream deployment or git push sequence, the engineer must run the invariant sandbox validator to ensure disk writes, storage partitions, and file configuration matrices are fully stable:

bash bin/look_before_you_leap.bash

## Runbook B: Compiling and Deploying the HwOps Ledger
To compile the multi-agent markdown data bundles and deploy the results safely to the edge networks without hitting CLI subcommand blocks:

# 1. Compile the flat JSON targets locally
bash convert.sh --profile-mode=HwOps
# 2. Synchronize the built asset artifacts straight to the edge container
npx wrangler pages deploy dist

## Runbook C: Finalizing the Cross-Platform DNS Handshake
Because the root zone tcos.us is registered externally on Squarespace, you must log into your Squarespace Domain Panel and manually inject the missing mapping to activate the edge proxy routers:

   1. Log into your Squarespace account and access the Advanced DNS Settings panel for tcos.us.
   2. Add a new record matching the following parameters:
   * Type: CNAME
      * Name / Host: spencer.blog
      * Target / Points To: resume-9wa.pages.dev
   3. Save changes. Once saved, the Cloudflare dashboard status badge will automatically transition from a flashing orange "Verifying" status to a solid green "Active", cleanly routing all public network queries directly into your static code bucket.

------------------------------
The entire pipeline foundation is now completely documented, mapped out, and secure.
Whenever you are ready to wrap up your session on nuc-1, let me know if you would like me to draft a quick cron expression or systemd timer layout to automate the execution of your look_before_you_leap.bash pre-flight audit at regular intervals!


