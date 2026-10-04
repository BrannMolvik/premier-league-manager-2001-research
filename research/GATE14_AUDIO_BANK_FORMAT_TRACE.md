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

## Recovery 273: bounded instruction/dataflow candidate inventory

The tracer can now optionally classify only the already-bounded loader/playback
windows into instruction facts that materially narrow manual BNK-format analysis:

- direct `CALL rel32` targets;
- immediate operands;
- memory operands with base register, index register, scale, displacement and
  operand width.

Every retained row is labeled
`bounded_linear_bnk_dataflow_candidate_not_cfg_or_format_proof`. The
classifier does not decide whether an offset belongs to a bank object, file
header, sample-table row, decoder state or unrelated stack/local storage. A
direct call target is likewise not assigned a file-I/O, allocation, decoder or
playback role without control-flow/data-flow adjudication.

This reduces the next private pass from reading broad linear disassembly to
examining concrete record-layout and call candidates while keeping all BNK
header/table/codec/decode flags false.

## Shared-offset triage boundary

A follow-up correlator can group equal non-stack memory displacements that recur
across at least two distinct bounded loader/playback windows. This is useful for
prioritizing candidate shared record fields because the same displacement is
observed in multiple source-qualified neighborhoods.

The correlator deliberately excludes `esp`/`ebp` operands so unrelated
stack-frame locals cannot become false cross-window evidence. It retains operand
width, window labels, base-register identities and instruction VAs.

A repeated displacement still does **not** prove that two instructions reference
the same object, that the field belongs to a BNK header/sample row, or that its
meaning is an offset/length/codec/rate/channel value. Every grouped record is
labeled
`shared_bnk_memory_displacement_candidate_not_object_or_field_proof`.

## Shared-call triage boundary

A second correlator groups exact direct-call targets that recur across at least
two distinct bounded loader/playback windows. This identifies common helper
targets worth manual control-flow analysis and preserves every source callsite
VA plus the windows in which the target recurs.

A repeated call target still does **not** prove a function role. It is not
automatically a file-I/O routine, allocator, decoder, sample lookup, playback
routine or bank-record accessor. Each grouped result is labeled
`shared_bnk_direct_call_target_candidate_not_function_role_proof`.

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
