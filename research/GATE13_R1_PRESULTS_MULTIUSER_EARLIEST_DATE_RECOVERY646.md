# Recovery646: actual original PResults multi-human day owner, 4A83F0 (source)

15 October 2026 KST. Main baseline `2d909bb74985942065a0633757efafca928b358f`, after source-return PR755 merge. Work branch `worker/gate13-r1-native-event-owner-646`. **All claims are STATIC original executable evidence** from the owner-authorized 4,714,541-byte `footballmanager.exe` SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Original binary not committed/executed.

## P0 whole-player NEXT and actual multi-manager discrepancy

Re-disassembled original `PResults::0x4A83F0..0x4A8513` (source does **not** define one current-user-only calendar walker):

1. `4A83FB` initializes `PResults+0x64` processed-event count to zero; `4A8421→653350` builds the original calculated date range; `4A8435` writes **0** to original selected-user ordinal global `0x8755D4`.
2. For each original registered user from count `0x8755E4`, `4A843B→4139D0` reads manager by current ordinal, gets his `user+0x5B4` **club POINTER** and calls `615D10` on original PRIMARY date-container `0x947AD8`, global current date `0x9847FC` and literal 1. It chooses the earliest resulting **native event+0x10 date index**, retaining the first registered user on equal dates. `4A8473–488` increments selected ordinal and does signed CDQ/IDIV by user count. It returns to ordinal **0** after a complete loop. **No current-human-only priority and no fabricated roster-ID ordering.**
3. If any manager's event is reached, `4A8495→510A20` derives actual source date. If current+1 is **strictly less** than this date, it decrements returned date by one. If date is tomorrow or earlier, no subtraction. With no human next-match event, `4A84BE→616A30` obtains original next PRIMARY date bucket, then decrements one. `4A84D2` caps target at `current_global_date + 87753C` (bounded batch window).
4. **Only when native current date is before capped end** `4A84EA→4A7210` traverses genuine original PRIMARY bucket list for eligible-event v+0x0C pre-count. It then sets `PResults+0x68 = eligible_count + already_processed`; **increments original global date at 4A84FD before calling 4A83D0/4A8260**; loops per day. No arbitrary number-of-matches progress bar, no fake second-calendar total.
5. The PResults event method `4A83D0` calls `4A7280` to refresh current date/caption and `4A8260` to execute real current-date event callbacks, then `4A8070` for next world effects. The second collection 947AF0 also receives current date preparation calls in `4A7317..362`; it cannot be ignored when accepting complete normal progression.

**Current port gap:** `HumanGameplayController` has only one `self.human: HumanManagerState|None` and `advance_original_management` takes a next-match candidate for **only that current human's club**, via `PrimaryScheduleShadowState.ordinary_next_candidate`. The actual original PResults `4A83F0` schedules around the earliest NEXT relevant to **all** registered managers and rotates source native count/ordinal. It is not source-safe to call a single-human date calculation a complete port of 2–6 humans; a multi-human saved registry, club pointer membership, and second calendar event ownership must be reconstructed first.

## Bounded implementation/checks, not claimed gameplay

`reconstruction/original_presults_multiuser_day_target.py` accepts ONLY source-reached ordered original `615D10` results for 1–6 independently registered users (non-null native user+5B4 club pointers, native event pointers and event+10 slot indexes), plus actual `510A20` selected-match date or actual fallback `616A30` next bucket date, original current date and 87753C cap. It returns source date limit, selected earliest event/manager and pre-count reachability without original callback execution, mutation or GUI claims. Wrong null/mismatched or duplicate source receipts fail closed. Tests cover 1–6 registered users, first-in-tie order, earlier later-manager selection, no-match fallback, cap, native input failures and no invented original timer/RNG. Independent private original PE opcode verification **11/11 sites + 5 direct call targets PASS**; newly authored Python tests are WIP on the branch, NOT exact-head CI certified yet.

## Actual next work

1. Recover original **registered human user array as a durable GameState/SaveLoad owner** (source 874C10+9C4 count 8755E4 and ordinal 8755D4, original default1–6), with source-verified team pointers/club IDs, capture/selection, user rotation and tie ordering; do not reinterpret source pointers as club IDs.
2. Map reconstructed primary match event/native flags/lifecycle to `510AD0` virtual+0x0C and `0x615D10` true dated-event candidates **and source-original second collection/other event classes**. `PrimaryScheduleShadowEntry.payload_filter_bits` is only 0x61 and `side_club_cache` is a surrogate, not an authenticated native event+8 field/vtable/virtual result. Unknown entries must block or be audited, not silently count as zero.
3. Once the total calendar event owner is source-qualified, produce actual ordered `6168C0→4A71F0` callbacks for ordinary NEXT, updating real PResults bitmap fill during event progress. Then finish original `432505+` conditional return and player-mode 0/1/2/3 result lifecycle and save/reopen.
4. Physical Windows11 original-vs-port GUI interactions remain required, as do Gate13 and Gates14–17, all shipped leagues/countries, full inbox/Squad/season play. Existing PR739 remains separate high-risk/unmerged.

**This branch does not yet open a PR because source-only earliest-date logic is not a finished normal player vertical slice. Continue feature batching rather than committing/CI after each trace.**


## Fresh original 510380/5103D0 LeagueMatch construction and pre-count state

Direct original PE `510380–5103C1` proves initial new native
LeagueMatch instance has **event+0x08 DWORD=0**
(`510395 MOV [EAX+8],0`), **date slot +0x10=-1**
(`51039C MOV [EAX+10],FFFFFFFF`) and event+0x0C
source collection ID from original passed collection pointer
(`947AF0` selects low bit1) plus that owner's per-collection
sequence integer. `5103BA–5103C1` increments source
collection sequence. Then original `5103D0–5104E6`
writes **match+0x44 DWORD=0** at 5104CF and sets
native common LeagueMatch vtable 7C4CE4; original
`510500–510516` wraps it as another common class
7C4C24. This is actual constructor source evidence,
not a new GameState flag invention.

**Critical timing constraint:** new native event+0x08 and flags+0x44
are demonstrably zero at constructor exit, but subsequent original
event callbacks, postponement links, reschedules and v+0x38/v+0x3C
may mutate these fields. Existing `PrimaryScheduleShadowEntry`
tracks `payload_filter_bits` only in mask 0x61 and
`side_club_cache` as surrogate. It does not retain independently
sourced **native event+0x08** or a complete vtable pointer.
Consequently constructor defaults alone do **not** authorize
auto-counting all reconstructed future events at
PResults `4A7210` or artificially adding native 6168C0 ticks.

**Exact next check:** identify all original event+8 writes after
initial `510395` and relevant original event+44 writes
in 615A60/511370/510BA0 paths; persist actual equivalent
per-node event8 and vtable class only where producer and
mutation semantics are qualified. Then compare count
against original first- and second-collection non-LeagueMatch
events, fail closed on unknown candidate types.


## PostponedEvent native +0x08 pointer truthiness confirmed, 510BA0

Source-preserving bound read-only original `510BA0–510C09`
links the current event to its replacement when original
postponement is permitted. At `510BA3`, it reads
`original_event+0x08`; nonzero directly skips re-postponing.
For a zero link, `510BAC` calls original virtual+0x18
to get the payload and checks **payload+0x44 bit0x40**;
set bit6 skips the postponement entirely. If clean,
it allocates a fresh 0x1C-byte wrapper, initializes
it by original `510380` (therefore new wrapper+8 starts 0),
writes **new wrapper+0x14 = old event** and
**new wrapper+0x18 = reason/payload source argument**,
sets specialized wrapper vtable `0x7C9FE8`,
then original `510BF8` writes **OLD original event+0x08 =
NEW wrapper pointer**. It invokes native `615A60`
to insert the new wrapper at original date index
`old+0x10 + 7`.

This proves a narrow equivalence for PResults:
`PrimaryScheduleShadowEntry.wrapper_link_state=linked`
may correspond to the original old event+0x08
being nonzero **if and only if** the entry was
actually linked by the qualified 510BA0/615A60
lifecycle. Native PResults `4A7210` requires
event+8 == 0; a linked old event must not count
as eligible again. Modern `wrapper_link_state=clear`
is *not sufficient* to assert actual native event+8
is zero after unspecified mutation, wrapper lifecycle,
or a prior process; do not promote it automatically.

Original `510BA0` is thus a bridge lead for
reconstructing event+8 truthiness inside persistent
`PrimaryScheduleShadowState`. A source-safe
implementation must preserve provenance of original
link insertion and unknown paths, not reinterpret
one user-visible postponed score or fixture date as
a native node pointer. The second event collection,
all non-LeagueMatch vtables, all actual 6168C0
callbacks and real GameState SaveLoad remain
outstanding. No original executable was launched.


## Recovery646 next exact-source discovery: native PostponedEvent wrapper PResults virtual ownership

Fresh private original PE vtable at **0x7C9FE8** (raw
`.rdata` offset `0x3C9FE8`) proves postponed event has
**different native virtual implementations** from common
LeagueMatch vtables:
- virtual+0x0C = **0x5140B0**,
- virtual+0x10 = **0x5140F0**,
- virtual+0x18 = **0x514100**.

All three load **wrapper+0x14** underlying original
event pointer and tail-jump to that underlying event's
corresponding vtable method. Thus native
`PResults 4A7210` calling wrapper v+0x0C can
correctly see the **underlying** `LeagueMatch 510AD0`
eligibility. But the immediately subsequent
`event+8` check is on the **new wrapper itself**,
not on the linked underlying old match!
Original `510BF8` writes **old match+8=new wrapper
pointer**, so counting the underlying old match
again would be incorrect; fresh wrapper was
initialized through `510380` with **wrapper+8=0**.
Then `v+18` returns original underlying match
via `514100→underlying v+18`, so the
`payload+44 bit0x40` is tested on the **underlying**
match, not wrapper bytes.

New `original_presults_postponed_wrapper_precount.py`
strictly requires the original 7C9FE8 wrapper
vtable and bidirectional 510BA0 source link
identity (wrapper+14 points to old match, and old
match+8 points to wrapper). It invokes already-
tested native common/special LeagueMatch v+0C
to establish eligibility, then applies the
**wrapper's** event+8 source gate and underlying
post-callback match+44 flags. If the underlying
virtual is false, post-virtual fields cannot be
supplied, preserving original short-circuiting.
Tests assert linked old event is excluded while
new wrapper is counted on source **+7-day** future
slot, including the original 4A7210 real date
bucket iterator, not a made-up fixture count.

Original executable independent direct source check
**8 original opcode sites plus native vtable
three exact method addresses PASS**. New
source-plus-composition Python tests authored on
the current feature branch, not yet remotely CI
run. Importantly this does **not** implement
real native event callback side effects, original
two-date-collection ownership, saved GUI/multiuser
or original PResults ticks. It rules out an easy
but wrong future implementation: `wrapper+8`
must not be mistaken for linked old match+8, and
`wrapper+44` must not be substituted for
the underlying match's payload+44. Normal
`PrimaryScheduleShadowEntry.wrapper_link_state`
is a partial semantic reflection, not proof the
native raw pointers were really reached.
