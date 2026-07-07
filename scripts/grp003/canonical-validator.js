function assertNoDuplicateKeysFromRawJson(raw) {
  const seen = new Set();
  raw.replace(/"([^"]+)"\s*:/g, (_, key) => {
    if (seen.has(key)) throw new Error("DUPLICATE_KEY");
    seen.add(key);
  });
}
module.exports = { assertNoDuplicateKeysFromRawJson };

function assertNoCborFloatsHex(hex) {
  const clean = hex.toLowerCase().replace(/^0x/, "");
  // CBOR simple/float major type examples:
  // f9 = float16, fa = float32, fb = float64
  if (clean.startsWith("f9") || clean.startsWith("fa") || clean.startsWith("fb")) {
    throw new Error("FORBIDDEN_FLOAT");
  }
}
module.exports.assertNoCborFloatsHex = assertNoCborFloatsHex;
