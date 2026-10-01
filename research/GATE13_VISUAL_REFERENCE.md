# Gate 13 Visual Reference

_Date: 30 September 2026_

## Purpose and evidence boundary

The authorized FM2001 disc/archive remains the canonical source for resources.
This note records **secondary visual evidence only** as a visual cross-check.
The earlier exact-asset extraction blocker has since been cleared on local
Windows: the source-backed PStartMenu/TeamSelect first-screen resource slice,
Button state mapping and PStartMenu Zurich caption geometry are now primary
evidence. The screenshots below remain useful only for whole-screen visual
recognition where primary evidence is still incomplete.

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
- primary executable evidence now binds all four PStartMenu event/control IDs,
  original English captions, action rectangles, 23-frame Button state mapping,
  centered Zurich line origins and native endpoint colors; see
  `research/GATE13_BUTTON_NATIVE_TRACE.md`;
- the secondary screenshot is no longer needed to establish those exact
  first-screen facts, but remains a useful whole-screen visual cross-check.

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
- TeamSelect Back/Start control rectangles and the shared 23-frame action atlas
  are now primary source/executable evidence;
- hierarchy row origins and source-strip art are also recovered, but the
  country/league/club item mapping, row hit behavior and selection-state
  semantics remain unresolved and must not be inferred from this screenshot.

Again, the 512x512 web representation is not a canonical 800x600 layout dump.
Do not derive hard-coded production coordinates from it.

## Gate-13 implementation consequence

The first-screen acceptance target is now mostly primary-evidence-backed rather
than screenshot-led:

1. use the provenance-imported shipped backgrounds/action atlases and original
   Zurich/English resources;
2. preserve the recovered PStartMenu action rectangles, all four captions,
   native Button groups/animation direction and caption line origins;
3. transition through the proven TeamSelect Back/Start controls while keeping
   hierarchy item identity/hit semantics fail-closed until recovered;
4. keep all simulation behind the presentation/application boundary already
   introduced in `reconstruction/front_end_state.py`;
5. verify the integrated source-backed presentation in a real Windows 11
   graphical run before promoting first-screen fidelity.

The screenshot remains noncanonical for exact pixels/coordinates. Remaining
first-screen gaps are TeamSelect hierarchy semantics and Windows graphical
validation, not missing PStartMenu asset names/rectangles/fonts/button states.
