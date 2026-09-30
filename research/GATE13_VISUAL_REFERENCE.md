# Gate 13 Visual Reference

_Date: 30 September 2026_

## Purpose and evidence boundary

The authorized FM2001 disc/archive remains the canonical source for resources.
This note records **secondary visual evidence only** so that the first Gate-13
screen can be recognized and cross-checked while exact asset extraction is
temporarily blocked.

Do not copy these screenshots into `original_assets/`, do not treat their
resampled pixel coordinates as canonical layout data, and do not use them as a
replacement for recoverable shipped art.

Primary executable/resource evidence already proves that the original front end
uses an 800x600 `FM2001_Art/Generic/bground.444` resource. The source-disc
SHA-256 recorded in `research/EXECUTABLE_ANALYSIS.md` is:

`9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9`

## PStartMenu visual composition

Secondary screenshot:

https://www.old-games.com/screenshot/9027-1-f-a-premier-league-football.jpg

The screenshot visibly establishes the following composition:

- dark/cyan-blue technical-grid / wireframe-stadium background;
- large centered EA SPORTS / FOOTBALL MANAGER 2001 identity mark;
- a lower button row with:
  - `START NEW GAME`;
  - `CONTINUE`;
  - `LOAD GAME`;
- a centered lower button:
  - `QUIT TO WINDOWS`;
- pale blue active-button treatment and darker/disabled-looking button
  treatment.

Cross-check against executable evidence:

- this is consistent with the recovered initial `PStartMenu` family;
- screen ID `0x323` remains the proven front-end identity;
- event/control ID `2` remains the proven ordinary New Game transition;
- only **START NEW GAME -> event/control ID 2** is promoted as a recovered
  interaction mapping here;
- IDs/semantics for Continue, Load Game and Quit must still be recovered rather
  than inferred from their visible order.

The web copy is a 512x512 screenshot representation, whereas the shipped
background resource is proven 800x600. It is therefore suitable for visual
composition and labels, **not exact coordinates or scale**.

## TeamSelect visual composition

Secondary screenshot:

https://www.old-games.com/screenshot/9027-2-f-a-premier-league-football.jpg

The screenshot visibly establishes a distinct team-selection presentation:

- the same blue technical-grid visual family;
- a left competition/country hierarchy headed `F.A. PREMIER LEAGUE`;
- visible hierarchy rows including `ENGLAND`, `F.A. PREMIER LEAGUE`,
  `DIVISION 1 (ENG)`, `DIVISION 2 (ENG)`, `DIVISION 3 (ENG)`,
  `CONFERENCE`, `SCOTLAND`, `GERMANY`, `ITALY`, `SPAIN`,
  `FRANCE`, `HOLLAND`, and `BELGIUM`;
- the selected competition row highlighted in yellow;
- a central Premier League lion/competition identity panel;
- a horizontal `MAIN MENU` label/bar through the middle;
- a prominent `START GAME` action;
- pointer-icon instruction callouts including `RIGHT CLICK`, `LEFT CLICK`,
  `RIGHT OR LEFT CLICK`, `LOADING INFORMATION`, and team-selection/user
  pop-up instructions.

Cross-check against executable evidence:

- the screen is consistent with the recovered `PMain@TeamSelect` family;
- TeamSelect Back remains proven control/event ID `0x29`;
- TeamSelect Start/Continue remains proven control/event ID `0x2A`;
- the visual `START GAME` action is consistent with the recovered
  Start/Continue role, but exact rectangle/resource/control binding still
  requires source extraction before it is promoted as pixel/layout evidence.

Again, the 512x512 web representation is not a canonical 800x600 layout dump.
Do not derive hard-coded production coordinates from it.

## Gate-13 implementation consequence

The first recognizably original slice now has a visual acceptance target without
requiring a redesign:

1. reproduce the shipped blue/background visual family from authorized source
   assets;
2. reproduce the large original main-menu identity composition;
3. preserve the visible original PStartMenu labels and recovered New Game
   interaction;
4. transition into the original TeamSelect hierarchy/competition visual
   structure;
5. preserve proven control IDs `0x29` and `0x2A`;
6. keep all simulation behind the presentation/application boundary already
   introduced in `reconstruction/front_end_state.py`.

Exact asset names beyond `bground.444`, exact rectangles, fonts, control
states, and remaining PStartMenu control IDs remain source-extraction work.
