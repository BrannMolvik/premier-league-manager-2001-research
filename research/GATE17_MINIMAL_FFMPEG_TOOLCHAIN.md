# Gate 17 minimal FFmpeg toolchain provenance

_Status: technical reproducibility checkpoint only._

The exact-source minimal FFmpeg build is statically linked, so the earlier
dynamic `libwinpthread-1.dll` deployment blocker is closed. Static linkage does
not erase the provenance of the compiler/CRT/runtime code incorporated at link
time.

This checkpoint therefore pins the successful build's GitHub Action revisions
and audits a critical subset of the actual MSYS2/UCRT64 package versions before
each future minimal-helper build. The complete `pacman -Q` inventory and a
machine-readable toolchain receipt are retained in the build artifact.

The successful reference run used MSYS2 installer release
`0.0.20260927`, GCC `16.2.0-4`, binutils `2.47-3`, NASM `3.02-1`, and
MinGW-w64 CRT/headers/winpthreads revision
`14.0.0.r426.g4564ee4b5-1`.

This remains deliberately incomplete. The contract does not claim that every
transitive build package is locked, nor that all corresponding source archives,
license texts, notices, or redistribution obligations have been assembled.
`source_material_complete=false` and `legal_compliance_claimed=false`
remain mandatory.

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
