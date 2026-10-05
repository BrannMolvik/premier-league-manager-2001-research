# Gate 14 FastView surfaced resource loading

_Status: independent Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Result

The source-closed FastView surfaced-resource plan now has two additional
read-only layers:

1. a fixed-Premier-League adapter that consumes an existing immutable fixture
   row and applies the source-proven Match `+0x48 == -1` rule;
2. a verified original-source loader that consumes only the resulting selection
   plan.

The loader does not select clubs, months, badge variants, background variants,
or fallback order independently.

## Fixed Premier League adapter

Fixed League builder `0x6173D0`, callsite `0x617490`, passes literal
`-1` as Match constructor argument 4. Base Match stores this at `+0x48`.

Therefore ordinary fixed Premier League matches have no explicit background
club override. The adapter converts that proven source sentinel to the pure
selection layer's explicit `None`, which means helper `0x514220` falls
back to the home side.

The adapter reads only:

- scheduled fixture date;
- home club id;
- away club id;
- existing clean-room club/country art fields.

It does not mutate match or management state.

## Verified source-root loader

`load_verified_fastview_surfaced_resources()` requires:

- an exact `FastViewSurfacedResourceSelection`;
- an original-game source root;
- the canonical original executable.

The canonical executable is passed through both existing verifier-backed
extractors:

- `tables_from_original_executable()`;
- `quantization_from_verified_executable()`.

The loader then tries only the already recovered source candidate lists in
their existing order.

For the full background it tries:

1. club `backgroundN`;
2. club unsuffixed `background`;
3. generic-tier `backgroundN`.

If all three are missing, loading stops. The unresolved native terminal
background fallback is not replaced with another guessed file.

For each badge it tries:

1. exact club `badge_2`;
2. exact generic badge fallback.

Every selected original resource retains:

- exact chosen source path;
- source byte count;
- SHA-256;
- decoded native geometry;
- decoded RGBA;
- transparent-pixel count.

The native geometry requirements are:

- background: **800x600**;
- home badge: **135x93**;
- away badge: **135x93**.

All decode passes use the repository's recovered EA444 implementation.

## Fidelity boundary

Promoted:

- fixed-Premier-League Match `+0x48=-1` adapter semantics;
- source-root path-attempt execution;
- exact chosen source identity and SHA-256 retention;
- canonical executable table/quantization verification;
- EA444 decode;
- strict native surfaced-resource geometry.

Still false:

- unresolved terminal background fallback semantics;
- staging every surfaced resource in Git;
- lifting surfaced pixels into the FastView component/overlap model;
- flattened complete FastView output;
- Gate 14 completion.

## Next step

Use the verified decoded surfaced-resource set as one explicit FastView raster
component family. Place the full 800x600 background at the first outer draw
rank and the home/away badge pixels at their recovered corner rectangles. Keep
cross-component overlaps fail-closed through the existing overlap model until
the native packed-pixel blend/output boundary is completed.
