# Gate 17 minimal FFmpeg build proof

_Status: build-proof work-ahead. Production packaging is unchanged._

This proof builds the startup-media helper directly from the pinned FFmpeg
source commit rather than redistributing the broad BtbN LGPL binary.

## Exact source

- FFmpeg repository: https://github.com/FFmpeg/FFmpeg
- source commit: `46d8f462eeb87ee1f704d8c44a0ee24fca471ad1`
- source contract:
  `third_party/ffmpeg-lgpl-candidate/SOURCE-CONTRACT.json`
- source license selected by the bounded contract: `COPYING.LGPLv2.1`

The workflow checks out that exact commit and writes `git rev-parse HEAD` into
the build receipt. A successful compile from a different source commit is not
acceptable evidence.

## Build boundary

`.github/workflows/gate17-minimal-ffmpeg-build.yml` builds under the native
MSYS2 UCRT64 environment on GitHub's Windows runner. Configure arguments are
read directly from the checked-in source contract rather than duplicated in the
workflow.

The contract disables all ordinary FFmpeg components and autodetection, then
explicitly restores only the runtime path required by FM2001 startup media:

- native Windows Media Foundation and w32threads;
- the `ffmpeg` and `ffprobe` programs;
- file and pipe protocols;
- EA input plus MOV/MP4 derivative input;
- source-bounded EA/TGQ decoders plus H.264/AAC derivative decoders;
- `h264_mf` and native AAC encoders;
- internal `aresample` for AAC sample-format conversion;
- MP4 and null muxers.

No `--enable-lib*`, GPL, nonfree or version-3 mode is accepted.

## Binary audit

The built `ffmpeg.exe` and `ffprobe.exe` must:

1. report every source-contract configure argument;
2. expose every required decoder, encoder, demuxer, muxer, protocol and filter;
3. have no `--enable-lib*`, GPL, nonfree or version-3 configure flag;
4. be SHA-256 identified in the receipt;
5. import no MinGW/MSYS runtime DLL such as `libgcc_s_*.dll`,
   `libstdc++-6.dll`, `libwinpthread-1.dll`, `libssp-0.dll` or
   `msys-2.0.dll`;
6. preserve the exact source-license file hash.

The import guard deliberately allows native Windows system DLLs, including
Media Foundation. If the first build exposes an unexpected toolchain runtime
DLL, the proof fails closed and the build/link strategy must be corrected or
that dependency must be explicitly provenance-tracked.

## What a passing build does not prove

Even a green build receipt keeps all of these false:

- synthetic roundtrip verified;
- exact original `easp.tgq` / `premintro.tgq` verified;
- external Windows 11 visible/audible playback verified;
- source-material distribution complete;
- production migration ready;
- legal compliance claimed.

The private original-TGQ step remains the preferred next promotion test when
the authorized source archive can again be executed. Until those later gates
pass, the normal package continues to use the existing #468 fail-closed helper.
