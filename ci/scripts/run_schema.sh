#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' 'ReceiptOS schema validation: existing schema and validator tests'
python -m pip install --disable-pip-version-check -e ".[dev]"
python -m pytest -q \
  tests/test_gcp_module_split_hardening.py \
  tests/test_gcp_readonly_audit_packet_schema.py \
  tests/test_gcp_readonly_packet_validator.py
