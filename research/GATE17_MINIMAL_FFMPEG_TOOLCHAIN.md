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

Public MSYS2 package metadata identifies source-only tarballs for the relevant
GCC, binutils and winpthreads/CRT families. Those are leads for the later
source-material bundle, not a compliance conclusion.
