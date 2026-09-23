#!/usr/bin/env -S node --experimental-strip-types

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const CORPUS_PATH = resolve(HERE, "../corpus/corrected-corpus.json");
const AUTHORIZED_IDS = new Set(["CNF-001", "CBF-001"]);

function hasUnpairedSurrogate(value: unknown): boolean {
  if (typeof value === "string") {
    for (let i = 0; i < value.length; i += 1) {
      const code = value.charCodeAt(i);
      if (code >= 0xd800 && code <= 0xdbff) {
        const next = value.charCodeAt(i + 1);
        if (!(next >= 0xdc00 && next <= 0xdfff)) return true;
        i += 1;
      } else if (code >= 0xdc00 && code <= 0xdfff) {
        return true;
      }
    }
    return false;
  }

  if (Array.isArray(value)) return value.some(hasUnpairedSurrogate);

  if (value !== null && typeof value === "object") {
    return Object.entries(value).some(
      ([key, item]) => hasUnpairedSurrogate(key) || hasUnpairedSurrogate(item),
    );
  }

  return false;
}

function sha256(text: string): string {
  return createHash("sha256").update(Buffer.from(text, "utf8")).digest("hex");
}

const corpus = JSON.parse(readFileSync(CORPUS_PATH, "utf8"));
const results: Record<string, unknown>[] = [];

for (const vector of corpus.vectors) {
  if (!AUTHORIZED_IDS.has(vector.id)) {
    throw new Error(`Unauthorized vector: ${vector.id}`);
  }

  const value = JSON.parse(vector.input_json);

  if (vector.id === "CNF-001") {
    const failedClosed = hasUnpairedSurrogate(value);
    results.push({
      id: vector.id,
      profile: vector.profile,
      actual_result: failedClosed ? "FAIL" : "PASS",
      actual_error_code: failedClosed ? "UNPAIRED_SURROGATE" : null,
      matched:
        failedClosed &&
        vector.expected_result === "FAIL" &&
        vector.expected_error_code === "UNPAIRED_SURROGATE",
    });
    continue;
  }

  const output = JSON.stringify(value);
  const digest = sha256(output);
  results.push({
    id: vector.id,
    profile: vector.profile,
    actual_result: "PASS",
    actual_output_json: output,
    actual_sha256: digest,
    matched:
      vector.expected_result === "PASS" &&
      vector.expected_output_json === output &&
      vector.expected_sha256 === digest,
  });
}

const passed = results.every((result) => result.matched === true);
const report = {
  audit_gate: "410_OPEN",
  corpus_version: corpus.corpus_version,
  promotion: "PROHIBITED",
  runner: "TYPESCRIPT_CORRECTED_CORPUS_HARNESS",
  status: passed ? "PASS" : "FAIL",
  vectors: results,
};

console.log(JSON.stringify(report, null, 2));
process.exitCode = passed ? 0 : 1;
