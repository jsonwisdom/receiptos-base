/**
 * @jsonwisdom/farcaster-verify
 *
 * Authority=false Farcaster Mini App manifest verification.
 *
 * Doctrine:
 * - RFC8785 canonicalization
 * - replayable evidence over authority
 * - semantic verification before lock acceptance
 */

export type FarcasterPermission = "farcaster.read" | "farcaster.write";

export interface FarcasterDeveloper {
  /** Human or organization name responsible for the manifest. Must be non-empty. */
  name: string;
  /** HTTPS developer URL. */
  url: `https://${string}`;
}

export interface FarcasterMiniAppManifest {
  /** Stable lowercase manifest identity. */
  id: string;
  /** Human-readable app name. Must be non-empty. */
  name: string;
  /** Human-readable description. Must be non-empty. */
  description: string;
  developer: FarcasterDeveloper;
  /** Optional HTTPS website URL. */
  website?: `https://${string}`;
  /** HTTPS PNG icon URL. */
  icon: `https://${string}.png`;
  /** At least one HTTPS image URL. */
  screenshots: Array<`https://${string}`>;
  app: {
    /** HTTPS Mini App URL. */
    url: `https://${string}`;
    /** Farcaster permission whitelist. */
    permissions: FarcasterPermission[];
  };
}

export interface FarcasterManifestLock {
  /** Must match manifest.id. */
  manifest_id: string;
  /** Canonical manifest path, normally .well-known/farcaster/manifest.jcs. */
  manifest_path: string;
  /** Must remain manifest.jcs. */
  canonical_source: "manifest.jcs";
  /** Standards-complete canonicalization doctrine. */
  canonicalization: "RFC8785";
  /** Lowercase SHA-256 digest of manifest.jcs. */
  sha256: string;
  /** ISO-8601 timestamp. Must not be future-dated. */
  created_at: string;
  /** Lock state. */
  status: "LOCKED";
  /** Doctrine flag. This package does not assert authority. */
  authority: false;
}

export interface Doctrine {
  authority: false;
  canonicalization: "RFC8785";
  principle: "Replay First. Verify Everything.";
}

export interface CommandMap {
  semantic: "farcaster-verify-semantic";
  lock: "farcaster-verify-lock";
  rfc8785: "farcaster-verify-rfc8785";
  invalid: "farcaster-verify-invalid";
  fuzz: "farcaster-verify-fuzz";
}

export interface PackageExports {
  package: "@jsonwisdom/farcaster-verify";
  doctrine: Doctrine;
  commands: CommandMap;
}

declare const exports: PackageExports;
export = exports;
