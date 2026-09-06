#!/usr/bin/env bash
# Shim: the real script is media/bin/deploy.sh, one for every operator.
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")/../bin" && pwd)/deploy.sh" spencer "$@"
