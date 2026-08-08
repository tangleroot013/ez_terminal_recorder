#!/usr/bin/env bash
set -euo pipefail

if ! command -v bats >/dev/null 2>&1; then
  echo "[error] bats not found -- install: sudo apt install bats  (or: npm install -g bats)"
  exit 1
fi

echo "[ok] running BATS suite"
bats "$(dirname "${BASH_SOURCE[0]}")"/*.bats
