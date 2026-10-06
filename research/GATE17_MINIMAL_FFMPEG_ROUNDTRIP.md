# Gate 17 minimal FFmpeg synthetic roundtrip proof

_Status: staged work-ahead. Do not treat this branch as evidence until the build-proof prerequisite is canonical and this proof passes on its own exact head._

## Purpose

The source/build proof establishes that a tightly bounded FFmpeg helper can be
compiled from the pinned source. This next proof asks a different question:
can that exact minimal helper execute the current FM2001 startup derivative
pipeline without adding test-only codecs or filters?

## Fixture boundary

The synthetic input is generated only inside CI by the already pinned broad
BtbN LGPL candidate. Its archive and extracted `ffmpeg.exe` must match the
hashes already recorded in
`third_party/ffmpeg-lgpl-candidate/SOURCE-CONTRACT.json`.

That broad executable is **not** a production migration candidate and is never
copied into the package by this proof. It is used only because it already has
`lavfi` source filters that can create a deterministic one-second 320x480
H.264/AAC fixture without widening the minimal helper.

## Minimal-helper path under test

The minimal helper receives a 320x480, 25 fps, H.264/AAC MP4 with 22050 Hz
stereo audio and must execute the production-shaped command:

- MOV/MP4 demuxing;
- H.264/AAC decode;
- exact recovered `scale=640:480:flags=neighbor` presentation transform;
- Media Foundation `h264_mf` video encoding;
- native AAC audio encoding;
- 22050 Hz stereo output;
- MP4 muxing;
- FFprobe validation;
- video and audio decode verification through the same null/pipe plumbing used
  by the runtime cache. Pinned FFmpeg `libavformat/nullenc.c` source-closes
  the null muxer's default output encoders as `wrapped_avframe` for video and
  `pcm_s16le` for audio on Windows, so the minimal helper retains those two
  internal encoders rather than treating the null muxer alone as sufficient.

The roundtrip receipt is bound to the SHA-256 identities from the immediately
preceding minimal build proof.

## What success means

A passing receipt may set:

- `build_verified=true`;
- `synthetic_roundtrip_verified=true`.

It must still keep all of these false:

- exact original TGQ verified;
- external Windows 11 visible/audible playback verified;
- source-material distribution complete;
- production migration ready;
- legal compliance claimed.

The next promotion boundary after this synthetic proof remains exact
`easp.tgq` / `premintro.tgq` conversion with the authorized private source,
followed by real Windows 11 playback acceptance.
