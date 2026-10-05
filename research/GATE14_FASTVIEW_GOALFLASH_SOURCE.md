# Gate 14 FastView GoalFlash source contract

_Status: source-backed Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Result

The previously omitted outer `GoalFlash` family is now source-closed at the
receiver, control-layout, formatting and color-selection boundary.

MSVC RTTI proves `GoalFlash` has exactly three typed receiver bases:

- `Receiver<EventGoal>` at object offset `+0x00`, callback `0x51CD70`;
- `Receiver<EventScore>` at `+0x04`, callback `0x51CE80`;
- `Receiver<EventPenaltyShootoutShot>` at `+0x08`, callback `0x51CEA0`.

The outer owner constructs two identical flash rows through
`0x51C700 -> 0x51BE20`, so this family contributes ten direct FastViewPanel
TextControls.

## Exact five-cell row

Each child row uses style index **1**, already source-bound to:

`Fonts/Zurich_BdXCn_BT_18pixel.fnt`

The five controls have height 33 and form one 488-pixel row:

| Cell | Child offset | x offset | width | raw flags | final flags | alignment |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `+0x04` | 0 | 134 | `0x22` | `0x2A` | right / center |
| 2 | `+0x08` | 134 | 30 | `0x22` | `0x2A` | right / center |
| 3 | `+0x10` | 164 | 30 | `0x21` | `0x29` | left / center |
| 4 | `+0x0C` | 194 | 134 | `0x21` | `0x29` | left / center |
| 5 | `+0x14` | 328 | 160 | `0x1022` | `0x102A` | right / center |

Generic TextControl forces bit `0x08`. The generic renderer already proves
the right/left and vertical-center meanings above. The extra `0x1000` bit on
cell 5 remains deliberately unnamed.

Mover `0x51C5F0` applies the same row y coordinate to all five cells and x
offsets `0, 134, 164, 194, 328`. A source x value of `-1` takes the
existing hidden/sentinel branch.

## Normal goal row formatting

Formatter `0x51C230` writes:

1. first club display string;
2. unsigned numeric field A through exact `%u`;
3. unsigned numeric field B through exact `%u`;
4. second club display string;
5. exact shape: `" (" + event string + " " + event dword0 + ")"`.

The club strings are resolved from DBTClubs by callback `0x51CD70`. The
score receiver `0x51CE80` copies EventScore dwords `+0x0C/+0x10/+0x14/+0x18`
into GoalFlash state; the active goal formatter consumes the relevant pair.

The event's `+0x10` string and `+0x00` dword have not yet been assigned
human-readable semantic labels here. Their exact formatting is preserved
without calling them scorer/minute merely from appearance.

The EventGoal `+0x0C` value controls which club/score pair is drawn with
source active RGB **255,255,255** versus inactive RGB **0,0,0**.

## Penalty-shootout formatting

Penalty receiver `0x51CEA0` builds the same row record family.
Formatter `0x51C3F0` preserves the first four club/score cells and makes the
fifth cell:

- `event string + " scored"`; or
- `event string + " missed"`.

Those suffixes are literal source strings at `0x828FA4` and `0x828F9C`.

When a shootout shot is scored, the source side flag highlights the matching
club/score pair. When it is missed, all first four club/score controls are
inactive/black. The status cell remains separately rendered.

## Fidelity boundary

Promoted:

- all three GoalFlash receiver types and callback addresses;
- two-row ownership;
- all ten TextControl registrations;
- exact five-cell row geometry;
- style-1 source font identity;
- raw/final render flags and recovered alignment;
- normal-row exact string shape;
- penalty `scored` / `missed` suffix semantics;
- side-dependent active/inactive club-score coloring.

Still false:

- semantic names for EventGoal `+0x10` string and `+0x00` dword;
- the extra cell-5 flag `0x1000` meaning;
- absolute time-dependent GoalFlash screen position over its animation;
- GoalFlash pixel rasterization;
- complete FastView frame;
- Gate 14 completion.

## Next step

Trace the producer of EventGoal `+0x10` and `+0x00`, plus the GoalFlash
animation-state position function, before binding live reconstructed events or
rasterizing this dynamic family. Alternatively continue another omitted visible
outer family if that source route is more direct.
