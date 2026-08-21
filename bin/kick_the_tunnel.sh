#!/usr/bin/env bash
# Spencer Butler <inspector@tcos.us>
# tcos.us
# kick_the_tunnel.sh
# Cleanly terminates dangling tunnel handles, audits ports, and restarts cloudflared.

echo "=== [1/3] Hunting active cloudflared contexts ==="
# Force kill any stubborn binary blocks natively via signal 9
sudo pkill -9 cloudflared || echo "No direct binary process found."
pkill -9 -f "cloudflare_tunnel" || echo "No active npm wrapper processes found."

echo "=== [2/3] Verifying port 8080 state ==="
# Audit loop to ensure local forwarders drop cleanly before re-binding
if command -v ss &> /dev/null; then
    ss -lntp | grep :8080 || echo "Port 8080 is clear and available."
elif command -v netstat &> /dev/null; then
    netstat -ant | grep 8080 || echo "Port 8080 is clear and available."
fi

echo "=== [3/3] Relaunching edge network tunnel ==="
# Spawns a clean background instance and hooks it into your logging tree
nohup npm run cloudflare_tunnel > cloudflare_tunnel.log 2>&1 &

echo "Initialization command deployed. Run the following watch block to track live propagation:"
echo "watch -n 2 \"dig spencer.blog.tcos.us +short && curl -sIL https://tcos.us | head -n 5\""

