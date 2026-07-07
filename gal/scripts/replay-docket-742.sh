#!/usr/bin/env bash
set -euo pipefail

# Docket 742-Omega replay command
# Authority: false
# Requires raw CSV exports to be available under replay_court/exports/.

python3 replay_court/process.py

sha256sum \
  replay_court/merged/jay_unified_ledger.csv \
  replay_court/receipts/replay_execution_report_v1.json \
  replay_court/receipts/receipt_manifest.json \
  replay_court/graphs/cross_wallet_graph.png \
  replay_court/graphs/adjacency.csv
