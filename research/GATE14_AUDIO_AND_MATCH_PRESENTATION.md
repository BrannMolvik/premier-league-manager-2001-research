# Gate 14 Audio and Match Presentation

_Last reconciled: 3 October 2026 KST, Recovery 194_

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

Recovery 194 rematerialized the authorized source, reproduced the full
2,456-file / 211-folder Joliet inventory, and revalidated the canonical
executable hash. The canonical executable itself embeds the full paths for the
bounded seven-resource family, so
`reconstruction/gate14_fastview_resource_catalog.py` schema 2 now resolves
those **source-proven exact paths** rather than relying on basename uniqueness:

- `FastViewTeam` / `TeamTable`: `FM2001_Art/FastView/team_bar_1.444`,
  `FM2001_Art/FastView/blank_bar.444`,
  `FM2001_Art/FastView/team_bar_2.444`;
- `PossessionDiagram`: `FM2001_Art/FastView/pitch_left.444`,
  `FM2001_Art/FastView/pitch_middle.444`,
  `FM2001_Art/FastView/pitch_right.444`,
  `FM2001_Art/FastView/pitch_normal.444`.

This matters because the real disc also contains
`FM2001_Art/Generic/match_report/pitch_normal.444`. The executable separately
embeds both paths, proving that the FastView component owns the FastView copy.
The resolver now fails closed on a missing exact path, wrong source size, or a
conflicting observed hash; a same-basename file elsewhere cannot substitute.

The same trace closes the bounded `PossessionDiagram` pixel geometry and
single-call territory update primitive. Constructor `0x5227D0`, called from
the FastView owner at `0x5206CD`, places the normal 294×78 pitch at
`(253,139)-(547,217)`. State 1 is initially active; left/middle/right
overlays use exact x offsets `[0,98,169]`. Update `0x522BB0` uses a private
MSVC-style presentation RNG and the EventPossession territory byte to choose
the next state. The original callback cadence and side-0/user orientation are
still intentionally unrecovered. See
`research/GATE14_FASTVIEW_POSSESSION_SOURCE_TRACE.md` and
`reconstruction/gate14_possession_diagram.py`.

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


Recovery 196 deliberately stages the four exact PossessionDiagram EA444 files
under the provenance-controlled original-assets tree and adds a checksum/size/
geometry validator plus an exact layer-placement adapter. The same fresh
executable trace closes the three PossessionFigures 40x18 percentage text
rectangles: side 1 is left at (311,181)-(351,199), neutral is centered at
(382,181)-(422,199), and side 0 is right at (454,181)-(494,199). This is a
source-index mapping only; which match side is the human user's screen side is
still unproven and remains fail-closed. Recovery 198 rejects the earlier bar-to-PossessionFigures association: RTTI and
constructor flow bind the 82x16 `team_bar_1` / `blank_bar` / `team_bar_2`
family to `FastViewPanel::FastViewTeam` / `TeamTable`, while
`PossessionFigures` remains the separate text-only component at `0x51E7E0`.

Recovery 198 also source-closes the bounded diagram's typed receiver lifecycle.
The FastView owner registers `PossessionDiagram` for EventPossession,
EventGoal, and EventGlobalPenalties. Goal source field `+0x0C` values 0/1
snap to diagram states 2/0. Global penalties latches object byte `+0x20`;
subsequent possession callbacks force state 1 without consuming presentation
RNG. The exact MatchController EventPossession emission cadence is still
unrecovered, so no runtime scheduler frequency is inferred.

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

Recovery 194 revalidated and enumerated the exact Library source successfully,
so the earlier process-start infrastructure blocker is no longer current.
This recovery concentrated first on the source-closed FastView presentation
family. The complete 64-bank audio inventory remains available for the next
trace, but no bank/sample role is inferred from filenames alone.

Existing startup-FMV evidence remains valid. New menu/login or match-audio bank
semantics still require executable ownership/callsite evidence for the exact
bank/sample resource before integration.

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

Verify the Recovery-194 exact-path resolver and PossessionDiagram primitive
through full CI. The four diagram paths, source identities and bounded pixel
geometry are now source-closed, so after that checkpoint deliberately stage
only those exact authorized assets under `original_assets/` using the existing
asset-policy import path, then connect the diagram to a player-visible
presentation surface **without** inventing update cadence or side orientation.

Continue the smallest source-backed player-visible FastView slice: keep
PossessionFigures percentage text and PossessionDiagram geometry separate from
the now-corrected FastViewTeam bar family, then recover the original
PossessionDiagram callback cadence or a source-backed presentation-host lifecycle
without inventing human-side orientation. Gate 13 remains the
earliest incomplete validation gate and Gate 14 remains work-ahead, not passed.
