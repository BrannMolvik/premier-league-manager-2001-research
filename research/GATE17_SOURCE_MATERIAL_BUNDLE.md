# Gate 17 static contributor source-material bundle

_Status: technical bundle-materialization checkpoint; no legal conclusion._

Recovery 385 proved member/direct-object contribution for exactly four locked
MSYS2/UCRT64 packages/source families in the exact minimal FFmpeg helper:

- MinGW-w64 CRT;
- GCC runtime;
- winpthreads;
- Windows default manifest.

The workflow in `.github/workflows/gate17-source-material-bundle.yml` now
materializes the exact first-party MSYS2 source-package tarballs already
verified in `TOOLCHAIN-CONTRACT.json`. It records SHA-256 and byte size for
each downloaded source package and uploads the four tarballs plus a deterministic
JSON manifest as a CI artifact. Third-party source archives remain outside Git.

This checkpoint deliberately does **not** promote
`source_material_complete` or `legal_compliance_claimed`. The first
successful artifact must be reviewed and its hashes pinned before the bundle is
reproducible against mirror drift. Actual license/notice texts must then be
identified and assembled from the relevant source/package material, and a
separate legal/compliance review remains required.
