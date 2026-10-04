# Gate 13 League Fixtures selector source-data audit

_Status: cloud-safe fail-closed integration boundary while private process execution is unstable._

## Purpose

The recovered `PLeagueFixtures` selector code proves two different facts:

1. eight static country radio controls with exact country IDs, captions, source
   order, event IDs and owner offsets;
2. up to six dynamic League radio controls rebuilt by traversing each native
   `DBRCountry` competition array at `+0x48/+0x4C`, RTTI-casting each
   `LeagueBase*` entry to concrete `League`, then preserving that encounter
   order for the visible controls.

The current clean-room `GameState` has a generic competition mapping, but it
does not materialize the original per-country `DBRCountry` competition-array
order. Dictionary/source-table order is therefore not accepted as a substitute.

## Audit contract

`gate13_league_fixtures_selector_source_audit.py` records:

- the exact eight source country selector IDs/events;
- the controlled club's source country and current live competition;
- the matching static country-selector index;
- the native dynamic-array offsets `+0x48/+0x4C`;
- which source-ordered country League arrays were explicitly supplied;
- which of the eight source countries remain missing;
- the current country's exact supplied League identities/captions;
- the current League's source-array index and resulting dynamic events 9..14;
- exact blocker codes and a single readiness boolean.

With no explicit native-order input, current runtime state reports
`dbrcountry_competition_array_order_unmaterialized` and remains not ready.
The audit never consults `state.competitions` to derive that order.

A future source-backed producer may supply
`source_cast_leagues_by_country`, but each value must already be the ordered
concrete League entries produced by the recovered native array traversal and
RTTI cast. The audit rejects missing countries, extra countries, duplicates,
invalid captions/IDs, more than six exposed League controls, and a current
competition absent from the exact current-country list.

## Boundary

This module is diagnostic only. It does not create radio controls, mutate the
selected country/League, infer selector geometry, reorder competitions, or
change the live League Fixtures grid. It also does not claim that the original
country arrays can be reconstructed from the generic runtime mapping.

The next implementation step is source-sensitive: recover/materialize the
native per-country competition-array ordering (or prove a source-backed
equivalent producer) before integrating the dynamic League selectors into the
stateful management presenter. Until then, the already-recovered static country
metadata may be inspected but the complete selector state remains fail-closed.
