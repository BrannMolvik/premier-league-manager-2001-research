# Gate 14 FastView TeamTable original-art loader

_Status: independent Gate-14 work-ahead. Gate 13 remains the earliest incomplete validation gate and is exclusively Codex-owned._

## Purpose

FastView TeamTable already has source-backed ownership, exact side-specific
resource pairing, row geometry, text semantics, and the energy-bar transform.
The remaining pixel boundary is that its seven original EA444 resources are not
yet part of a reusable decoded-art interface.

This checkpoint adds that interface without committing replacement pixels or
claiming a complete TeamTable raster.

## Exact source family

reconstruction/original_fastview_team_art.py accepts only these seven
source-proven resources, in source contract order:

| Resource | Bytes | Geometry | SHA-256 |
| --- | ---: | ---: | --- |
| team_name_grid.444 | 3,496 | 259x16 | 368f7c86ef07d9447af886b0a4d8857fa4a732d65f17913f72b2a9155e9a4d93 |
| team_name_grid_2.444 | 3,512 | 259x16 | 0cce4d1646afa3dd11da5f0db6b3a887ded8a6d647f39d998eaef8ffe5f71602 |
| team_name_grid_3.444 | 3,512 | 259x16 | 8deb413437234504cbb6c3a076b172304469d873f4e2df5fbedd314e5f22b095 |
| team_name_grid_4.444 | 3,496 | 259x16 | 6fc1446b5d65a07a5165fa0947282dfeb6b783d142ae9edc76f60dbd5cecd3e8 |
| team_bar_1.444 | 2,344 | 82x16 | edd35c18a53598b3cfd3e93adc2b27153742582d7888a0923fdd672d36e2681d |
| blank_bar.444 | 2,776 | 82x16 | 961eb49ae0810a522130f4b6e7401c7d16250d0de65bc7e51bc8341c6b8a7e3a |
| team_bar_2.444 | 2,312 | 82x16 | 4514b621f8d6a7b41c82c5215c4a1af571f60d773f0a3d1ea095c87d62e8a751 |

All paths remain the exact FM2001_Art/FastView paths already recovered from the
canonical executable.

## Loader contract

load_verified_fastview_team_art(source_root, original_executable):

1. reads the supplied FOOTBAL.EXE;
2. obtains EA444 entropy/zigzag tables only through
   tables_from_original_executable();
3. obtains the fixed-point quantization source only through
   quantization_from_verified_executable();
4. reads every exact TeamTable resource path;
5. requires the recorded source byte size and SHA-256;
6. decodes with the verified original codec tables;
7. requires the decoded source geometry;
8. returns one immutable OriginalFastViewTeamArt bundle.

The executable helpers independently require the canonical executable SHA-256,
so replacement codec tables cannot silently enter this path.

No proprietary decoded output is written to Git by this module.

## Identity and fail-closed behavior

The bundle is deliberately strict:

- every one of the seven source resource names must be present;
- unexpected replacement names are rejected;
- source order is preserved;
- duplicate source identities are rejected;
- decoded geometry and RGBA byte count are checked;
- image_for() is bound to the exact FastViewTeamResource object identity rather
  than accepting an equal-by-value fabricated descriptor;
- missing, wrong-size, or wrong-hash source bytes fail before a decoded bundle
  is returned.

## What this enables

Once validated, this bundle can feed a TeamTable component rasterizer using the
already recovered:

- side 0 / side 1 name-grid selection;
- row 0 origins and 17-pixel row step;
- row 0..10 primary versus row >=11 alternate name-grid rule;
- static/dynamic energy-bar resource ownership;
- exact source energy rectangle transform;
- retained PlayerRow text render plans.

This loader does not itself choose source clipping/cropping behavior for the
dynamic energy PictureControl and does not rasterize PlayerRow text. Those
remain separate evidence/application steps.

## Validation boundary

reconstruction/test_original_fastview_team_art.py covers the exact seven-file
contract, identity-bound lookup, resource-set completeness, geometry/RGBA
validation, and source file missing/size/checksum failure.

Local process execution remains unavailable in the current ChatGPT sandbox.
The branch therefore must receive hosted CI before merge; no passing test claim
is made by this note alone.
