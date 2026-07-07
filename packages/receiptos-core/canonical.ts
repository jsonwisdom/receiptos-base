import { canonicalize as jcsCanonicalize } from "json-canonicalize";
import { createHash } from "node:crypto";

export function canonicalJSON(value: unknown): string {
  return jcsCanonicalize(value);
}

export function sha256Hex(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

export function hashCanonical(value: unknown): string {
  return sha256Hex(canonicalJSON(value));
}

export function receiptIdFromCore(core: unknown): string {
  return `ros-${hashCanonical(core)}`;
}
