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
7. call `0x514520` and accept the current schedule node only if its
   `node+0x08` link is **still null** afterward.

This seventh branch direction is important. The header path does **not** require
`0x514520` to populate `node+0x08`; a newly non-null link causes
`0x615C50` to skip that node and continue down the bucket.

The unused optional context branch in `0x615C50` is not promoted into a
management-header semantic claim.

## Side-resolution/link boundary: 0x514520

`0x514520` does not allocate the `node+0x08` object itself. When that link is
still null and native flag bits 5/6 permit the path, it invokes the virtual
resolver on the first embedded `Side` at match `+0x14`. It then re-reads
`node+0x08`; only if the link is still null does it invoke the second
`Side` resolver at match `+0x28`.

The `Side` resolver is not a pure getter. `Side::+0x00` at `0x510320`
first resolves the underlying ClubRef and can then search the selected schedule
collection through `0x615F40`. That path can call `0x510BA0`, which allocates
and links a new 0x1c schedule object at the original wrapper's `+0x08` and
inserts it through `0x615A60` at a later schedule position. Consequently,
"both clubs are direct" is not by itself sufficient evidence that
`node+0x08` stays null.

RTTI confirms `Side` derives from `ClubRef`. The header candidate therefore
depends on both ClubRef resolution and the native linked-schedule side effects,
not merely on whether two club identities can be read.

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
references is not excluded by `0x510B20` **once it reaches this predicate**.
This does not supersede the earlier `0x514520` / `node+0x08` link test.

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
construction and the common `+0x64` dependency predicate returns zero.
However, Recovery 399's first pass over this trace incorrectly treated
`0x514520` as the allocator of `node+0x08`. The corrected disassembly proves
the opposite acceptance boundary: `0x615C50` returns a candidate only when
the link remains null after the Side resolver calls.

The repository's primary schedule shadow already retains source bucket order
and conservative participant graphs, but it does not currently retain the
`node+0x08` linked-object state or all `0x510320 -> 0x615F40 -> 0x510BA0`
side effects. Therefore the direct fixed-League **text producer is not yet safe
to integrate generically**. The selector control flow is closed; the clean-room
state mapping for the link test is the remaining implementation prerequisite.

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

This Recovery-399 trace closes the selector's native control flow and the
common direct-ClubRef `+0x64` predicate, but the corrected `node+0x08`
acceptance direction leaves one live-state mapping prerequisite before even the
direct fixed-League producer can be integrated. It does **not** claim those two
lines are integrated yet.

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


## Recovery 401: direct wrapper-link lifecycle source-closed

Recovery 401 re-opened the authorized private executable workspace and reverified
the canonical executable SHA-256 before continuing. Direct disassembly now closes
the remaining startup/direct-Side ambiguity that blocked the bounded fixed-League
header path.

### Wrapper construction starts with no linked object

Base schedule-wrapper constructor `0x510380` explicitly writes zero to
`wrapper+0x08`. Ordinary `LeagueMatch` construction at `0x5104F0` reaches
that base through `0x5103D0`; the common match constructor also initializes
match flags at `match+0x44` to zero. Therefore a newly materialized shipped
fixed-League wrapper starts with:

- `wrapper+0x08 == null`;
- native match bits 0, 5 and 6 clear.

This is direct executable evidence, not a clean-room default assumption.

### Direct Side resolution cannot create the link

`Side::0x510320` begins by reading its inherited ClubRef concrete-club slot
at `Side+0x04`. If that slot is already non-null it returns immediately at
`0x510379`. The `0x615F40` schedule search is reachable only after the
normal ClubRef resolver path for a Side whose concrete slot was initially null.

The shipped fixed-League builder constructs both participants as direct
ClubRefs, so both embedded Sides already have their concrete club slots.
Consequently the `0x514520` header materialization call invokes two Side
resolvers that return the concrete clubs without reaching `0x615F40` or
`0x510BA0`. For a fresh fixed-League wrapper, `wrapper+0x08` therefore
remains null across the exact acceptance test in `0x615C50`.

### The current-day schedule pass also leaves direct/direct LeagueMatch clear

The current-day bucket pass `0x615C10` calls wrapper virtual `+0x0C` before
it will invoke `0x510BA0`. Ordinary match implementation `0x510AD0` returns
true when bit 5 is clear and both Side resolvers return concrete clubs. A fresh
direct/direct fixed-League match satisfies that condition, so `0x615C10`
does not create a linked object for it.

Likewise, the `0x615DA0` continuation path invokes `0x510BA0` only after
the match virtual `+0x64` predicate returns nonzero. Recovery 399 already
proved common direct ClubRefs make `0x510B20` return zero, so this path also
does not link a direct fixed-League header candidate.

### Remaining external reschedule producers are post-start mutation boundaries

Static direct-call enumeration finds the remaining non-selector
`0x510BA0` callers at `0x4A801F` and `0x5E3C34`.

The `0x4A801F` path scans a date window, resolves match Sides and can move a
matching club's schedule wrapper. It is reached from the date-driven runtime
work around `0x4A7B30`, not from fixed-League construction. The
`0x5E3C34` path likewise searches live schedule state and can relink a match
during later runtime event processing. Those producers prove that
`wrapper+0x08` is not globally immutable for an entire season.

The clean-room currently does not model either producer's linked-wrapper
side effect. Therefore the safe representation is not a permanent boolean
"direct matches never link." It is an explicit three-state runtime contract:

- **clear**: source-proven fresh wrapper state;
- **linked**: only when a source-backed producer is later implemented and
  explicitly records the link;
- **unknown**: after the clean-room crosses a runtime boundary where an
  unmodelled original reschedule producer could have acted.

Header selection may consume only **clear** direct fixed-League entries.
`linked` entries are skipped exactly like native `0x615C50`; `unknown`
entries that could contain the human club must fail closed instead of being
silently skipped.

### Bounded implementation consequence

This closes the corrected Recovery-399 prerequisite far enough for a bounded
implementation:

1. the primary-schedule shadow may mark startup-materialized wrappers
   `clear`;
2. direct fixed-League Sides preserve `clear` through the header's own
   `0x514520` resolution;
3. the shadow must be invalidated to `unknown` when unmodelled post-start
   reschedule processing can occur;
4. the management-header selector may scan exact bucket/head-to-tail order and
   return a direct fixed-League candidate only while every relevant earlier
   participant/link state is source-known;
5. unsupported symbolic participants or unknown link state remain fail-closed.

This is intentionally narrower than claiming season-long reschedule fidelity.
It is sufficient to repair the fresh ordinary-management header without
inventing postponed-fixture behavior.


## Recovery 402: bounded clean-room integration and verification

Recovery 402 implements only the source-closed direct fixed-League subset described above.

The clean-room primary schedule shadow now records wrapper link certainty as
`clear`, `linked`, or `unknown`:

- fresh startup materialization is `clear`;
- explicit source-backed linked state is skipped by the header selector;
- a relevant `unknown` state fails closed;
- legacy snapshots that predate this field restore as `unknown`, never as
  invented `clear`;
- all current GameState day-advance routes invalidate previously clear state to
  `unknown`, because the original post-start `0x4A801F` / `0x5E3C34`
  reschedule producers remain unmodeled.

The management bridge scans the retained exact bucket/head-to-tail shadow order
and accepts only an unplayed `fixed_league_match` for competition 0/context 0
with two direct ClubRefs and `clear` wrapper state. The selected node token,
scheduled date, home/away club IDs, competition name, and source short names
are checked against live Premier League state before presentation. No
chronological fixture sort or nearest-fixture fallback was introduced.

For the accepted ordinary LeagueMatch formatter path, first-hand formatter
tracing also closes the remaining literal expansion details:

- `%Rf{ Round}` contributes no suffix for the ordinary League branch;
- `%Lf{ Leg}` contributes no suffix for a normal LeagueMatch;
- y=34 is therefore the source competition name;
- y=51 expands `%1s Vs %2s %D{%D %M %Y}` using source short names,
  unpadded day, three-letter month, and native two-digit `%Y`.

The live host now rasterizes those two controls with the already staged exact
18px Zurich font, recovered right/vertical-center `0x2102` style, white
`0xFFFF` endpoint, and exact control rectangles `(172,34,378,16)` and
`(172,51,378,16)`. When the bounded selector returns no source-known
candidate, both lines remain absent.

Validation was performed on PR #547 exact head
`d54184a0767416cb51d756f8edcc45a82d272677`:

- Gate 13 presentation source tests: run `37679247332`, success;
- reconstruction suite: run `37679247185`, **2915 tests / 25 skipped / 0
  failures**;
- repository asset policy: run `37679247320`, success.

PR #547 merged as
`97f8ecb3d39addbe3d036016bc52a05a91eb8c83`.

This integration does not claim later-season postponed-match fidelity and does
not close Gate 13. The primary club-name line still requires the verified exact
36px Zurich font to be staged and rendered, and the startup-FMV Windows
transport receipt remains a separate audit blocker.
