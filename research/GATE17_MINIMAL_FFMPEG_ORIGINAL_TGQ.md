# Gate 17 minimal FFmpeg exact-original TGQ proof

_Status: proof producer prepared; no private Windows receipt exists yet._

## Purpose

The minimal helper now has two hosted proofs: exact pinned-source build and a
same-build synthetic startup roundtrip. Those do not prove that the helper can
convert the two original FM2001 startup TGQs.

`reconstruction/gate17_ffmpeg_original_tgq_proof.py` closes the evidence
handoff without putting original media in Git.

## Fail-closed bindings

The producer requires all of the following from the same private Windows run:

- exact `ffmpeg.exe` and `ffprobe.exe` whose SHA-256 values match the
  successful minimal build receipt;
- that build receipt still declares only `build_verified=true`;
- a successful synthetic-roundtrip receipt SHA-256-bound to that exact build
  receipt and those exact binaries;
- the authorized original game directory outside Git;
- exact canonical `FMV/easp.tgq` and `FMV/premintro.tgq` hashes/sizes from
  `original_startup_media.py`;
- the Windows Media Foundation profile:
  `scale=640:480:flags=neighbor`, `h264_mf`, AAC, MP4;
- exact decoded video frame counts 97 and 1275 respectively.

It reuses the existing private converter, so source files, derivatives and both
receipts must remain outside the repository.

A successful Gate-17 receipt may set only:

- `build_verified=true`;
- `synthetic_roundtrip_verified=true`;
- `exact_original_tgq_verified=true`.

It must keep external Windows playback, source-material completeness,
production migration readiness and legal-compliance claims false.

## Recovery 352 private-source checkpoint

The authorized 511,121,336-byte Library archive was rematerialized and the two
original TGQs were recovered directly from the MODE1/2352 Joliet image:

- `FMV/easp.tgq`: 1,383,304 bytes,
  SHA-256 `73dc078ee8fe7e1d7412b4bcba072c3f8ec85546d5e5b94f90be9732498af97c`,
  320x480, 25 fps, 97 decoded video frames, ADPCM EA 22050 Hz stereo;
- `FMV/premintro.tgq`: 28,434,180 bytes,
  SHA-256 `a16e64a1c680ce1c7bcf57f76f05dd8e51a77663b5b4a673e681c9da188a0b0d`,
  320x480, 25 fps, 1275 decoded video frames, ADPCM EA 22050 Hz stereo.

A Linux reference conversion using the same recovered scale/AAC/MP4 geometry
also succeeded for both inputs, but it used libx264 and is only input sanity
evidence. It does not satisfy the Windows `h264_mf` minimal-helper criterion.

The remaining blocker is platform locality: the exact minimal helper is a
Windows Media Foundation build while the private-source sandbox is Linux.
Private TGQ bytes must not be uploaded to the public hosted workflow.

## Intended private Windows command

After obtaining the exact build artifact containing `ffmpeg.exe`,
`ffprobe.exe`, `build-proof.json` and `roundtrip-proof.json`, run outside
Git:

```powershell
python reconstruction/gate17_ffmpeg_original_tgq_proof.py `
  --repo-root . `
  --source-root "C:\Games\FM2001" `
  --output-root "C:\FM2001-private\startup-minimal" `
  --conversion-receipt "C:\FM2001-private\startup-minimal-conversion.json" `
  --output-receipt "C:\FM2001-private\gate17-original-tgq.json" `
  --ffmpeg "C:\FM2001-private\minimal-helper\ffmpeg.exe" `
  --ffprobe "C:\FM2001-private\minimal-helper\ffprobe.exe" `
  --build-proof "C:\FM2001-private\minimal-helper\build-proof.json" `
  --roundtrip-proof "C:\FM2001-private\minimal-helper\roundtrip-proof.json"
```

This is not Gate 17 completion and does not promote the helper into the release
package.
