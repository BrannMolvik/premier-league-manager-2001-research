# Gate 14 FastView score/table original-art loader

_Status: independent Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate and is exclusively Codex-owned._

## Purpose

FastView score and LeagueTable presentation already has source-backed resource
ownership, exact paths, byte sizes, SHA-256 identities, decoded geometry, and
visible layout rectangles. The remaining pixel boundary is a reusable,
checksum-gated decoded-art interface for those originals.

This checkpoint adds that interface without committing replacement pixels,
naming still-unresolved text controls, or claiming a complete FastView frame.

## Exact source family

The loader accepts exactly eight resources, in preserved source-contract order:

1. current_fix_grid_1.444, 309x19, FastViewLeagueScores;
2. current_fix_grid_2.444, 309x16, ScoreCompositeNormal;
3. half_time_icon.444, 18x16;
4. extra_time_icon.444, 18x16;
5. penalties_icon.444, 18x16;
6. full_time_icon.444, 18x16;
7. current_table_grid_1.444, 381x19, LeagueTableComposite heading;
8. current_table_grid_2.444, 381x16, LeagueTableComposite row.

All paths, sizes, hashes and owners come from the existing
gate14_fastview_scores.py and gate14_fastview_league_table.py contracts. No
filename-based role inference is added here.

## Loader contract

load_verified_fastview_score_table_art(source_root, original_executable):

1. reads the supplied FOOTBAL.EXE;
2. obtains EA444 tables and quantization only through the existing canonical
   executable hash-gated helpers;
3. reads each exact source path;
4. requires the recorded byte size and SHA-256;
5. decodes with the verified original codec tables;
6. requires the exact decoded geometry;
7. returns one immutable OriginalFastViewScoreTableArt bundle.

The bundle preserves the distinct metadata types used by score grids, phase
icons and LeagueTable grids. image_for() is identity-bound to the exact
source-proven metadata object, so an equal-by-value fabricated descriptor
cannot silently substitute.

## Fail-closed behavior

The loader rejects:

- missing or unexpected resource names;
- missing source files;
- byte-size or checksum drift;
- decoded geometry or RGBA-size mismatch;
- metadata types outside the three established source contracts;
- canonical-executable absence or codec-table verification failure.

## What this enables

A later disjoint raster slice can now use original pixels for already recovered
placements without re-reading or re-classifying source files:

- current-fixture score strips;
- ScoreCompositeNormal row grids;
- typed half/extra/penalties/full-time icons;
- current LeagueTable heading and row grids.

Text semantics that remain unproved stay out of scope. Cross-component z-order,
audio and 3D choreography also remain fail-closed.

## Validation

Synthetic tests cover exact eight-resource order, geometry, image identity,
resource-set completeness, and source missing/size/checksum failures. The new
source and test files are explicit reconstruction-workflow triggers.

The local process sandbox remains unavailable with process-start
caas.internal.errors.ClientError, so this checkpoint requires hosted CI before
merge.
