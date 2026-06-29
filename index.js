"use strict";

module.exports = {
  package: "@jsonwisdom/farcaster-verify",
  doctrine: {
    authority: false,
    canonicalization: "RFC8785",
    principle: "Replay First. Verify Everything."
  },
  commands: {
    semantic: "farcaster-verify-semantic",
    lock: "farcaster-verify-lock",
    rfc8785: "farcaster-verify-rfc8785",
    invalid: "farcaster-verify-invalid",
    fuzz: "farcaster-verify-fuzz"
  }
};
