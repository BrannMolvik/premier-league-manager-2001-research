# Gate 13 management-header match selector source trace

_Recovery 399, 8 October 2026._

## Scope and evidence boundary

This note closes the native selector behind the ordinary management-header
conditional match lines far enough to reproduce the **direct fixed-League
first-season path** without replacing it with a generic "next fixture" search.

First-hand analysis used the canonical shipped executable only:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

The authorized original disc archive was re-materialized and the executable was
re-extracted from its MODE1/2352 track. Its SHA-256 again matched the value
above. No original executable bytes, raw disassembly, disc image, or temporary
extraction are committed by this trace.

This is a bounded closure. Direct fixed first-season LeagueMatch nodes are
source-closed below. Cup and other symbolic participant references retain their
existing fail-closed boundary until their date-dependent ClubRef predicates are
mapped into the live clean-room state.

## Header caller and schedule-container selection

The central-header refresh at `0x432760` obtains the current human club and
calls `0x4079D0` before entering `0x615DA0`.

`0x4079D0 -> 0x403640` selects one of the two native schedule collections from
the current club's runtime category byte at `+0x74`:

- values 2 or 3 select the collection at `0x947AF0`;
- every other value selects the collection at `0x947AD8`.

The date used for selection is the global current game date at `0x9847FC`.
The apparent extra date argument left on the caller's stack is cleanup
compatible with `0x615DA0`'s `ret 8`; `0x615DA0` itself reloads the current
date global before the first search.

## Exact date-forward bucket traversal: 0x615D10

The selected schedule collection has the source-visible shape needed by the
search:

- `+0x00`: array of per-date linked-list bucket heads;
- `+0x04`: bucket count;
- `+0x08`: absolute base date.

`0x615D10` computes the first bucket as:

`requested date - collection base date`

and scans that bucket and all later buckets in ascending date order. Within a
bucket it delegates to `0x615C50`, which walks the native linked list
head-to-tail. Therefore the selector preserves the already-recovered
ScheduleContainer bucket and shuffle order. It is **not** equivalent to sorting
all fixture rows by a modern date/fixture key.

For the management-header call, `0x615C50` receives the current club plus the
fixed selector state used by `0x615D10`. Its relevant acceptance boundary is:

1. obtain the concrete match through virtual `+0x18`;
2. require native match flag bit 5 to match the header's clear target;
3. require the match to contain the current club through its ClubRef/Side
   membership predicate;
4. in the header's materializing path, reject a node that already has a
   `node+0x08` runtime-side object;
5. reject native match flag bit 6;
6. reject native match flag bit 0 for the header's zero fallback argument;
7. call `0x514520` and require the node to become materializable.

The unused optional context branch in `0x615C50` is not promoted into a
management-header semantic claim.

## Participant materialization: 0x514520

`0x514520` is the lazy participant/materialization boundary used by the
header search. When `node+0x08` is still null and match flag bit 6 is clear, it
requires both embedded participant objects to resolve:

- participant 0 is the `Side` / ClubRef at match `+0x14`;
- participant 1 is the `Side` / ClubRef at match `+0x28`.

Only when both virtual participant resolvers return nonzero does the routine
allocate the small runtime-side object, store it at `node+0x08`, and register
it through the schedule collection.

RTTI confirms `Side` derives from `ClubRef`. This matters because the later
date-dependency test is a ClubRef predicate, not a UI-only fixture filter.

## Concrete match classes and virtual predicate

MSVC RTTI closes the concrete class family traversed by this selector:

- `Match`;
- `LeagueMatch`;
- `FriendlyMatch`;
- `CupMatch`;
- `CupMatchReplay`;
- `FirstLegMatch`;
- `SecondLegMatch`.

For these classes virtual `+0x18` is the common identity return, so the
underlying match object examined by the selector is the concrete object itself.

All listed classes except `SecondLegMatch` use `0x510B20` at virtual
`+0x64`. `SecondLegMatch` uses `0x510B60`.

### Common predicate: 0x510B20

`0x510B20` asks `0x4F2B60` about each of the two participant ClubRefs using
the schedule-relative date/index supplied by the wrapper. If either participant
reports a date-dependent unresolved dependency, `0x510B20` returns nonzero.

The critical direct-ref result is source-closed: when a ClubRef's normal virtual
resolver already returns a concrete club, `0x4F2B60` returns zero. Its
additional type-specific branches apply only to unresolved symbolic ClubRef
types.

Therefore an ordinary fixed LeagueMatch whose two participants are direct club
references is not excluded by `0x510B20` on this dependency test.

### Second-leg extension: 0x510B60

`SecondLegMatch` first applies the common `0x510B20` predicate. If that does
not exclude the match, it follows the linked-match chain through `+0x54` and
`0x510C10` and adds a schedule-date dependency check against the linked tail.

This is deliberately not generalized into a clean-room Cup rule by this trace.

## Outer qualifier loop: 0x615DA0

`0x615DA0` starts by calling `0x615D10` with the current human club and the
global current game date. For each returned candidate it calls virtual
`+0x64` with the wrapper's schedule-relative date/index.

- A zero predicate result returns that candidate to the management-header
  caller.
- A nonzero predicate result causes the candidate to be materialized/attached,
  converts its relative schedule index to an absolute date using the selected
  collection's base date, and resumes `0x615D10` from that date.

The original assumes this continuation path can yield another candidate. The
clean-room must fail closed rather than invent a fallback if its available
runtime state cannot represent the continuation.

## Clean-room mapping for the shipped fixed Premier League

The repository already has the exact pieces needed for the bounded shipped
first-season League path:

- `competition_schedule.StartupScheduleNode` retains both participant
  ClubRefs, schedule identity, competition identity and node kind;
- `direct_club_ref()` represents native direct ClubRefs;
- fixed real-fixture League nodes are emitted as
  `node_kind="fixed_league_match"` with two direct ClubRefs;
- `primary_schedule.py` reproduces primary-container placement
  (`0x615950`), linked-list insertion and the `0x615BE0` per-bucket shuffle;
- `GameState.install_premier_league_scheduler_order()` retains the exact
  recovered head-to-tail fixture order for Premier League rounds;
- current date, played/unplayed result state, source fixture identity and club
  identities already exist in the live GameState/management bridge.

For this direct fixed-League subset, both participants are concrete from
construction and the common `+0x64` dependency predicate returns zero. This
closes the native selection semantics needed to select the first qualifying
unplayed fixed Premier League match involving the current human club while
preserving recovered ScheduleContainer date/bucket order.

This does **not** authorize a generic selector for:

- unresolved Cup ClubRefs;
- second-leg dependency chains;
- other symbolic ClubRef types;
- a schedule collection whose exact live bucket order is unavailable.

Those cases remain fail-closed.

## Relationship to the two central header lines

The text/layout side was already source-closed in
`research/GATE13_MANAGEMENT_CENTRAL_HEADER_SOURCE_TRACE.md`:

- y=34: `%C %Rf{ Round} %Lf{ Leg}`;
- y=51: `%1s Vs %2s %D{%D %M %Y}`;
- matchup `%1s` / `%2s` use the source short club names;
- both controls use rect width 378 at x=172, 16px height, raw style
  `0x2102`, white endpoint `0xFFFF`, and the exact 18px Zurich font.

This Recovery-399 trace closes the missing selector for the direct fixed-League
path only. It does **not** claim those two lines are integrated yet.

## 36px club-name font re-verification

The same authorized disc was used to re-extract the still-unstaged club-name
font from ISO extent 170896:

`Fonts/Zurich_BdXCn_BT_36pixel.fnt`

The extracted file is exactly 155,544 bytes and again hashes to:

`92a10c37d85a5bd23bab3ca8aee69779a570a47e5a8b25cbf0e5f0bf13c835df`

Its EA font atlas parses as 2678x38 with native line height 39. The source word
`Southport` measures 99 pixels; the recovered right-aligned/vertically
centered `(172,1,378,32)` control therefore starts at x=451 and clips to the
control's 32-pixel vertical extent.

The bytes are verified in the private analysis workspace but are **not staged
in Git by this checkpoint**. The repository asset remains blocked until the
byte-identical file can be imported through a binary-capable provenance write
path. No replacement font is authorized.

## Exact next step

The next repository-side implementation task is to bind the direct fixed-League
selector to already-recovered schedule/runtime state and render the two exact
conditional match lines for that bounded path. Any unsupported node class,
symbolic participant reference, missing exact order, or unresolved runtime
state must return no header match instead of falling back to a plausible
fixture search.

Separately, stage the exact 36px font and club-name renderer as soon as a
binary-capable Git/provenance path is available.

Neither this trace nor those follow-up integrations close Gate 13. The
post-#482 audit, focused/full verification, and the separate private Windows
startup-FMV transport receipt remain required.
