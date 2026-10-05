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
- its encoder inventory contains both h264_mf and aac.

The receipt records the exact candidate executable and license hashes, but
keeps all of these false:

- production_runtime_switched;
- windows11_conversion_verified;
- windows11_playback_verified;
- license_compliance_claimed.

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
