# Gate 14 FastView white-endpoint ClockControl raster

_Status: stacked follow-on to the ClockControl source-state checkpoint. Gate 13 remains the earliest incomplete validation gate._

## Purpose

ClockControl has two source color classes:

- native endpoint `0xFFFF`, whose all-bits-on value maps exactly to white in
  the existing endpoint-only text path;
- RGB8 alert input `(255,45,45)`, which the original converts into the active
  runtime packed-16 format before drawing.

The second path still depends on an observed runtime mask layout and the
unresolved packed-16 to modern-display expansion boundary.

This checkpoint therefore renders **only** ClockControl states whose exact
modern color is already source-safe. It refuses the alert color rather than
treating source RGB8 as proof of final modern RGBA.

## Source inputs reused

The raster uses only evidence already closed by the ClockControl state trace:

- TextControl rectangle: `(439,44)-(621,64)`;
- left/top text origin from render flags `0x0A`;
- style index 1;
- exact Zurich 18px source font:
  `Fonts/Zurich_BdXCn_BT_18pixel.fnt`;
- native white endpoint `0xFFFF`;
- exact ClockControl text state supplied by `FastViewClockState`.

No new text, position, phase meaning, or color is inferred here.

## Raster contract

`reconstruction/gate14_fastview_clock_raster.py` emits one transparent
800x600 plane named `clock_text`.

For the constructor's empty text it emits a zero-layer transparent plane.

For a non-empty white state it:

1. rasterizes the exact source text with the verified style-1 Zurich font;
2. uses line origin `(439,44)`;
3. clips every glyph pixel to the exact 182x20 ClockControl rectangle;
4. maps native `0xFFFF` only through the existing endpoint-white conversion;
5. retains source glyph alpha unchanged.

Examples that are eligible include:

- first-half numeric states before the alert threshold;
- `Half time`;
- the source second-half reset state `46 mins` after the second-half latch;
- later normal second-half numeric states before 91;
- `Full time`.

## Explicitly withheld states

A state is rejected whenever
`state.color.exact_modern_rgba_recovered == false`.

That includes:

- numeric 46+ before the second-half latch;
- numeric 91+ before the post-90 latch;
- `Extra time`;
- `Penalties`.

Those states use exact source RGB8 `(255,45,45)`, but that value is input to
the original packed-16 conversion rather than proof of the final display pixel.

The raster therefore does **not** simply write modern `#ff2d2d`.

## Fidelity boundary

This checkpoint closes only a partial ClockControl pixel plane.

It keeps false:

- alert-color modern RGBA recovery;
- alert-colored clock raster availability;
- integration into the current FastView component set;
- global FastView z-order;
- flattened overlap output;
- complete FastView frame;
- Gate 14 completion.

The next safe step after verification is to integrate this white-only clock
plane into component/overlap accounting at its already source-closed outer
position, while carrying its partial-state limitation explicitly. Full clock
coverage still requires the runtime packed-16 display boundary.
