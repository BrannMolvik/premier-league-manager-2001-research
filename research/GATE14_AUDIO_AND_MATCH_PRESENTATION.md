# Gate 14 Audio and Match Presentation

_Last reconciled: 2 October 2026 KST, Recovery 183_

## Scope

Gate 14 restores FM2001's player-visible audio and match presentation on top of
the reconstructed gameplay state. Presentation code must consume existing
simulation output rather than recreate match decisions.

Gate 13 remains the earliest incomplete validation gate because a fresh
real-Windows schema-8 receipt is still pending. This file records independent
Gate-14 work-ahead only.

## Already source-backed

### Match presentation architecture

The original executable separates MatchCalculator from FastView/3D
presentation. Persisted binary evidence establishes these presentation routes:

- scored chance with normal attribution -> exact FastView
  `EventPlayerGoal`;
- scored chance with side inversion -> exact FastView
  `EventPlayerOwnGoal`;
- possession/territory payload -> exact `EventPossession`;
- MatchCalculator record types 6/7/8/9/10 -> FastView
  HalfTime / FullTime / ExtraTime / Penalties / Substitution sender families.

The exact class/event-string names for the five boundary/substitution sender
families above are not yet persisted, so reconstruction code must not invent
them.

Non-goal chance records and type-5 incidents currently have no separately
proven FastView sender identity in persisted evidence. They remain unlabelled
at the presentation-route layer even though their backend semantics are known.

`reconstruction/match_presentation_feed.py` is the read-only projection
boundary over already-created match events. Recovery 183 extends that feed
with only the semantic FastView mappings listed above.

### Startup FMVs

`research/STARTUP_PRESENTATION.md` source-binds:

- `FMV/easp.tgq`, SHA-256
  `73dc078ee8fe7e1d7412b4bcba072c3f8ec85546d5e5b94f90be9732498af97c`;
- `FMV/premintro.tgq`, SHA-256
  `a16e64a1c680ce1c7bcf57f76f05dd8e51a77663b5b4a673e681c9da188a0b0d`.

Both contain original EA ADPCM stereo audio at 22,050 Hz. The original startup
path calls the same FMV wrapper for both. A modern FFmpeg conversion of
`premintro.tgq` to H.264/AAC was already proven viable.

The clean host already contains an explicit verified-startup-media seam from
earlier Gate-14 work-ahead. Exact startup skip input and transition/fade
behavior remain open.

## 3D / FastView resource evidence

Persisted disc/binary research records:

- 235 loose `.SCI` files;
- `SCTABLE.STI` with 137 fixed 48-byte scenario-selection records;
- `AISCRIPT.VIV`, `MOAI.VIV`, and `GEN4TBLS.T` as BIGF archives;
- 584 motion/animation-named entries in `MOAI.VIV`;
- all 584 nonblank AISEQS secondary names map to those MOAI entries;
- plaintext `CAMERA.SCR`.

This proves the original 3D presentation layer is structured and data-driven,
but internal SCI choreography semantics are not yet decoded. Do not synthesize
an "original" 3D sequence from filenames alone.

## Audio/source inventory boundary

The canonical authorized source remains:

`/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`

Size: 511,121,336 bytes. SHA-256:
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.

Recovery 183 successfully rematerialized that exact Library file. However, the
current execution sandbox fails before starting even trivial archive-inspection
processes. Therefore this recovery cannot honestly add new loose-audio,
sound-bank, or cue-path filenames from fresh source enumeration.

The persisted verified Joliet inventory does establish one additional bounded
fact: the disc contains **64 `.bnk` files**. Their individual paths and runtime
semantics are not persisted here, so they remain neutral **bank candidates**
rather than being called music, commentary, crowd, UI, or match effects.

`reconstruction/gate14_audio_source_inventory.py` now makes the next healthy
private-source pass deterministic. It reads the existing ISO/Joliet or raw
MODE1/2352 catalog, records every `.bnk` path neutrally, separately recognizes
the two already source-bound startup TGQs, and emits an explicit semantic
boundary saying bank suffix/entry meanings are still unrecovered.

This is an infrastructure blocker, not a source-availability blocker. Existing
startup-FMV evidence remains valid. New menu/login or match-audio bank semantics
must wait for either:

1. a functioning local/private process path that can enumerate the verified
   Joliet source; or
2. already-persisted repository evidence that source-binds a concrete audio
   resource and its owner.

## Gate 14 completion status

- Match presentation consumes reconstructed state/events rather than
  duplicating simulation logic: **work-ahead in progress**, with a source-backed
  semantic feed boundary now present.
- Original login/menu music and applicable sound resources integrated or
  converted: **open**. Startup FMV audio conversion/playback feasibility is
  proven, but separate menu/login music and sound-bank ownership are not.
- A match recognizably presented in the original style/workflow: **open**.
  Semantic FastView routes and original 3D resource families are mapped, but
  original choreography is not yet decoded/integrated.
- Presentation fidelity does not block core management play: architectural
  separation is preserved; final criterion remains for Gate-14 audit.

## Exact next cloud-safe task

After the Recovery-183 semantic-feed checkpoint is verified, continue with the
smallest source-backed match-presentation shell that can display the recovered
semantic event stream without inventing commentary, sound cues, or 3D
choreography. If private execution recovers first, prioritize enumerating the
verified disc's audio/sound-bank files and tracing concrete menu/login ownership.
