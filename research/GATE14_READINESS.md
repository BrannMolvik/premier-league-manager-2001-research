# Gate 14 readiness audit

_Status: fail-closed active Gate-14 roadmap audit after Gate 13 closure._

## Purpose

Gate 14 now contains many independently source-backed presentation layers. A
single readiness contract is needed so partial renderer/audio advances cannot be
mistaken for Gate completion.

`gate14_readiness.py` maps current canonical evidence to the four official
`ROADMAP.md` completion criteria:

1. match presentation consumes reconstructed match state/events;
2. original login/menu music and applicable sound resources are integrated or
   converted for the modern runtime;
3. a match is recognizably presented in the style/workflow of the original;
4. presentation fidelity does not block core management play.

## Current canonical result

Two criteria are currently satisfied by architecture already on `main`:

- reconstructed match state/events feed the presentation path;
- presentation remains separated from core management play.

Two criteria remain open:

- original audio integration;
- recognizable original match presentation.

The audit therefore requires `gate14_ready=false`.

## Recovery 313 capability reconciliation

Three player-visible/runtime seams are now canonical without promoting either
open roadmap criterion:

- **First-screen press audio is bound on Windows.** The source-backed
  PStartMenu/TeamSelect Button press route delivers numeric
  `AudioHooks(10, 0, 0x40)` to canonical `menus.bnk` slot 2 through the
  in-memory Windows PCM backend. This is a real source event binding for that
  bounded Button path, but the broad readiness field
  `audio_event_binding_recovered` remains false because it represents the
  still-unrecovered semantic/application-wide login/menu audio boundary.
  Human-heard bound-path Windows evidence is also still absent.
- **Default startup FMVs are integrated on normal Windows launch.** The exact
  original `easp.tgq` / `premintro.tgq` files are revalidated, converted
  once into a private verified H.264/AAC cache, rehashed on reuse, and played
  through the built-in synchronous Windows MCI backend. Hosted Windows package
  CI proves packaging and runtime construction, not actual human-visible/
  audible playback, native skip input, fades, or exact display treatment.
- **Resolved FastView pixels have an operator-visible Tk surface.** An
  already-built `HumanFastViewResolvedPresentation` can be shown in a native
  800x600 child window using its canonical resolved-preview PNG unchanged.
  Unresolved overlap pixels stay transparent. No source navigation trigger is
  invented, so ordinary management play does not automatically enter this
  window yet.

The readiness model records these separately as
`first_screen_press_audio_bound`,
`startup_media_default_windows_path_integrated`,
`startup_media_real_windows_verified`,
`operator_visible_resolved_fastview_surface`, and
`source_fastview_navigation_trigger_recovered`. Their canonical values are
true, true, false, true, and false respectively.

## Source-backed capabilities already retained

The current audit records these solved sub-capabilities:

- completed human outcome -> resolved-only FastView -> Tk draw path;
- operator-visible 800x600 Tk child surface for that exact resolved preview,
  without an invented source navigation trigger;
- default Windows startup-media runtime/package path for the exact verified
  original startup TGQs;
- live source-backed first-screen Button press PCM binding on Windows;
- dynamic PlayerRow energy pixels;
- English PlayerRow text pixels;
- source-closed parameterized FastViewScores and FastViewTeam nested construction/count algorithms;
- source-closed relative draw order across the currently rasterized FastView component families;
- the source-closed two-row GoalFlash receiver/control/formatting contract, while its absolute placement and pixels remain explicitly absent;
- the source-closed one-instance ScoreCompositeMain outer ownership/control-order contract, while its branch geometry/content and pixels remain explicitly absent;
- the source-closed four-control embedded outer registration/constructor/order contract, while their roles, geometry/resources/state behavior and pixels remain explicitly absent;
- native packed-16 font destination read, alpha endpoints, /256 mask-wise blend rule and color-key behavior;
- ownership and selected playback entrypoints for the four canonical BNK banks;
- chant pool selection and timing arithmetic.

These facts are useful progress but are not sufficient to close either open
roadmap criterion.

## Current blockers

The audit exposes the unresolved capabilities directly:

- broad semantic/application-wide audio event/sample binding beyond the
  bounded first-screen Button press route;
- human-heard bound-path Windows output and full login/menu audio integration;
- real-Windows startup-FMV visibility/audibility plus native skip/fade/display
  fidelity;
- a source-backed ordinary runtime trigger into the operator-visible FastView
  presentation surface;
- complete FastViewScores/LeagueTable nested pixels;
- complete FastViewTeam nested pixels beyond the already-complete retained PlayerRows;
- GoalFlash absolute timing/position;
- GoalFlash pixel rasterization and resolved-composite integration;
- ScoreCompositeMain exact geometry and pixel rasterization;
- four embedded outer controls' exact geometry and pixel rasterization;
- global FastView z-order across omitted/unbound layers;
- a complete FastView frame;
- chant event semantics;
- source-backed 3D choreography;
- final recognizable-original-workflow verification.

The audit deliberately does not convert this list into a percentage. Completion
remains criterion-based.

The font blend rule is now source-closed, but this does **not** mean the current
masked overlap pixels are resolvable. The original blend operates in the active
runtime 16-bit packed surface format. An actual runtime mask-value receipt and
an exact packed-16 to modern-RGBA expansion boundary still remain prerequisites
for emitting those pixels.

## Fail-closed guards

The data model rejects invalid promotion paths. In particular:

- login/menu audio cannot be declared integrated before bank ownership,
  playback entrypoints and sample decode are ready;
- a complete FastView frame cannot be asserted before the resolved human path,
  energy/text pixels, complete score/team subpanel pixels, the source-closed
  GoalFlash contract, absolute GoalFlash placement, GoalFlash rasterization,
  the source-closed ScoreCompositeMain
  contract, exact ScoreCompositeMain geometry/pixels, the source-closed four-
  control embedded outer contract, exact embedded-control geometry/pixels,
  global z-order and the already source-closed font blend prerequisite are all
  satisfied;
- recognizable original workflow cannot be asserted without at least one
  completed source-backed match presentation path.

This audit does not change presentation behavior. It only makes the current
Gate-14 closure boundary machine-checkable.

## GoalFlash omission guard

The source contract merged from the canonical executable proves the two
GoalFlash rows, their three typed receiver families, five style-1 text controls
per row, exact relative cell geometry/flags, normal-goal formatting shape, and
penalty-shootout suffix/highlight behavior. That is sufficient to prove that
GoalFlash is a real visible FastView family, but not sufficient to place its
pixels on the 800x600 frame.

The readiness model therefore carries three separate facts:

- `goalflash_source_contract_recovered = true`;
- `goalflash_absolute_position_recovered = false`;
- `goalflash_pixels_rasterized = false`.

This distinction is deliberate. A resolved-only composite with zero remaining
pixel overlaps is still not a complete original frame while a source-backed
visible family is omitted. Future GoalFlash work must recover the absolute
mover/timing position and produce source-backed pixels before
`complete_fastview_frame_recovered` can become true. The unresolved
EventGoal field labels remain neutral and are not prerequisites invented by
this readiness guard.

## ScoreCompositeMain omission guard

The exhaustive outer registration trace also proves a separate visible
`ScoreCompositeMain` family. Exactly one of three owner branches constructs
it through `0x51B400` or `0x51B330`, both flowing through
`ScoreComposite::0x51A730`. The shared builder appends one PictureControl and
four TextControls at outer ranks 16..20.

That evidence does **not** justify borrowing the already reconstructed
`ScoreCompositeNormal` LeagueScores row geometry. The two families have
different constructors and ownership paths. The readiness model therefore
carries:

- `scorecomposite_main_source_contract_recovered = true`;
- `scorecomposite_main_geometry_recovered = false`;
- `scorecomposite_main_pixels_rasterized = false`.

This keeps the complete-frame criterion false until the outer main composite's
own branch geometry/content and pixels are recovered from source.


## Embedded outer-control omission guard

The exhaustive outer registration trace proves four additional visible controls
that are not present in the current component raster set. The two pre-GoalFlash
objects live at parent offsets `+0x388/+0x3D4` and outer ranks 4/5; the
post-team loop contributes `+0x424/+0x478` at ranks 34/35.

Only their registration/constructor/order topology is currently source-closed.
No current evidence assigns their rectangles, resources, visible roles, control
state semantics or pixels. The readiness model therefore carries:

- `embedded_outer_controls_source_contract_recovered = true`;
- `embedded_outer_controls_geometry_recovered = false`;
- `embedded_outer_controls_pixels_rasterized = false`.

This is intentionally separate from `direct_chrome`, which contains only the
source-bound top-bar and ticker PictureControls. Complete-frame promotion must
remain false until these four omitted outer controls have their own exact
source-qualified geometry and pixels.


## Nested subpanel completeness guard

PR #366 source-closed the parameterized construction algorithms inside the two
nested wrappers. That evidence remains canonical and is now represented
separately from pixel completeness:

- `score_subpanel_parameterized_construction_recovered = true`;
- `team_subpanel_parameterized_construction_recovered = true`;
- `score_subpanel_complete_pixels_recovered = false`;
- `team_subpanel_complete_pixels_recovered = false`.

The distinction is required by the renderer contracts already on `main`.
`FastViewScoreTableStaticPlane` explicitly carries
`text_rasterized=false` and `complete_component=false`. The retained
PlayerRow compositor explicitly carries `complete_team_table=false`, because
it covers PlayerRow controls rather than all TeamTable-level children. The
nested-order contract separately proves six TeamTable-level controls before the
PlayerRow subtrees.

Accordingly, `complete_fastview_frame_recovered` now requires both nested
subpanels to be pixel-complete. This does not reopen the source-closed row-count
or phase-tail algorithms. It prevents their structural recovery from being
mistaken for complete visible output.
