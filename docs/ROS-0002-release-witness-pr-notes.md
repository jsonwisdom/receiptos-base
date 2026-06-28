# ROS-0002 PR Notes

This PR adds the first automated release witness layer.

It is intentionally side-effect-free:

- no secrets
- no private keys
- no chain writes
- no IPFS writes
- no release creation

The only goal is to prove that a tag can trigger a clean GitHub runner to replay the checked-in evidence bundle and upload the replay inputs as workflow artifacts.
