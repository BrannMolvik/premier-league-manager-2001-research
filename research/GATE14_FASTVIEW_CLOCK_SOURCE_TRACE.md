# Gate 14 FastView ClockControl source state

_Status: independent Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Result

The original FastView clock is now source-closed as a typed event-driven text
state machine rather than only a numeric GlobalTick bridge.

ClockControl owns one generic TextControl at object offset `+0x18` and six
typed receiver bases:

| Receiver | Object offset | Vtable | Callback |
| --- | ---: | ---: | ---: |
| EventGlobalTick | `+0x00` | `0x7CA468` | `0x51EDB0` |
| EventGlobalHalfTime | `+0x04` | `0x7CA45C` | `0x51EEE0` |
| EventGlobalSecondHalf | `+0x08` | `0x7CA450` | `0x51EFB0` |
| EventGlobalFullTime | `+0x0C` | `0x7CA444` | `0x51EFD0` |
| EventGlobalExtraTime | `+0x10` | `0x7CA438` | `0x51F0A0` |
| EventGlobalPenalties | `+0x14` | `0x7CA42C` | `0x51F170` |

MSVC RTTI class-hierarchy descriptors directly identify those six receiver
types beneath `ClockControl`; the event names are not inferred from the text.

## TextControl construction

ClockControl constructor `0x51EB90` creates the visible TextControl at
`0x51EC30 -> 0x527960`.

The exact control contract is:

- screen rectangle: `(439,44)-(621,64)`;
- style index: **1**;
- raw flags: `0x02`;
- generic forced render bit: `0x08`;
- final render flags: `0x0A`;
- native initial color: `0xFFFF`;
- initial text source at `0x874BA0`: empty string.

Because render flags `0x0A` contain neither the generic horizontal-center bit
`0x04` nor vertical-center bit `0x20`, the clock uses the source
left/top text origin. Style 1 is the already source-backed Zurich 18px text
family used elsewhere in FastView.

## Localization

The exact executable localization-global mapping already closed for
ScoreComposite labels also closes all ClockControl text globals.

| Clock text | Global | English.idx entry | STR id | Exact English |
| --- | ---: | ---: | ---: | --- |
| numeric suffix | `0x982384` | 2333 | 21532 | `mins` |
| half time | `0x98238C` | 2331 | 21530 | `Half time` |
| full time | `0x982388` | 2332 | 21531 | `Full time` |
| extra time | `0x9821F4` | 2433 | 21617 | `Extra time` |
| penalties | `0x9822D0` | 2378 | 20014 | `Penalties` |

Tests replay these entries against the provenance-tracked original
`English.idx` / `English.str` pair. No clock label is guessed from context.

## Numeric tick behavior

`EventGlobalTick` reads the event's first dword. It ignores value **0** and
also ignores ticks after the penalties latch is set.

Otherwise `0x51EDD0` formats:

`"%u %s" -> "<tick> mins"`

and writes that string into the one TextControl.

The same source value remains the one MatchIterator divides by five for the
already recovered possession-array index.

## Color/state transitions

ClockControl constructor initializes bytes `+0x6C/+0x6D/+0x6E` to zero.

The numeric formatter uses an exact source RGB8 alert input:

`(255,45,45)`

packed through the active runtime 16-bit channel metadata.

It selects that alert color when:

- tick is at least **46** and the second-half latch `+0x6C` is still zero;
- tick is at least **91** and the post-90 latch `+0x6D` is still zero.

Phase callbacks are exact:

- HalfTime: text `Half time`, native color `0xFFFF`;
- SecondHalf: set `+0x6C=1`, then directly render numeric **46**;
- FullTime: text `Full time`, native color `0xFFFF`, set `+0x6D=1`;
- ExtraTime: text `Extra time`, alert RGB8 `(255,45,45)`, set `+0x6D=1`;
- Penalties: text `Penalties`, alert RGB8 `(255,45,45)`, set `+0x6E=1`.

After the penalties latch, normal GlobalTick callbacks no longer replace the
display.

## Reconstruction contract

`reconstruction/gate14_fastview_clock.py` now exposes a pure
`FastViewClockState` transition model over the source events and exact
localized strings.

The native white endpoint remains usable by the existing exact endpoint text
path. The red-tinted source color deliberately remains represented as RGB8
input rather than a fabricated modern RGBA value.

This checkpoint therefore keeps false:

- exact packed16 value for the alert color without observed runtime masks;
- exact packed16-to-modern RGBA expansion;
- integrated ClockControl raster plane;
- global FastView z-order;
- complete FastView frame;
- Gate 14 completion.

## Next step

Once this checkpoint is verified, either:

1. add a partial clock raster that emits only states whose modern endpoint color
   is already exact and withholds alert-colored states; or
2. close the runtime pixel-format/display expansion boundary and raster the full
   clock state.

Do not turn source RGB8 `(255,45,45)` directly into an exact modern display
claim until that output boundary is closed.
