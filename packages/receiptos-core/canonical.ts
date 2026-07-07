// Deterministic canonicalization for L1 verifier

export function canonicalize(input: any): string {
  // Stable sort keys, no Date, no stringify for hash
  if (input === null || typeof input !== 'object') return JSON.stringify(input);
  if (Array.isArray(input)) {
    return '[' + input.map(canonicalize).join(',') + ']';
  }
  const keys = Object.keys(input).sort();
  const pairs = keys.map(k => `${JSON.stringify(k)}:${canonicalize(input[k])}`);
  return '{' + pairs.join(',') + '}';
}