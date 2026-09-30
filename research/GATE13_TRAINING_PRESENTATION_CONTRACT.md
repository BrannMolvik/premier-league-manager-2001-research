# Gate 13 Training Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes already recovered original training-system identities,
record layout and method semantics into the Gate-13 read-only presentation
seam. It does not claim a complete original Training screen.

## Source module and screen-class boundary

The original executable retains the source path:

`D:\Projects\FM2001\Applications\FootballManager\Training.cpp`

The persisted research used for this checkpoint does **not** independently pin
a Training-screen RTTI class/vtable. The contract therefore records
`screen_class_name = None`. It must not be replaced by a guessed class name
because the subsystem source module and a particular presentation panel are not
the same claim.

## Native per-user training records

The recovered DBRUser-owned training store contains exactly **40 records** of
`0xC8` bytes each.

Per whole record:

- `+0x08` = player ID;
- `+0x24` = embedded training object.

Inside the embedded object:

| Offset | Proven state |
| ---: | --- |
| `+0x00` | training method ID |
| `+0x04` | repeating eight-week countdown |
| `+0x08` | active training-step count |
| `+0x0C` | start of 17 one-byte per-skill counters |
| `+0x20` | start of 17 paired dword states |
| `+0x64` | start of seven per-method result counters |

Constructor `0x4EAB80` initializes:

- method ID **5**;
- countdown **8**;
- active count **0**;
- skill counters to zero;
- paired skill-state dwords to one;
- seven method-result counters to zero.

## Seven recovered methods

Profile builder `0x4EAA00` creates seven contiguous 17-byte vectors.
Selector `0x4EA9A0` gives the exact method mapping:

| Method | Recovered semantics | Profile vector | Weekly RNG draws |
| ---: | --- | ---: | ---: |
| 0 | rest/recovery | 4 | 0 |
| 1 | attacking | 0 | 4 |
| 2 | midfield | 2 | 4 |
| 3 | defensive | 1 | 4 |
| 4 | goalkeeper | 3 | 4 |
| 5 | fitness | 5 | 6 |
| 6 | technique | 6 | 4 |

The draw counts are derived from the proven nonzero profile slots visited by the
weekly updater. They are included to pin method identity and source behavior,
not as a presentation animation/timing claim.

Coach dispatcher `0x42C240` independently agrees with the recovered method
semantics through the specialist employee lookups.

## Source update chain

The normal weekly user path is:

`0x42AE40 -> 0x61CBA0 -> 0x61C520 -> 0x4EACE0`

where `0x61CBA0` walks all 40 records and `0x61C520` applies the recovered
eligibility checks before entering the training update.

Daily training-record maintenance is rooted at `0x61CA60` and occurs before
the Saturday active-training update in the recovered DBRUser calendar order.

## Read-only presentation boundary

`ManagementSourceDataBridge.training_rows()` already exposes the controlled
club's source-roster order, current method ID, countdown, active count, all 17
skill counters, all 17 state dwords and all seven method-result counters.

The new contract supplies original-system identity/shape for those fields. It
does not mutate training state or recalculate simulation behavior.

## Explicit non-claims

The contract contains no:

- original Training screen class or numeric screen ID;
- control/widget IDs;
- proof that the semantic method names are bound to particular visible control
  rectangles;
- row/column geometry;
- artwork/resource paths;
- font/color/alignment rules;
- navigation edges.

Those remain open Gate-13 presentation work.

## Gate 13 consequence

Training now has a source-proven method/record presentation contract attached to
the existing read-only player-training rows. The original Training screen's
visual resources, controls, geometry and navigation remain unresolved.
