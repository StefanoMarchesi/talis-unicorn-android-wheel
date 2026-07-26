# Unicorn Android wheel for Talis

Reproducible Chaquopy-compatible Android wheels for
[`unicorn`](https://github.com/unicorn-engine/unicorn), built from the official
PyPI source distribution. This repository contains build metadata and patches,
not Apple's libraries and not a pre-provisioned Anisette identity.

## Supported target

- Unicorn: `2.1.4`
- Python: `3.11`
- Android API: `24+`
- ABI: `arm64-v8a`
- Emulated architecture: AArch64 only (the Apple Music Android library bundle
  used by Anisette.py is selected for `arm64-v8a`)
- Chaquopy package builder: commit
  `e01057c72fdd737f202bd1be1de85af51e06cad0` (`17.0.0`)

The output filename is verified by `scripts/verify-wheel.py`. The verifier also
checks the wheel metadata, Android ELF machine, 16 KiB load-segment alignment,
SONAME and the absence of host-library dependencies.

## Build

The official Chaquopy wheel builder only runs on Linux x86-64. On a compatible
host with an Android SDK:

```sh
./scripts/build.sh
```

The wheel is written to `dist/`. GitHub Actions builds the same artifact on a
clean runner and publishes it as a workflow artifact. A release attaches the
wheel, `SHA256SUMS`, the pinned upstream source archive and the exact Android
patch; applications should consume a versioned release, never the latest
workflow output.

## Supply-chain boundary

- The Unicorn source URL and SHA-256 are pinned.
- The Chaquopy builder commit and Python target are pinned.
- Build products are not committed to Git.
- Apple binaries are downloaded by Anisette.py only after explicit developer
  action in the consuming app; they are outside this repository.
- This project does not contain Apple credentials, Find My tokens, private
  OpenHaystack keys or location reports.

The engine code included in this build is distributed under GNU GPL version 2.
Chaquopy's build tooling is MIT-licensed. See `THIRD_PARTY_NOTICES.md`.
