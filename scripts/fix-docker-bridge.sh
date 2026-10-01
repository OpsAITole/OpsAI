#!/usr/bin/env bash
# Allow container-to-container traffic on Compose bridges.
# Some hosts mix iptables-nft/legacy in ways that drop same-bridge FORWARD traffic.
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found" >&2
  exit 1
fi

if ! command -v iptables >/dev/null 2>&1; then
  echo "iptables not found; skipping bridge fix" >&2
  exit 0
fi

# Broad local-dev allow for private Docker ranges (idempotent insert check)
RULE_SPEC=(-s 172.16.0.0/12 -d 172.16.0.0/12 -j ACCEPT)
if ! sudo iptables -C DOCKER-USER "${RULE_SPEC[@]}" 2>/dev/null; then
  sudo iptables -I DOCKER-USER "${RULE_SPEC[@]}"
  echo "Inserted DOCKER-USER allow for 172.16.0.0/12"
else
  echo "DOCKER-USER allow for 172.16.0.0/12 already present"
fi

# Prefer ACCEPT on legacy FORWARD if that table is active
if command -v iptables-legacy >/dev/null 2>&1; then
  sudo iptables-legacy -P FORWARD ACCEPT 2>/dev/null || true
fi

echo "Docker bridge forwarding check complete."
