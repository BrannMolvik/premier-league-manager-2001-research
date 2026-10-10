# Primary Squad preparation producer — 8 October 2026

Canonical executable SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Private reports and executable remain outside Git. No original process was
launched for this investigation.

## Original behavior and evidence

`PSquadScreen::constructor 4B8240` retains the club at `+C8` and constructs
two `PSquadList` owners (`+130`, discriminator 0; `+1030`, discriminator 1).
Its `4B7BD0` producer precedes `4B7500` ordering and `4B6FE0` slot mapping.

For primary-owned players, `4B7BD0` uses `408500`'s actual next-match quota.
A roster of at least quota+25 with no reserve flags invokes `40AB40` with
the retained club reserve formation (`404A70`, club+1DC). Formation 22 is
normalized to 0, including unsuccessful selection. Each formation slot scans
eligible players once in original roster order, using role rating times Form;
strictly greater scores replace the candidate, so ties retain original order.
This is not `409C90`'s preferred-role prepass. An incomplete XI is not committed.
After success, eleven reserve roles/auxiliary bytes are written; `40AEA9`
forces three reserve substitutes chosen in remaining original order.

Small rosters clear existing reserves through `4181B0`, including `418220`'s
role/auxiliary-byte swap and preferred-role reset. Every branch then runs
`4067B0`. That reverse overflow walk has **four sequential quota checks**;
one player's later setter can replace its earlier state. The small-roster
11/3 reserve *count substitution* must not fabricate reserve selection flags.
The loop exits on excess==0, not excess<=0.

`418220` preserves previous role/aux bytes at player+152/+153, while the new
role-object setters mask to five/four bits. Import explicitly zeros these
backup bytes (`418F83`, `418F8A`). Club import explicitly zeros reserve
formation (`403684` supplies zero, `403764` writes +1DC). These are producer
writes, not assumptions about allocation initialization.

`5F0E00`'s actual 46 role records and `5F2110` linkage qualify the
`5F0D20` occupancy capacities. First-XI role 8 counts role-4 contribution
divided by three; reserve role 8 adds the full contribution. The role-adjust
scan is native 1..19, not invented formation order.

Private bounded canonical-function execution compared 100 primary preparation
cases against `original_squad_preparation.py`, including setters, role swaps,
overflow and first-active call ordering: all match. Source scoring/availability
leaf inputs were explicitly supplied; this is not a live startup proof.
Receipts: `work/squad-preparation-native-comparison.log`,
`work/qualify-squad-preparation.py`, `work/qualify-squad-position-caps.py`.

Private script/receipt SHA-256:

- preparation comparison script: `25d51753ad5fbc2a987d4b305a99a1700b8f8e1b68b6ea56f57138b7269041bc`;
- comparison receipt: `f033f75b2940248fd8f78bf61ee9934d73d8c178ec752bb356aebcdaf50fa734`;
- canonical role-table initializer harness: `ceaac6f8082a5fc616c7be6cfe1f2b5ef8bd3afdb9bf1a00da8282df71e9b7bd`.

## Implementation and limits

The pure producer and GameState preparation/order adapters are implemented.
Save schema 47 retains reserve formation and both position backup bytes.
Primary-only semantics are explicit; unresolved secondary/loan contexts and
first-active loan-list counter side effects fail closed before mutation.

The normal host is **not yet wired**. A canonical database check on Southport
(30 players) and Liverpool (35) exposes incomplete first-XI startup state when
only this constructor preparation is applied. Do not invent first-XI autofill
or claim a playable paired roster until the preceding startup/manual selection
boundary is qualified. This does not prove that the original auto-selected a
first XI at startup: that lifecycle remains unknown. Likewise retain native empty-row owners and slot holes;
do not compact them or replace the paired lists with scrolling.

`408500` is not the displayed club competition's quota: it calls
`4079D0 -> 615D10`, with the current source day and eligible match guard;
only a proven null next-match result takes its literal-five fallback.
The live integration must retain this exact lookup boundary.

## Paired presentation adapter

`original_squad_paired_presenter.py` now binds explicit prepared membership
to both 20-slot owners. It preserves vertical holes. `-1` is an empty-owner
branch; a nonnegative index beyond roster count follows `406F00`'s null
lookup rather than Python indexing. Other negative indices fail closed.
Unpresented IDs are retained in a diagnostic field, not silently discarded.
A complete 11+5 / 11+3 fixture proves all 30 IDs appear once across both lists;
this synthetic selection fixture is a regression, not native startup evidence.

`4B4FE0` is shared by both lists. `4B5052..4B506D` uses discriminator +98C
to select globals 984560/984558; language loader 637574/6375B6 binds
English.idx 166/168 (`First Team`/`Reserves`). The same title/grid/font
setup uses the recovered parent origins (37,0) and (418,0), exactly 381 apart.
The opt-in paired title/grid and text renderer preserve that transform and
reuse identical child pixels. This is not yet connected to the ordinary host.

Empty SCF owner setup is independently identified: vtable 7C5810 -> 48A510
uses wrapper 943F90; loader 5F9B70 supplies an 89x16 crop at source x=239.
Do not substitute the populated-row bitmap: the exact backing-art/crop chain
and normal row-selection pointer events still require completion before the
paired rendering is an ordinary playable screen.

Verification: **287 focused tests, zero failures/skips** (34.568 seconds),
including runtime swaps, preparation, native mapping, paired holes/identity,
paired translation, schema-47 disk save/reload, existing management host,
header/caption and Windows startup backend tests. Repository asset policy and
`git diff --check` pass. Full-suite and fresh Windows acceptance are not rerun
because the live ordinary paired route has not reached an executable milestone.
