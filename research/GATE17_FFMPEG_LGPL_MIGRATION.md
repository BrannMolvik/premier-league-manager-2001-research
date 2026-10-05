# Gate 17 LGPL FFmpeg migration candidate

_Status: candidate-only audit. Production packaging still uses the #468 pinned
imageio-ffmpeg/Gyan executable and remains fail-closed for final release._

## Why this exists

Recovery 318 established that the current bundled Windows helper is an FFmpeg
7.1 Gyan essentials static build with GPL enabled and libx264 present. PR #468
therefore made third-party license/source material a hard final-release
boundary instead of silently distributing that helper.

A narrower route is possible in principle without changing the source-backed
startup sequence:

- FFmpeg's EA TGQ decoder is an internal decoder named eatgq;
- FFmpeg documents a Windows Media Foundation H.264 encoder named h264_mf;
- FFmpeg's AAC encoder is native;
- Microsoft documents H.264 and AAC encoders plus the MP4 sink/source as
  built-in Media Foundation capabilities on supported Windows versions;
- BtbN publishes distinct Windows LGPL builds which exclude GPL-only libraries
  such as libx264/libx265.

The current conversion contract already targets H.264/AAC in MP4. Replacing
libx264 with h264_mf could therefore retain the derivative codec/container
contract while removing the current GPL/libx264 dependency. This still does
not eliminate FFmpeg redistribution obligations and is not a legal conclusion.

## Pinned candidate

The probe intentionally targets one immutable BtbN artifact:

- release tag: autobuild-2026-10-03-18-14;
- archive: ffmpeg-n9.0.2-22-g46d8f462ee-win64-lgpl-9.0.zip;
- GitHub asset SHA-256:
  3fc85bae9f9643a03d15c2d2de12fb017dcd9fdabe819bfb1a94f54fea108714;
- upstream FFmpeg revision token: n9.0.2-22-g46d8f462ee.

reconstruction/gate17_ffmpeg_lgpl_candidate.py verifies the archive hash,
requires exactly one packaged bin/ffmpeg.exe and LICENSE.txt, and then checks
the executable itself.

## Required executable properties

The candidate is rejected unless:

- its version line contains the pinned source revision;
- its configuration does not contain --enable-gpl, --enable-nonfree,
  --enable-libx264, or --enable-libx265;
- its decoder inventory contains eatgq;
- its encoder inventory contains both h264_mf and aac;
- on Windows CI it can actually instantiate h264_mf and native AAC, write a
  320x480 / 25 fps / 22,050 Hz stereo MP4, and decode both streams again.

The synthetic roundtrip proves candidate executable/runtime capability only; it
does not substitute for converting the two exact original TGQs or for real
Windows 11 visible/audible acceptance.

The receipt records the exact candidate executable and license hashes, but
keeps all of these false:

- production_runtime_switched;
- windows11_conversion_verified;
- windows11_playback_verified;
- license_compliance_claimed.

## Exact private conversion command

PR #470 adds an opt-in private conversion profile without changing normal
runtime defaults. Once private source execution is healthy and the exact
original installation tree is available outside Git, run:

```powershell
python reconstruction/gate14_startup_media_convert.py `
  --source-root "C:\path\to\FM2001" `
  --output-root "C:\private\fm2001-lgpl-startup" `
  --receipt "C:\private\fm2001-lgpl-startup-receipt.json" `
  --repo-root "." `
  --ffmpeg "C:\path\to\pinned-lgpl\ffmpeg.exe" `
  --ffprobe "C:\path\to\pinned-lgpl\ffprobe.exe" `
  --video-encoder h264_mf
```

The converter revalidates the canonical source sizes/SHA-256 identities before
starting FFmpeg, writes no success receipt until both derivatives satisfy the
H.264/AAC MP4 geometry and exact decoded-frame contract, and records
`video_encoder: h264_mf` in the private receipt.

The runtime cache API also accepts the same explicit candidate profile for
verification work. Cache receipts are profile-bound in addition to being bound
to the FFmpeg executable SHA-256, so a prior `libx264` cache cannot be reused
as evidence for `h264_mf`. Normal application launch still omits the profile
argument and therefore continues to use the unchanged `libx264` default until
promotion is explicitly justified.

## Promotion boundary

Do not replace the production helper merely because this probe passes. A
migration still needs:

1. an actual Windows 11 conversion of both exact original TGQs through the
   candidate using h264_mf;
2. the same decoded frame-count and audio-decode checks used by the existing
   runtime cache;
3. real Windows 11 visible/audible startup acceptance for the new derivatives;
4. exact source/license/build-script distribution handling for the selected
   LGPL helper;
5. an updated final-release provenance contract and package audit.

Until those steps pass, #468's current fail-closed GPL-build boundary remains
canonical.

## Public references

- https://ffmpeg.org/legal.html
- https://ffmpeg.org/ffmpeg-all.html
- https://www.ffmpeg.org/doxygen/9.0/eatgq_8c.html
- https://learn.microsoft.com/en-us/windows/win32/medfound/supported-media-formats-in-media-foundation
- https://github.com/BtbN/FFmpeg-Builds
- https://github.com/BtbN/FFmpeg-Builds/releases/tag/autobuild-2026-10-03-18-14
