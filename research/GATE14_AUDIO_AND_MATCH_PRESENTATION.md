# Gate 14 Audio and Match Presentation

_Last reconciled: 2 October 2026 KST, Recovery 184_

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

### Completed-human adapter and bounded FastView shell

PR #130 merged the presentation-only completed-human adapter as
`393acb370c2164cff7c72fc552ebd84fbbeb6b37`. It preserves the existing
Premier League fixture ID or tagged primary-match reference and projects the
already-completed `user_result.events` / possession segments through the
semantic FastView feed. Full reconstruction CI run `37021083056` passed
**1,393 tests with 22 expected skips**; asset-policy run `37021083395`
passed.

PR #133 merged the next deliberately narrow shell as
`c1ea9ecd5e6bd50622cff4f2236d34ea6cb8cab3`.
Full reconstruction CI run `37022409513` passed **1,397 tests with 22
expected skips**; asset-policy run `37022409837` passed. The shell lives in
`reconstruction/fastview_semantic_shell.py` and is based only on persisted
original component evidence:

- `FastViewPanel` exists as the semantic event receiver/presenter layer;
- `ScoreComposite` is an original FastView component;
- `PossessionFigures` receiver `0x51EA80` prints the three possession values
  as `%u%%`.

The shell therefore exposes the existing event minute, running score and exact
recovered FastView sender name where one exists. Unmapped events retain
`sender_name=None`. It also exposes the original EventPossession record with
the exact three percentage strings and preserves the territorial value only as
raw data.

This is not yet the original visual FastView screen. Exact panel geometry,
side-0 screen orientation, commentary, audio mapping, territorial
left/middle/right thresholds and 3D choreography remain explicitly unrecovered
and are not synthesized by this layer.

Recovery 184 now adds
`reconstruction/gate14_fastview_resource_catalog.py` as the deterministic
bridge from persisted executable asset names to exact source-disc paths. The
target set is deliberately limited to the already-evidenced smallest visual
family:

- `PossessionFigures`: `team_bar_1.444`, `blank_bar.444`,
  `team_bar_2.444`;
- `PossessionDiagram`: `pitch_left.444`, `pitch_middle.444`,
  `pitch_right.444`, `pitch_normal.444`.

The resolver scans a saved full-disc inventory by exact case-insensitive
basename. It publishes a source path only when exactly one catalog entry
matches, carries an already-proven SHA-256 when available, and fails closed on
missing or ambiguous basenames. It explicitly leaves layout geometry, side-0
screen orientation and territorial thresholds unrecovered. No directory path
is inferred from the executable filename alone.

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

Verify the Recovery-184 FastView resource resolver through CI. With the current
process-start sandbox failure, fresh private execution is still required to run
the saved full-disc catalog through that resolver and to trace the exact
PossessionFigures/PossessionDiagram geometry. Do not import or place those
assets before both the unique source paths and placement semantics are proven.

Until that private execution path recovers, continue independent later-gate
cloud-safe testing or release-audit work under the deferred-blocker policy.
Gate 13 remains the earliest incomplete validation gate and Gate 14 remains
work-ahead, not passed.
