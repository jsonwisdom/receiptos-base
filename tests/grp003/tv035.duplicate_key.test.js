const test = require("node:test");
const assert = require("node:assert");
const { assertNoDuplicateKeysFromRawJson } = require("../../scripts/grp003/canonical-validator");

test("TV-035 rejects duplicate keys", () => {
  assert.throws(
    () => assertNoDuplicateKeysFromRawJson('{"a":1,"a":2}'),
    /DUPLICATE_KEY/
  );
});
