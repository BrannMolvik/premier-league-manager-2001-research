# Gate 12 - English Divisions

_Last updated: 29 September 2026_

## Scope

This checkpoint extends the already-verified generic primary `LeagueMatch`
runtime from the European child groups into the source-backed English
divisional competitions. It does not infer IDs from names or test fixtures.

## Canonical identity and schedule-container ownership

The English root country/region is **26**. Canonical `Static.dat` competition
records identify the ordinary English root Leagues below:

| ID | Competition | Runtime kind | Matchdays | Container |
|---:|---|---|---:|---|
| 0 | F.A. Premier League | League | 38 | primary, fixed-fixture |
| 2 | Division 1 (ENG) | League | 46 | primary, procedural |
| 3 | Division 2 (ENG) | League | 46 | primary, procedural |
| 4 | Division 3 (ENG) | League | 46 | primary, procedural |
| 7 | Conference | League | 42 | primary, procedural |

The executable ownership predicate is the already-recovered packed
`DBRCompetition +0x38` schedule-container field: codes **2 or 3** belong to
the secondary container; every other code belongs to the primary pass.

Applying that predicate to root `runtime_kind_code == 1` competitions in
country/region 26, while excluding fixed-fixture Premier League ID 0, gives:

```text
primary procedural English Leagues: (2, 3, 4, 7)
secondary procedural English Leagues: ()
```

This result is now asserted by canonical verification rather than maintained as
a hand-written runtime ID list.

The lower source entries named Conference 2 / Conference Cup are not part of
this proven root procedural-League set. They remain outside this runtime slice
until their exact class/season role is needed and source-backed.

## Implementation

`partition_root_procedural_league_ids()` derives primary and secondary root
League IDs from parsed competition records using the exact container predicate.

Canonical controller construction now:

1. derives England's procedural roots from source data;
2. rejects an unexpected secondary English procedural root rather than silently
   routing it into the primary container;
3. combines the proven English primary set with the already-supported European
   child League IDs 14/167 for the primary matchday view;
4. materializes those `league_match` nodes into the existing
   `LiveProceduralLeagueState` registry.

No new draw, participant, or schedule RNG is introduced by this bridge.

## Verification

Implementation checkpoints:

- `33483857`: derive root procedural-League container ownership;
- `e6ca4da2`: regression-lock the exact container predicate;
- `be403e04`: canonical verification asserts England -> primary
  `(2, 3, 4, 7)`, secondary `()`;
- `ae359cd4`: attach the source-derived English set to canonical controller
  primary order and live state;
- `91008587`: deterministic four-division save/reload continuation test.

GitHub Actions at `91008587337fd53dc55023a2a1a6508505928639` ran **783
reconstruction tests**. The only two failures are the same pre-existing
secondary-schedule assertions:

- secondary root-order expectation around competitions 170/181;
- secondary bucket-count expectation 262 versus current 280.

Both new English-divisional regressions passed. Repository asset policy passed.

## Next boundary

The four English divisional regular-season LeagueMatch structures are now live,
ordered, executable, and reload-safe. The next Gate-12 boundary is not another
regular-season match bridge. It is the **cross-division season transition**:
promotion, relegation, and any English playoff/qualification competitions that
determine movement between Premier League, Divisions 1/2/3, and Conference.

That transition must be audited from the canonical competition/allocation
structures before mutating club competition membership. Do not guess promotion
counts or playoff winners from modern football rules.
