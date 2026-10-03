# Gate 17 original playable-scope catalog

_Date: 4 October 2026 KST_

## Purpose

Gate 17 requires explicit evidence for every originally selectable/playable
country and League. PR #224 made that a mandatory external release receipt,
but deliberately did not invent a producer or hard-coded league list.

This checkpoint adds the repository-side catalog primitive that the final
Windows audit can consume. It does **not** claim Gate 17 complete.

## Source boundary

The catalog reuses already-recovered original TeamSelect behavior rather than
introducing a second definition of playable:

- canonical executable TeamSelect country order:
  England (26), Scotland (66), Germany (33), Italy (40), Spain (73),
  France (31), Holland (24), Belgium (9);
- root League filter:
  runtime_kind_code == 1, matching country ID, no parent competition;
- root League order:
  signed initialization_order_value, stably preserving source-table order
  for ties;
- club filter:
  exact competition membership;
- club order:
  raw CP1252 visible-name bytes;
- hierarchy capacity:
  16 shared country/League controls;
- club capacity:
  24 club controls.

The eight-country executable list independently agrees with the eight original
country-flag resources recovered from the authorized disc:
belgium.444, england.444, france.444, germany.444, holland.444,
italy.444, scotland.444, and spain.444.

Canonical game-directory loading is additionally guarded by the existing
hash verification for:

| File | SHA-256 |
| --- | --- |
| Master.dat | 183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8 |
| Static.dat | e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8 |
| English.str | aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601 |
| Core.str | b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06 |

No original game bytes are committed.

## Shared hierarchy capacity

TeamSelect does not reserve eight country slots plus eight League slots.
It rebuilds one 16-control list, inserting the selected country's root Leagues
immediately after that country row and truncating only after the list is built.

For the executable-recovered country order, the maximum source League rows
reachable before the 16-control boundary are:

    England  15
    Scotland 14
    Germany  13
    Italy    12
    Spain    11
    France   10
    Holland   9
    Belgium   8

The catalog records both the total source root-League count and the exact
visible/selectable prefix for each country. It likewise records every source
club count but only the first 24 native-ordered club rows as selectable when a
League exceeds the original club-control capacity. Any truncation is explicit
in the emitted JSON.

## Implementation

reconstruction/gate17_full_scope_catalog.py provides:

- derive_original_playable_scope(database) for the exact recovered TeamSelect
  projection;
- load_canonical_original_playable_scope(game_dir), which first verifies the
  canonical source hashes;
- deterministic JSON serialization;
- a compact-JSON SHA-256 catalog fingerprint;
- CLI output, optionally to a named JSON file.

The catalog fails closed when a required TeamSelect country is missing or
renamed, a visible League has no caption or selectable club, club IDs duplicate,
or a visible club caption is empty.

Focused synthetic regressions are in
reconstruction/test_gate17_full_scope_catalog.py. They cover the exact country
order, native League filter/order, shared 16-row truncation behavior,
24-club truncation, deterministic fingerprinting, and failure on missing or
changed source identities.

## Known functional blocker exposed by this audit

The current clean-room front end can represent source-proven TeamSelect
selections, but the gameplay handoff is still narrower than the original.

HumanGameplayController.select_club() currently accepts only clubs present in
the reconstructed Premier League and raises for every other TeamSelect club.
FrontEndSession documents the same Premier-League-only continuation boundary.

This means the new Gate-17 full_original_scope release receipt must remain
false until the human gameplay backend is generalized to every cataloged
TeamSelect League/club and those routes receive real Windows end-to-end
validation. The existing procedural-League runtime is a likely reuse path, but
this checkpoint does not modify shared gameplay state while Gate 13 is owned by
the active Codex worker.

## Exact next Gate-17 work-ahead

1. Run the catalog against the hash-verified canonical game directory and retain
   the emitted country/League/club identities plus catalog SHA-256 as durable
   evidence.
2. Build a disjoint fail-closed capability audit that compares the catalog to
   the current human-control continuation surface.
3. After the Gate-13 shared-runtime ownership lock is released, generalize
   human selection/match continuation through the existing procedural-League
   backend rather than creating a parallel simulator.
4. Exercise every catalog entry in the final Windows 11 archive and feed that
   independent receipt into the schema-2 Gate-17 evidence validator.

Until those steps pass, Gate 17 remains open.
