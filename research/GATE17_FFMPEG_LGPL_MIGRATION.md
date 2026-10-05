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
requires exactly one packaged bin/ffmpeg.exe, bin/ffprobe.exe and LICENSE.txt.
Both tools must identify the same pinned FFmpeg source revision. The probe
records both executable hashes before any later promotion decision.

## Required executable properties

The candidate is rejected unless:

- its version line contains the pinned source revision;
- its configuration does not contain --enable-gpl, --enable-nonfree,
  --enable-libx264, or --enable-libx265;
- its decoder inventory contains eatgq;
- its encoder inventory contains both h264_mf and aac;
- on Windows CI it can actually instantiate h264_mf and native AAC using the
  production conversion path's `-fps_mode passthrough`, write a 320x480 /
  25 fps / 22,050 Hz stereo MP4, and decode both streams again;
- the archive's own ffprobe must report exactly H.264/yuv420p video, AAC
  22,050 Hz stereo audio and an MP4 container for that synthetic derivative.

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


## Recovery 319 source-minimization boundary

The verified BtbN LGPL archive is technically useful, but its own
`-version` configuration proves that it statically enables many third-party
libraries. It therefore narrows the current GPL/libx264 problem without
providing a minimal redistribution surface.

The exact source chain now pinned for that verified broad candidate is:

- BtbN FFmpeg-Builds release tag `autobuild-2026-10-03-18-14`;
- BtbN build-repository commit
  `9acad4a9ef1583096af7836cc1e9c8cbcb4d3950`;
- build arguments `win64 lgpl 9.0`;
- BtbN's `9.0` add-in selects FFmpeg branch `release/9.0`;
- the candidate executable identifies FFmpeg source commit
  `46d8f462eeb87ee1f704d8c44a0ee24fca471ad1`;
- the LGPL variant's FFmpeg license file is `COPYING.LGPLv3`.

`third_party/ffmpeg-lgpl-candidate/SOURCE-CONTRACT.json` keeps that broad
candidate explicitly non-minimal and non-production-ready. It also defines a
separate minimal-helper target pinned to the same FFmpeg source commit.

The minimal target uses `--disable-everything --disable-autodetect`, enables
no `--enable-lib*` dependency, and then explicitly re-enables Windows
Media Foundation because FFmpeg's configure script classifies
`mediafoundation` as an autodetected platform facility and `h264_mf`
depends on it. The `ffmpeg` program also depends on FFmpeg's generic thread
capability, so the native `w32threads` backend is explicitly re-enabled after
autodetection is disabled. It retains only:

- file protocol;
- the FFmpeg `ea` Electronic Arts demuxer;
- `eatgq` plus the bounded set of EA audio codecs the upstream EA demuxer can
  select;
- native H.264 and AAC decoders because the runtime immediately decode-verifies
  each generated derivative before accepting its cache receipt;
- native AAC encoding plus FFmpeg's internal `aresample` filter, because the
  AAC encoder accepts FLTP while EA audio decoders may produce integer PCM;
- Windows Media Foundation `h264_mf`;
- the actual `mp4` muxer, which selects FFmpeg's shared MOV/ISO-BMFF
  muxing machinery, plus the `mov` demuxer so FFprobe and runtime decode
  verification can reopen the generated MP4;
- the `pipe` protocol and `null` muxer because the runtime verifier uses
  `-progress pipe:1` and decodes accepted derivatives to `-f null -`;
- the `ffmpeg` and `ffprobe` command-line programs.

FFmpeg's upstream source identifies `eatgq` as the Electronic Arts TGQ video
decoder and the `ea` input format as the Electronic Arts multimedia demuxer.
FFmpeg's codec documentation lists `h264_mf` as a Media Foundation H.264
encoder. These source facts bound the technical target but do not prove that
the proposed minimal configure line builds successfully.

All minimal-helper proof flags deliberately remain false. Promotion still
requires an actual build from the pinned FFmpeg commit, synthetic conversion
proof, exact original-TGQ conversion, external Windows 11 playback acceptance,
and source/license material completion. The contract is technical provenance,
not a legal-compliance determination.


The minimal target also deliberately omits `--enable-version3`. The selected
pinned FFmpeg sources for TGQ/EA demuxing, Media Foundation encoding, native
AAC, MOV/MP4 muxing and internal audio resampling carry the project's LGPL
2.1-or-later notice, and the selected configure dependencies do not require
GPL or version-3-only mode. The minimal target therefore pins
`COPYING.LGPLv2.1` rather than inheriting the broad BtbN build's
`COPYING.LGPLv3`. This is a source/license-mode observation, not a legal
redistribution-compliance conclusion.
