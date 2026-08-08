"""Agent Economics V0.1 evaluator surface.

Import is fail-closed: vendored AL truth-contract bytes must match their pinned
Git blob object IDs before any evaluator module is considered loadable.
"""

from .schema_pin import SchemaPinError, verify_schema_pin

SCHEMA_PIN_STATUS = verify_schema_pin()

__all__ = ["SCHEMA_PIN_STATUS", "SchemaPinError", "verify_schema_pin"]
