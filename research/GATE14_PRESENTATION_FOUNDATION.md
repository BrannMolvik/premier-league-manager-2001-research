# Gate 14 presentation foundation

_Date: 2 October 2026 KST_

## Status

This is **cloud-safe work ahead while Gate 13 remains the active validation
gate**. It does not mark Gate 14 complete and does not bypass the deferred
TeamSelect selection-record/Start-resolution trace or the upgraded real-Windows
first-screen audit.

## Source-backed startup media contract

`reconstruction/original_startup_media.py` turns the already verified startup
FMV research into a fail-closed source contract without checking proprietary
media into Git.

The exact startup order remains:

1. `FMV/easp.tgq` at startup callsite `0x530FAE`;
2. `FMV/premintro.tgq` at startup callsite `0x531175`.

Both use wrapper `0x461E20`. Their independently measured SHA-256 values,
sizes, 320x480 geometry, 25 fps video, 22,050 Hz stereo audio and decoded
frame counts are durable code constants. The differing wrapper flag bit 0 is
preserved neutrally as `playback_flag_bit0`; it is **not** renamed to
"skippable" because the precise user input semantics remain only probable.

`validate_original_startup_media()` accepts a deliberately supplied source
root and rejects size/hash mismatches. Hosted CI uses a synthetic contract
fixture; an opt-in original-source test can be enabled with
`FM2001_ORIGINAL_GAME_ROOT`.

## Fail-closed modern TGQ conversion contract

The same module now defines the first modern compatibility handoff without
claiming a playback integration.

`build_startup_media_conversion_plans()` first revalidates every supplied TGQ
against its exact original size and SHA-256, preserves the proven two-item
startup order, and returns deterministic non-overwriting FFmpeg argument lists.
The current compatibility target is deliberately narrow:

- MP4 container;
- H.264 video through `libx264`;
- `yuv420p` pixel format;
- source frame timing passed through rather than synthesized;
- AAC audio;
- original 22,050 Hz stereo geometry;
- `+faststart` for ordinary modern playback.

The planner does **not** launch FFmpeg. This keeps process execution and
provenance decisions outside the pure source contract.

After a caller performs the conversion,
`build_startup_media_ffprobe_args()` defines the required frame-counting
probe and `validate_startup_media_probe()` refuses the derivative unless it
has exactly one video and one audio stream, MP4/H.264/AAC structure, original
320x480 geometry, exact 25 fps timing, the original decoded video-frame count,
`yuv420p`, and 22,050 Hz stereo audio. It does not treat the MP4 as
bit-identical to the TGQ. Provenance remains anchored to the original TGQ
checksum that was validated before conversion.

This closes the repository-side **conversion contract**, not the player-visible
startup criterion. Still required before making a Gate-14 playback claim:

1. execute the private conversion/receipt runner against the authorized original TGQs on a healthy process allocation and retain its outside-Git receipt;
2. integrate a Windows playback surface that consumes only verified derivatives and preserves the proven startup order;
3. recover the exact input event(s) behind the longer FMV's bit-0 callback path;
4. verify transition/fade behavior on Windows 11.

No skip key, fade timing, scaling/interlace treatment or runtime player is
invented by this checkpoint.

## Match presentation feed boundary

`reconstruction/match_presentation_feed.py` establishes the Gate-14
simulation/presentation seam for matches.

It accepts the existing reconstructed timed `MatchEvent` stream and possession
segments and preserves:

- event object identity;
- event order and minute;
- possession records;
- running score derived only from already-resolved goal attribution.

It contains no match RNG, chance generation, simulation import, commentary
generator, sound mapping or animation selector. Reordered/invalid inputs fail
closed instead of being silently re-sorted.

This is groundwork for the Gate-14 criterion that match presentation consume
reconstructed match state/events rather than duplicate simulation logic. The
criterion should not be checked off until an actual player-visible match
presentation uses this feed.

## Remaining Gate-14 evidence/work

Still open:

- execute the merged private conversion/receipt runner against the source-backed TGQs when process execution is healthy;
- integrate original login/menu music and applicable sound resources;
- integrate the verified startup derivatives in the Windows runtime;
- recover exact startup skip/input and transition behavior;
- recover source-backed match presentation graphics/timing/audio mappings;
- connect a player-visible match presentation to
  `match_presentation_feed.py`;
- restore FastView/3D only to the evidence level practical for the port;
- verify presentation on Windows 11 without blocking the core management loop.

The earliest incomplete validation gate remains Gate 13.
