# Gate 17 contributor license-material checkpoint

_Status: technical evidence assembly only; not a legal conclusion._

The exact four toolchain packages that contribute code/data to the minimal
static FFmpeg helper are already source-package-pinned. This checkpoint
reproduces the license/declaration material that their own MSYS2 package recipes
identify:

- GCC: `COPYING3` and `COPYING.RUNTIME` from the pinned GCC 16.2.0 source;
- MinGW-w64 CRT: the three COPYING files installed by its package recipe;
- winpthreads: the COPYING file installed by `_install_licenses`;
- Windows default manifest: its `.SRCINFO`, `PKGBUILD`, and pinned
  `genrc.py` as Public Domain declaration/source evidence, because that
  source package contains no separate dedicated license text.

Every evidence file is SHA-256 and size pinned in
`TOOLCHAIN-CONTRACT.json`. CI re-downloads the exact pinned source packages,
extracts the evidence from the nested source archive/bare source repositories,
checks the package-recipe declarations, and fails closed on byte drift.

This still does **not** assert that the collected texts are legally sufficient,
that every possible notice obligation has been adjudicated, that the full FFmpeg
source-distribution requirement has been packaged, or that the release is legally
compliant. Therefore `license_notice_material_complete=false`,
`source_material_complete=false`, and `legal_compliance_claimed=false`
remain mandatory.
