# Gate 17 minimal FFmpeg toolchain provenance

_Status: technical reproducibility checkpoint only._

The exact-source minimal FFmpeg build is statically linked, so the earlier
dynamic `libwinpthread-1.dll` deployment blocker is closed. Static linkage does
not erase the provenance of the compiler/CRT/runtime code incorporated at link
time.

This checkpoint pins the successful build's GitHub Action revisions and now
enforces an exact lock of the complete observed MSYS2/UCRT64 package environment
before each future minimal-helper build. The lock contains 151 package/version
rows captured by `pacman -Q | LC_ALL=C sort`; any missing, extra, or changed
package fails the provenance audit.

The successful reference environment used MSYS2 installer release
`0.0.20260927`, GCC `16.2.0-4`, binutils `2.47-3`, NASM `3.02-1`, and
MinGW-w64 CRT/headers/winpthreads revision
`14.0.0.r426.g4564ee4b5-1`.

The package lock is a reproducibility claim only. It does not claim that every
installed package contributes redistributed code, nor that all corresponding
source archives, license texts, notices, or redistribution obligations have
been assembled. `source_material_complete=false` and
`legal_compliance_claimed=false` remain mandatory.

## Recovery 380 bounded source-material map

The critical package subset is now mapped back to eight source-package
families in `TOOLCHAIN-CONTRACT.json`. This mapping is intentionally narrower
than a full build-environment closure.

Official MSYS2 package metadata verified exact source-only tarball identities
for six of those families as of 7 October 2026:

- GCC `16.2.0-4`:
  `https://mirror.msys2.org/mingw/sources/mingw-w64-gcc-16.2.0-4.src.tar.zst`;
- binutils `2.47-3`:
  `https://mirror.msys2.org/mingw/sources/mingw-w64-binutils-2.47-3.src.tar.zst`;
- NASM `3.02-1`:
  `https://mirror.msys2.org/mingw/sources/mingw-w64-nasm-3.02-1.src.tar.zst`;
- MinGW-w64 headers `14.0.0.r426.g4564ee4b5-1`:
  `https://mirror.msys2.org/mingw/sources/mingw-w64-headers-14.0.0.r426.g4564ee4b5-1.src.tar.zst`;
- winpthreads `14.0.0.r426.g4564ee4b5-1`:
  `https://mirror.msys2.org/mingw/sources/mingw-w64-winpthreads-14.0.0.r426.g4564ee4b5-1.src.tar.zst`;
- Windows default manifest `20260815-1`:
  `https://mirror.msys2.org/mingw/sources/mingw-w64-windows-default-manifest-20260815-1.src.tar.zst`.

The two remaining critical-family rows are deliberately unresolved rather than
filled from filename inference:

- `msys2-runtime 3.6.10-6`: the official repository index confirms the
  pinned `3.6.10-6` package version, but this checkpoint did not independently
  verify the exact `-6` source-only tarball metadata;
- MinGW-w64 CRT `14.0.0.r426.g4564ee4b5-1`: the official package index
  confirms the pinned binary version, but this checkpoint did not independently
  verify the exact source-only tarball identity for that revision.

The validator requires every pinned critical binary package to map to one of
these source families and requires each family version to agree with the pinned
binary version. A source archive URL may appear only when its official metadata
was verified. Unverified rows must keep the URL null and retain an explicit
blocker note.

This still does **not** establish a complete transitive package lock. The
successful build artifact's full `pacman -Q` inventory must be reduced to the
components that actually contribute redistributed code, and every relevant
source/license/notice obligation must then be assembled and checksummed.
Accordingly `complete_package_lock=false`,
`source_material_complete=false`, and `legal_compliance_claimed=false`
remain mandatory. This is technical provenance work, not a legal conclusion.

## Recovery 381 critical source-family closure

The two source-family identities left unresolved in Recovery 380 are now
independently verified from first-party MSYS2 package metadata:

- `msys2-runtime 3.6.10-6` publishes
  `https://mirror.msys2.org/msys/sources/msys2-runtime-3.6.10-6.src.tar.zst`;
- MinGW-w64 CRT `14.0.0.r426.g4564ee4b5-1` publishes
  `https://mirror.msys2.org/mingw/sources/mingw-w64-crt-14.0.0.r426.g4564ee4b5-1.src.tar.zst`.

The critical subset therefore has source-tarball metadata for all eight mapped
source families. This closes only those two bounded metadata blockers. It does
**not** establish the complete transitive package lock, identify every package
whose code is redistributed in the static helper, assemble the final
source/license/notice bundle, or make a legal-compliance conclusion.
`complete_package_lock=false`, `source_material_complete=false`, and
`legal_compliance_claimed=false` remain mandatory.

## Recovery 381 complete build-environment package lock

Three independent successful minimal-FFmpeg build artifacts produced the same
byte-identical `pacman -Q | LC_ALL=C sort` inventory:

- workflow `37506276513`, artifact `11431743521`, artifact digest
  `sha256:ec6ce0ab49e7e0b5aa9b4c2b6df5f01dd0f6c62f02c75588c91a67e8d82b0db9`;
- workflow `37582619057`, artifact `11465166679`, artifact digest
  `sha256:ba03294e8a8ed8541773e1ceb0db7209690ceb24816df79e57380ae455f63cdc`;
- workflow `37585092239`, artifact `11465843961`, artifact digest
  `sha256:0bb3bb84778217b70fa20b4e3996a2e5cac1fcdfbb734d148ad682e06b81d46c`.

Each inventory has 151 package/version rows and SHA-256
`c1e79ae6500dd48a206fa786f9f863f37cdc788e6f2dbfba0c926e999077abec`.
The exact rows are now retained as
`third_party/ffmpeg-lgpl-candidate/TOOLCHAIN-PACKAGES.lock`.

The toolchain audit compares the live build environment against that complete
map and fails closed on missing packages, extra packages, version drift, lock
digest drift, or package-count drift. `complete_package_lock=true` therefore
means only that the successful build environment's package identities are
completely locked.

This does **not** decide which of those 151 installed packages contribute code
or data to the statically linked helper. That attribution, the corresponding
source/license/notice bundle, and the separate legal review remain unresolved.
Accordingly `source_material_complete=false` and
`legal_compliance_claimed=false` remain mandatory.
