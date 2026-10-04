# Gate 14 BNK loader / sample-format source trace

_Status: disjoint Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

Executable ownership is now source-backed for the four core banks
`menus.bnk`, `game00.bnk`, `playercalls.bnk` and `Advice.bnk`, together
with selected native playback entrypoints. That still does not make the banks
playable in the clean runtime because their sample/header/codec structure has
not been source-closed.

Filename extensions or third-party format expectations are not accepted as
evidence.

## Bounded private trace

`gate14_audio_bank_format_source_trace.py` collects checksum-gated windows
around the already-qualified audio path:

- shared bank loader `0x6D01F0`;
- menus/game initialization `0x6D0160`;
- playercalls initialization `0x6D0250`;
- Advice initialization `0x6D02F0`;
- main audio-bank initialization `0x6D0AC0`;
- menus playback helper `0x6CFF10`;
- generic runtime SFX callback `0x6D0050`;
- Advice playback helper `0x6CFFA0`.

The next healthy private run should follow the loader's file reads/allocations
and the playback helper's sample lookup far enough to establish the exact record
layout shared between load and playback.

## Fail-closed boundary

The trace requires all of these to remain false until manually source-proven:

- bank header layout;
- sample table layout;
- sample offsets;
- sample codec;
- sample-rate/channel metadata;
- sample names;
- modern sample decode readiness;
- bank role semantics;
- event binding.

This checkpoint therefore accelerates the original-audio integration path
without claiming that any BNK content is decoded or playable.

No proprietary executable bytes, bank bytes, or generated disassembly belong in
Git.
