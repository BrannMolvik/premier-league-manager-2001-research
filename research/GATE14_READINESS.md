# Gate 14 readiness audit

_Status: fail-closed roadmap audit while Gate 13 remains Codex-owned._

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

## Source-backed capabilities already retained

The current audit records these solved sub-capabilities:

- completed human outcome -> resolved-only FastView -> Tk draw path;
- dynamic PlayerRow energy pixels;
- English PlayerRow text pixels;
- source-closed relative draw order across the currently rasterized FastView component families;
- the source-closed two-row GoalFlash receiver/control/formatting contract, while its absolute placement and pixels remain explicitly absent;
- the source-closed one-instance ScoreCompositeMain outer ownership/control-order contract, while its branch geometry/content and pixels remain explicitly absent;
- native packed-16 font destination read, alpha endpoints, /256 mask-wise blend rule and color-key behavior;
- ownership and selected playback entrypoints for the four canonical BNK banks;
- chant pool selection and timing arithmetic.

These facts are useful progress but are not sufficient to close either open
roadmap criterion.

## Current blockers

The audit exposes the unresolved capabilities directly:

- exact audio event/sample binding;
- audible Windows output and login/menu audio integration;
- GoalFlash absolute timing/position;
- GoalFlash pixel rasterization and resolved-composite integration;
- ScoreCompositeMain exact geometry and pixel rasterization;
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
  energy/text pixels, the source-closed GoalFlash contract, absolute GoalFlash
  placement, GoalFlash rasterization, the source-closed ScoreCompositeMain
  contract, exact ScoreCompositeMain geometry/pixels, global z-order and the
  already source-closed font blend prerequisite are all satisfied;
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
