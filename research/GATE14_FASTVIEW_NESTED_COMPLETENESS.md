# Gate 14 nested FastView completeness audit

_Status: source-backed cloud-safe audit; Gate 13 remains the earliest incomplete validation gate._

## Purpose

This audit reconciles two truths that had drifted apart in the repository:

1. PR #366 source-closed parameterized nested construction for FastViewScores
   and FastViewTeam.
2. The current renderer still exposes partial nested pixel planes.

The first fact must not be discarded, but it also must not be used to promote a
complete FastView frame.

## Recovered nested construction

Already canonical:

- LeagueTable heading: 8 visible controls;
- LeagueTable row: 10 visible controls per displayed row;
- displayed LeagueTable rows: source-count parameterized;
- TeamTable: 6 table-level controls;
- PlayerRow: 9 visible controls per row;
- TeamTable rows: `max(11, source_player_count)`;
- side 0 TeamTable precedes side 1;
- ScoreCompositeNormal: 5 static controls plus a runtime 0-or-2 phase pair;
- phase updates clear the old pair and append PictureControl then TextControl.

These remain represented as recovered parameterized construction, not as an
immutable constructor-only flattened z-order.

## Current pixel incompleteness

### FastViewScores / LeagueTable

`gate14_fastview_score_table_static_raster.py` intentionally emits only
source-backed static art. Every `FastViewScoreTableStaticPlane` requires:

- `text_rasterized = false`;
- `complete_component = false`.

LeagueTable geometry already exposes seven heading TextControls and nine
TextControls per row, so those are real visible omissions rather than a
hypothetical future enhancement. ScoreCompositeNormal also owns four static
TextControls per row, while the phase-label text is handled only as a separate
runtime plane.

Therefore the score subpanel cannot yet claim complete pixels.

### FastViewTeam

The retained PlayerRow raster is strong: it source-rasterizes the PlayerRow
name grid, energy art and all six English text cells. Its own contract still
requires:

- `complete_retained_player_rows = true`;
- `complete_team_table = false`.

That boundary is correct because TeamTable construction contributes six
table-level controls outside each PlayerRow subtree. Those controls have not
been reconciled into a complete TeamTable raster.

Therefore the team subpanel cannot yet claim complete pixels.

## Readiness consequence

Canonical readiness now keeps four separate facts:

- `score_subpanel_parameterized_construction_recovered = true`;
- `team_subpanel_parameterized_construction_recovered = true`;
- `score_subpanel_complete_pixels_recovered = false`;
- `team_subpanel_complete_pixels_recovered = false`.

A complete FastView frame must require both pixel-completeness flags in addition
to the already-explicit GoalFlash, ScoreCompositeMain, embedded outer-control,
global-order and blend prerequisites.

## Fidelity boundary

This checkpoint does not infer:

- missing nested text semantics or strings;
- missing TeamTable-level resources/geometry;
- a timeless aggregate icon/text order across separate phase broadcasts;
- global FastView z-order;
- complete-frame fidelity;
- Gate 14 completion.

The next safe visual task is to source-bind one of the known omitted nested
families rather than rerunning the already-closed nested count formulas.
