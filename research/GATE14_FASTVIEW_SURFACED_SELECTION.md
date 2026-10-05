# Gate 14 FastView surfaced resource selection

_Status: independent source-backed Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Result

The source-closed FastView background/badge selectors now have a pure clean-room
binding layer. One already-known match can be reduced to exact source-resource
attempts without loading original bytes or rerunning match simulation.

The selector requires, explicitly:

- the match calendar date;
- home club id;
- away club id;
- the original-equivalent Match `+0x48` override state.

The override state has no default. A caller must pass an integer club id or
explicit `None`. `None` means the caller knows the override is absent,
therefore original helper `0x514220` falls back to Match `+0x14`, the
source-proven home side.

## Existing clean-room fields

No new club-art database is introduced.

The binding reads the already reconstructed fields:

- `Club.graphics_basename`;
- `CountryDefinition.graphics_directory`;
- `Club.fan_base_index`.

The final field is now instruction-level bound to the original background
fallback branch.

Master.dat reader `0x4022D0` consumes exactly **94 source bytes** before its
four-byte read into expanded DBRClub `+0x70`. Runtime import `0x403660`
preserves that field. The clean-room database already reads packed
`Master.dat +94` as `Club.fan_base_index`.

Therefore the generic background tier thresholds recovered from
`DBRClub+0x70` bind directly to `Club.fan_base_index` rather than a newly
invented value.

## Selection output

`build_fastview_surfaced_resource_selection()` produces one immutable plan
containing:

- the source-backed home, away and selected background club art identities;
- the exact seasonal background variant;
- the three background attempts in native order:
  1. club `backgroundN`;
  2. club unsuffixed `background`;
  3. `genericTier_backgroundN`;
- the exact club `badge_2` path plus generic badge fallback for home;
- the same pair for away.

The plan carries no source bytes. It also keeps the unresolved terminal
background fallback separate instead of replacing it with a guessed file.

## Fidelity boundary

Promoted:

- clean-room `Master.dat +94` / DBRClub `+0x70` binding;
- date -> seasonal variant binding;
- home/away -> badge path binding;
- explicit override-or-home -> background path binding;
- all currently recovered source file attempt order.

Still false:

- original source file loading;
- EA444 decode of these selected resources;
- surfaced-resource raster planes;
- cross-component complete-frame output;
- Gate 14 completion.

## Next step

Add a verified source-root loader that consumes **only this selection plan**.
For each family it must try the source paths in the recovered order, fail closed
when all source-backed attempts are absent, decode the selected EA444 resource
through the existing verified executable tables/quantization, and retain exact
chosen path plus byte identity. That layer must remain separate from component
composition.
