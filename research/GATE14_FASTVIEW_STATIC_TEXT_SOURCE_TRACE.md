# Gate 14 FastView score/table static-text private source trace

_Status: cloud-safe evidence tooling; Gate 13 remains the earliest incomplete validation gate._

## Purpose

The nested score/table geometry already proves a large visible family of static
TextControls:

- four ScoreCompositeNormal TextControls per visible LeagueScores row;
- seven LeagueTable heading TextControls;
- nine TextControls per displayed LeagueTable row.

Their rectangles and source order are known, but their final values/meanings and
constructor style/font/color arguments are deliberately not claimed. The next
honest step requires the canonical executable rather than football-UI guesses.

## Exact bounded targets

The tracer records private bounded source windows at:

- ScoreComposite shared base constructor `0x51A730`;
- LeagueTable Row constructor `0x51D730`;
- LeagueTable Heading constructor `0x51DCB0`;
- generic TextControl constructor `0x527960`;
- generic text style selector `0x527BA0`;
- generic text draw neighborhood `0x64F090`.

The first three owner windows are also linearly decoded for **direct CALL
candidates** to `0x527960`.

For every candidate, the report preserves bounded preceding instructions for
manual adjudication. Those instructions are explicitly not labeled function
arguments. Stack/register values near a call cannot become style, color, text or
semantic evidence without control-flow and calling-convention analysis.

## What remains false

The emitted private report keeps all of these false:

- constructor argument positions recovered;
- user-facing text semantics recovered;
- final text values recovered;
- font/style/color recovered;
- static text pixels rasterized;
- complete score-subpanel pixels;
- global FastView z-order;
- complete FastView frame;
- Gate 14 completion.

## Exact private follow-up

On a healthy canonical-executable path:

1. run this trace with `--disassemble`;
2. verify the direct TextControl callsites in each owner constructor;
3. establish the generic TextControl calling convention/parameter ownership;
4. trace only source-supported style/color/font/value producers backward;
5. persist semantic/value conclusions only where that data-flow is unambiguous;
6. rasterize the controls only after the relevant source font, style and values
   are exact.

Generated source bytes/disassembly remain outside Git.
