const test = require("node:test");
const assert = require("node:assert");
const { assertNoCborFloatsHex } = require("../../scripts/grp003/canonical-validator");

test("TV-037 rejects CBOR float", () => {
  // fa 3f800000 = float32 1.0
  assert.throws(
    () => assertNoCborFloatsHex("fa3f800000"),
    /FORBIDDEN_FLOAT/
  );
});
