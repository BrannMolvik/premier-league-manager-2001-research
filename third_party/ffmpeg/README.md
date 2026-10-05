# Bundled FFmpeg release boundary

The Windows release-candidate workflow currently obtains its executable from
`imageio-ffmpeg==0.6.0` and copies that executable to
`runtime_tools/ffmpeg.exe`.

The historical Windows package run `37305008767` identified that executable
as **FFmpeg 7.1 essentials_build-www.gyan.dev**, built with GPL/version-3/static
configuration and GPL-family external libraries including libx264. The exact
observed identity used by the release guard is recorded in `PROVENANCE.json`.

This directory is intentionally **not** a declaration that redistribution
requirements are satisfied. The final Gate-17 release audit must fail while
`release_materials.release_ready`, `license_material_complete`, or
`source_material_complete` are false. Before final release, the exact selected
binary must have corresponding license and source-distribution material staged,
hash-bound in `PROVENANCE.json`, and included in the same release archive.

Primary references recorded for the audit:

- https://ffmpeg.org/legal.html
- https://www.gyan.dev/ffmpeg/builds/
- https://github.com/imageio/imageio-ffmpeg/releases/tag/v0.6.0

This is a provenance and packaging control, not legal advice or a legal
compliance determination.
