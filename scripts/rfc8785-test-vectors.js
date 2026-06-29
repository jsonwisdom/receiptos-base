#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const { canonicalize } = require("json-canonicalize");

function fail(message) {
  console.error(`::error::${message}`);
  process.exit(1);
}

function must(condition, message) {
  if (!condition) fail(message);
}

function sha256(text) {
  return crypto.createHash("sha256").update(text).digest("hex");
}

const vectors = [
  {
    name: "object keys sort deterministically",
    input: { b: 2, a: 1 },
    expected: '{"a":1,"b":2}'
  },
  {
    name: "nested objects sort while arrays preserve order",
    input: { z: [3, 2, 1], a: { b: true, a: null } },
    expected: '{"a":{"a":null,"b":true},"z":[3,2,1]}'
  },
  {
    name: "strings preserve slash characters without extra whitespace",
    input: { url: "https://cmptrwsdm.com/app" },
    expected: '{"url":"https://cmptrwsdm.com/app"}'
  },
  {
    name: "number representation is normalized",
    input: { int: 1, zero: -0, decimal: 1.5, exponent: 100000000000000000000 },
    expected: '{"decimal":1.5,"exponent":100000000000000000000,"int":1,"zero":0}'
  },
  {
    name: "unicode strings remain semantically intact",
    input: { omega: "Ω", emoji: "🧾", composed: "é" },
    expected: '{"composed":"é","emoji":"🧾","omega":"Ω"}'
  }
];

for (const vector of vectors) {
  const actual = canonicalize(vector.input);
  must(actual === vector.expected, `${vector.name}\nExpected: ${vector.expected}\nActual:   ${actual}`);
  console.log(`PASS ${vector.name} sha256=${sha256(actual)}`);
}

console.log("RFC8785 canonicalization test vectors passed.");
