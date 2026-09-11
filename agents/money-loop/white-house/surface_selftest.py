#!/usr/bin/env python3

import json

from semantic_rendering import ALLOWED_PROVEN_RENDERINGS, FORBIDDEN_RENDERINGS, SEMANTIC_TYPE
from surfaces import SURFACES, render_surface


def main() -> None:
    checks = 0

    for surface in SURFACES:
        for wording in ALLOWED_PROVEN_RENDERINGS:
            output = render_surface(surface, "PROVEN", wording=wording)
            if surface == "JSON":
                payload = json.loads(output)
                assert payload["semantic_type"] == SEMANTIC_TYPE
                assert payload["evidence_gate_proven"] is True
                assert payload["claim_proven"] is False
                assert payload["allegation_proven"] is False
                assert payload["fraud_proven"] is False
                assert payload["guilt_established"] is False
                assert payload["doj_endorsement"] is False
                assert payload["legal_finding"] is False
                assert payload["authority_created"] is False
            else:
                assert SEMANTIC_TYPE in output
                for forbidden in FORBIDDEN_RENDERINGS:
                    assert forbidden.casefold() not in output.casefold()
            checks += 1

        for forbidden in FORBIDDEN_RENDERINGS:
            try:
                render_surface(surface, "PROVEN", wording=forbidden)
            except ValueError:
                checks += 1
            else:
                raise AssertionError(f"{surface} bypass accepted forbidden rendering: {forbidden}")

    print(f"PASS: T16 JSON/CLI/REPORT/LOG bypass matrix ({checks} checks)")


if __name__ == "__main__":
    main()
