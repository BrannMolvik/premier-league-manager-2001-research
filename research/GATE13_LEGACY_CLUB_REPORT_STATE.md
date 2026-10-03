# Gate 13 legacy club setup boundary

3 October 2026; based exclusively on canonical main `6207dbe01de068083c20f7fe22a773adab35e010`.
Executable SHA-256: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
The authorized ZIP hash and physical MODE1/2352 sectors were reverified locally.
No source files or binary dumps are committed here.

## Confirmed visiting-capacity lifecycle; unresolved fresh bytes

`0x5DA2F0` retains its DBRClub receiver through `0x5DA538`. The uncontrolled
branch reads `+0x13C/+0x140` as unsigned dwords, clamping each to zero only
when greater than 200000 (double at `0x7D73D8`). There is no authorization to
replace an unknown allocation byte with zero or a modern stadium split.

Native save/load address sites `0x402C05/12`, `0x402FA2/B3`, and
`0x4033A2/B3` and clone copies `0x40C20B/17` preserve these runtime values.
`0x667E90` is the stream read wrapper, not a capacity producer. Fresh club
loading `0x40B9C0` allocates through `0x40BBE0`, constructs `0x405A40`,
imports each DBTClub through `0x403660`, then runs `0x40BD10`. The latter
constructs/copies a fallback club; the inspected path does not establish
actual clubs' visiting-capacity initialization. CRT HeapAlloc uses flags 0;
zero-filled fresh storage is not a contract. Uncontrolled-home production
therefore remains fail-closed pending a proven write or observed native
allocation/lifecycle boundary. Home capacities `+134/+138` are a different
producer and do not authorize visiting values.

## Confirmed attendance byte and D48 guards

Constructor `0x405A6E/0x405AA7` clears `+E8` explicitly, but does not initialize
`+130`. At the end of gate calculation, `0x5DB972` tests E8 bit 9. When clear,
`0x5DB97F` writes count 1 without reading the allocation byte. When set,
`0x5DB9B5/0x5DB9C1` increments AL with byte wrap, not saturation. The weighted
attendance average is a separate field; `0x5DB9E3..EC` sets bit 9. Native
clone/save paths retain flags and count. The new runtime type distinguishes
known-clear flags with unknown count from a produced byte and saves that
distinction in internal schema 42.

`0x408170` returns zero for a null user. Count below 2 returns shipped global
`0x8217D8` (5). Otherwise global human owner `0x4139D0`, registered League
`0x4F3B10`, and `0x4F4070 -> 0x4F4940` supply the refreshed zero-based native
member-array index. Rank >= global `0x8217D4` (4) also returns 5. This result
is independent of an unknown count: both possible count branches return 5.
Runtime uses strict source short-name byte ordering, not display/club-ID
fallback. Missing native membership/name ordering and rank -1 stay unknown.

Rank below 4 with count >=2 takes a different branch that rewrites the entire
AI roster's Condition using MatchEngine RNG. Its output must not be replaced
by a numeric 16 without the actual player/RNG side effects. This remains
fail-closed, as do secondary/loan shirt contexts. No Gate-14 code is changed.

## Genuine ordinary route milestone

Authorized `Stadium/Data.wad` provided exact `Lists/Buildings.dat` and
`Maps/coventry.MAP`, staged privately as the database's `MapFiles/coventry.map`.
WAD SHA-256: `d7d00e3fd80836be1c67bffca721c903e81e67fea5ae319b260777a91fc7814d`.
Buildings: `3afa87771a8801cd5e307eef6a1039781022d8962d424e6838285ea4055005f9`.
Coventry map: `e580a5afc8c2a44f398e776cfc9d89acc00f5f4516b6b6446b7bb343df57b3ec`.
Container-format reference only: [OpenTPW WADView](https://github.com/OpenTPW/WADView).
No public game copy was downloaded or substituted.

Canonical database, season 2000, CRT and MatchEngine seeds 1, first round
26 August 2000: fixture 2, Coventry (5) hosting Newcastle (11), human native
rank 5. Existing legal-XI autofill and original stadium/ticket materialization
feed the real calculator, not injected report fragments. All eleven scalars
and initial participant flags are present; strict assembly actually publishes
one report and fixture link `{2: 0}`. Disk save and fresh controller reload
preserve the identical report, link and attendance state. A real Tk
`<Button-3>` at that fixture's native visible cell opens matching PMatchInfo
context and the source-accepted popup rectangle `(20,50,760,500)`.

Private receipt `work/gate13-calculated-reload-rightclick-20261003.json`:
SHA-256 `23bdb02b2d2315a34692a05772d2dc6b1079563613ff9fbacc5811679f78f028`.
Private save SHA-256 `8ada1012f08b1f703753a30f59c757147242521ecfd166890bd7c01294e6bea4`.
Private reproducer: `work/probe_gate13_human_setup.py 2`; source extractor:
`work/recover_stadium_setup_private.py coventry.map`. All stay outside Git.

This is successful context publication/navigation, **not complete visible
PMatchInfo contents**: nested owner-local rendering remains fail-closed.
Chelsea fixture 1 also published/reloaded, but its away club fell outside the
first twelve visible columns; no invented scroll action was used. The ordinary
host also does not automatically materialize these private stadium inputs.
Gate 13 remains open; this probe does not sign off original timing or normal
play recognizability, or reduce the original all-country functionality scope.
