#!/usr/bin/env python3
"""
ReplayOS unified CLI — thin front-end.

Exit codes (stable contract):
  0  Success
  1  Verification failed (including gatekeeper refusal)
  2  CLI / configuration / load error
  3  Adapter, publisher, or anchor execution failed
  4  Unexpected internal error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gatekeeper import GatekeeperError
from manifest_schema import ArtifactVerificationStatus
from orchestrator import CLIOrchestrator, OrchestratorConfig


def cmd_verify(args: argparse.Namespace) -> int:
    orch = CLIOrchestrator(OrchestratorConfig(strict=True))
    try:
        result = orch.verify(
            Path(args.manifest),
            Path(args.artifacts_root) if args.artifacts_root else None,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        return 4

    if args.json:
        print(json.dumps({
            "valid": result.valid,
            "integrity_ok": result.integrity_ok,
            "artifacts_ok": result.artifacts_ok,
            "errors": list(result.errors),
            "warnings": list(result.warnings),
            "artifact_checks": [
                {"uri": c.uri, "status": c.status.value, "message": c.message}
                for c in result.artifact_checks
            ],
        }, indent=2, sort_keys=True))
    else:
        print(f"Integrity: {'PASS' if result.integrity_ok else 'FAIL'}")
        print(f"Artifacts: {'PASS' if result.artifacts_ok else 'FAIL'}")
        for c in result.artifact_checks:
            mark = "✓" if c.status == ArtifactVerificationStatus.PASS else "✗"
            print(f"  {mark} [{c.status.value}] {c.uri}")
            if c.message:
                print(f"      → {c.message}")
    return 0 if result.valid else 1


def cmd_attest(args: argparse.Namespace) -> int:
    orch = CLIOrchestrator(OrchestratorConfig(
        output_dir=Path(args.output_dir),
        signer_id=args.signer_id,
        strict=True,
    ))
    orch.register_defaults()

    try:
        _, results = orch.attest(
            Path(args.manifest),
            Path(args.artifacts_root) if args.artifacts_root else None,
            adapter_names=args.adapter,
            anchor_names=args.anchor,
        )
    except GatekeeperError as e:
        print(f"🛑 {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        return 4

    any_success = any(r.success for r in results)
    if args.json:
        print(json.dumps({
            "results": [
                {
                    "adapter": r.adapter_name,
                    "success": r.success,
                    "envelope_digest": r.envelope_digest,
                    "reference": r.reference,
                    "errors": r.errors,
                }
                for r in results
            ],
        }, indent=2, sort_keys=True))
    else:
        for r in results:
            mark = "✓" if r.success else "✗"
            dig = r.envelope_digest[:24] + "…" if r.envelope_digest else "—"
            print(f"{mark} {r.adapter_name}: {dig}")
            if r.reference:
                print(f"    → {r.reference}")
            for err in r.errors:
                print(f"    error: {err}")

    if not results:
        return 2
    return 0 if any_success else 3


def cmd_interop(args: argparse.Namespace) -> int:
    orch = CLIOrchestrator()
    try:
        vector = orch.interop(Path(args.fixtures_dir))
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        return 4

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    canonical = json.dumps(vector, indent=2, sort_keys=True, ensure_ascii=False)
    out.write_text(canonical + "\n", encoding="utf-8")

    if not args.quiet:
        print(f"Interop parity vector written to {out}")
        print(f"  cases: {len(vector.get('cases', []))}")
        for c in vector.get("cases", []):
            status = "PASS" if c.get("valid") else "FAIL"
            print(f"  [{status}] {c.get('kind')}/{c.get('case')}")
    return 0


def cmd_capabilities(args: argparse.Namespace) -> int:
    orch = CLIOrchestrator(OrchestratorConfig(output_dir=Path("attestations")))
    orch.register_defaults()
    caps = orch.list_capabilities()
    if args.json:
        print(json.dumps([
            {"kind": c.kind, "name": c.name, "description": c.description}
            for c in caps
        ], indent=2, sort_keys=True))
    else:
        by_kind: dict = {}
        for c in caps:
            by_kind.setdefault(c.kind, []).append(c)
        for kind in sorted(by_kind):
            print(f"{kind}:")
            for c in by_kind[kind]:
                desc = f" — {c.description}" if c.description else ""
                print(f"  {c.name}{desc}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="replayos",
        description="ReplayOS verification, attestation, and interop CLI",
    )
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("verify", help="Verify a release manifest → VerificationResult")
    v.add_argument("--manifest", required=True)
    v.add_argument("--artifacts-root", default=None)
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_verify)

    a = sub.add_parser("attest", help="Verify, gatekeep, then attest")
    a.add_argument("--manifest", required=True)
    a.add_argument("--artifacts-root", default=None)
    a.add_argument("--output-dir", default="attestations")
    a.add_argument("--signer-id", default="cli:default")
    a.add_argument("--adapter", action="append", help="Adapter name (repeatable)")
    a.add_argument("--anchor", action="append", help="Anchor name (repeatable)")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_attest)

    i = sub.add_parser("interop", help="Run fixture corpus → parity vector")
    i.add_argument("--fixtures-dir", default="tests/fixtures")
    i.add_argument("--output", default="tests/interop/parity_vector.json")
    i.add_argument("--quiet", action="store_true")
    i.set_defaults(func=cmd_interop)

    c = sub.add_parser("capabilities", help="List registered adapters/anchors/…")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_capabilities)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
