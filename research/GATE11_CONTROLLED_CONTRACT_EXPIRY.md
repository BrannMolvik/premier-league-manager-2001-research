# Gate 11 controlled-player contract expiry and renewal suggestions

Verified against canonical FM2001 `FOOTBAL.EXE` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

This note maps the ordinary user-controlled branch of DBRPlayer
`0x41BEE0` separately from the already implemented non-user
`0x41ABC0` random renewal/release path.

## Callers

Three direct executable callers exist:

- `0x41ABCE`: `0x41ABC0` delegates here when `0x417360` reports that
  the player's active/current club is user-controlled. This is the ordinary
  first-of-month player-maintenance route already reached through
  `0x4A81A0 -> 0x40BB10 -> 0x4042E0`.
- `0x41AD79`: broader player aging/recycle maintenance `0x41ACA0`.
  The user-controlled branch calls `0x41BEE0` unless global
  `0x875680` selects an immediate 12-month `0x419190` renewal.
- `0x432132`: a multi-user roster sweep inside `0x431F70`; it walks
  every linked user's club roster, invokes `0x41BEE0` on each player, then
  processes the manager mail queue for the current date through `0x613EE0`.
  This is a separate session/UI transition path and is not substituted for the
  proven monthly caller.

The clean-room calendar implementation should use the proven monthly caller
for ordinary progression. The other callers remain explicit boundaries rather
than being silently invented as additional daily/monthly passes.

## Ordinary pre-expiry path: Out of contract begins 21 days before expiry

For ordinary players, where byte `player+0x138 < 0xFE`, current date below
contract expiry enters the normal controlled-player branch.

The code first tests:

```text
current_date + 21 >= contract_expiry
```

and, when true, sets DBRPlayer `+0x14` bit 7, the already proven
**Out of contract** status.

This corrects the earlier provisional description: the ordinary controlled
player becomes Out of contract **within 21 days before expiry**, not only after
expiry.

## Assistant-manager renewal suggestion window

The same branch continues only when:

```text
current_date + 112 >= contract_expiry
```

so the suggestion window opens 112 days before expiry.

Further gates are:

- byte `player+0x164 == 0`;
- `0x417360(player) == 1`, active/current club is user-controlled;
- one shared CRT `RNG(10)` draw is consumed and must be **< 4**;
- `0x41C6F0(player)` must be false.

`0x41C6F0` calls `0x422950`; only when that lookup succeeds and
`player+0x178 > 0` does it suppress the suggestion. The runtime already
maps `+0x178` as pending/deal count. Until the exact global lookup at
`0x8774A8` needs materialization, this suppression should remain a
source-backed predicate rather than be guessed from pending count alone.

No additional `0x64D540` call occurs in the suggestion construction or
queue insertion. Thus an eligible suggestion attempt consumes exactly one
shared `RNG(10)` draw.

Once an event is queued, `player+0x164` is set to **1**. Contract
application/renewal paths including `0x419210` clear it back to zero, proving
`+0x164` is the persistent latch that prevents repeated renewal suggestions
while the previous suggestion/workflow remains active.

## Exact suggestion event classes

After the RNG and pending-workflow gates, `0x41BEE0` branches on
`0x41E5A0`. That helper is already proven as:

- player age >= 24;
- player `+0x6C == 2` (EU/exempt code).

When true, the queued event uses RTTI class:

`EAMAssManSuggestBosmanPlayerContractRenewalMsub`

with vtable `0x7BDBE0`, message ID `0x1B7`, and original key string
`AssManSuggestBosmanPlayerContractRenewalM`.

Otherwise it uses:

`EAMAssManSuggestPlayerContractRenewalMsub`

with vtable `0x7BDB8C`, message ID `0x0E`, and original key string
`AssManSuggestPlayerContractRenewalM`.

Both are wrapped in RTTI class **MPMEAMail** (vtable `0x7BD564`). The
wrapper stores the current date at `+4`, the event pointer at `+8`,
sets event flags `|= 0x6`, and queues it through `0x613EC0` on the
global manager/mail queue at `0x947AA8`.

Action handlers `0x5D2AD0` and `0x5D2C00` converge, for their action-0
branch, on RTTI class **EAMAmendContractsub** (vtable `0x7BDC44`) and
hand it to the existing event/action pipeline. Therefore accepting either
assistant-manager suggestion enters the Amend Contract workflow; the clean-room
should not auto-renew merely because a suggestion was created.

## Expired controlled player: cleanup first

When current date is at or beyond expiry, `0x41BEE0` first verifies that the
player is still present in the registered club roster. If not, it exits.

For a rostered player it then:

1. returns an active loan through `0x41AA50` when status bit 6 is set;
2. invokes `0x471210(player,0,0)`;
3. clears status bits 1, 7, 8, 9 and 13;
4. calls `0x41EDF0`, which clears the already mapped loan-list bit 12 and
   decrements club `+0x1A8` when positive.

This cleanup occurs before the post-expiry grace decision.

## Ordinary post-expiry grace and final detachment

For ordinary `player+0x138 < 0xFE`, the function tests:

```text
current_date - 21 >= contract_expiry
```

Only once the player is at least **21 days past expiry** does it set
Out-of-contract bit 7 and call `0x41EF00(player, 1)`.

`0x41EF00` performs the actual ordinary controlled-player detachment:

- if the current club is user-controlled, `0x5CE460(player_id)` purges
  matching player-linked queued manager/mail entries before continuing;
- `0x417380` returns the player's already-proven 200-byte per-club
  **training record**; its word `+8` is set to `-1`, removing the training
  assignment;
- when current/temporary club `+0x72` equals registered club `+0x10`, it
  sets Out-of-contract bit 7, stores the old club ID in `player+0x74`,
  removes the player ID from that club roster through `0x4051F0`, and sets
  both club IDs `+0x10/+0x72` to `-1`.

This is a true free-player detachment and differs from the non-user monthly
`0x41ABC0` release branch, which can set Out of contract while club context
remains.

The ordinary controlled path contains **no shared CRT RNG** in expiry cleanup
or the 21-day-past-expiry detachment. Its only direct shared-CRT draw is the
pre-expiry assistant-manager suggestion `RNG(10)`.

## Separate +0x138 special/recycle branch

Values `player+0x138 >= 0xFE` take a different path and are intentionally
kept neutral here.

Direct facts:

- `0xFF` is an immediate pre-expiry return state;
- `0xFE` performs schedule/date tests and can promote the byte to `0xFF`
  while clearing `+0x164`;
- after expiry, any value >= `0xFE` bypasses the ordinary 21-day grace,
  clears injury bit 0, removes the player from the club roster, sets
  `player+0x74=-1`, moves both club IDs to global `0x8755D0`, then clears
  `+0x138/+0x164`.

Existing repository evidence proves `0x8755D0` is canonical club **332,
!Spare**, used by the game's player-generation/recycle machinery. Neighboring
`0x41ACA0 -> 0x41AD90` logic also performs an age/recycle transformation.
This strongly bounds the special branch as recycle/retirement-related state,
but the exact semantic name of `+0x138` is not promoted from inference.
It must remain neutral until a direct event/string/accessor link proves the
label.

## Pending/deal count +0x178 closed for the supported runtime

Direct writer tracing closes the second half of `0x41C6F0` sufficiently for
the existing clean-room deal model.

- fresh DBRPlayer construction initializes `player+0x178 = 0`;
- successful deal/workflow creation paths including `0x41FBD0` increment
  `player+0x178`;
- remover `0x417870` first removes the matching entry from global deal list
  `0x8774A8`, then decrements `player+0x178` only when it is positive;
- final club assignment `0x422F70` resets `player+0x178 = 0`.

The lookup half of `0x41C6F0` is also exact: `0x422950 -> 0x50E790 ->
0x50E590` returns true only for a matching global deal record whose state
dword is **3, 4, or 5**.

The modern `TransferRuntimeState` currently permits at most one
`DealInProgress` per player. Within that supported invariant, a matching live
deal record proves the original count is positive, so the controlled renewal
suppression can be represented exactly as:

```text
deal exists for player
AND deal.state in {3,4,5}
```

without inventing a second unsynchronized count field. If later work adds
multiple simultaneous deal records for one player, the explicit `+0x178`
count must be materialized at that time.

## Renewal clear path

Existing `0x419190(12) -> 0x419210` evidence remains applicable.
`0x419210` clears Out of contract and the mapped signed-for-another-club
state and clears `player+0x164`. It also schedules
**MPMClearNewPlayerSignedContract** for current date + 180 days; unrelated
still-unmaterialized status bits must not be invented.

## Clean-room implementation boundary

The source-backed ordinary controlled-player slice can now be implemented as:

- persistent renewal-suggestion latch corresponding to `player+0x164`;
- pre-expiry Out-of-contract set at 21 days;
- 112-day assistant-manager suggestion window with exact single
  `RNG(10) < 4` draw and Bosman/ordinary event kind;
- expired cleanup of mapped loan/transfer-list states;
- ordinary 21-day post-expiry detachment from roster and club IDs, plus
  training-record cleanup where that user training object is materialized;
- unified first-of-month contract iteration so AI and controlled players retain
  source club/roster ordering.

The `+0x138 >= 0xFE` special recycle branch, full MPMEAMail presentation,
and interactive Amend Contract response UI remain separate follow-up pieces.


## +0x138 special controlled-contract state bounded as non-fresh compatibility path — 28 September 2026

Follow-up after the ordinary `0x41BEE0` lifecycle audited the remaining neutral
`DBRPlayer+0x138` `0xFE/0xFF` branch without assigning a speculative label.

Direct xref result inside the DBRPlayer code region:

- fresh construction writes `+0x138 = 0`;
- save/load serialization reads/writes the byte;
- `0x41BEE0` reads it, promotes `0xFE -> 0xFF`, and later clears it;
- no separate fresh-game writer that sets `+0x138 = 0xFE` was found;
- the already mapped transfer-refusal reasons “player has decided to retire”
  and “player wants to stay for an upcoming testimonial” do not directly read
  or write `+0x138`.

The special expired branch itself is still instruction-bounded: it clears
additional player state, removes the player from the old roster, moves both club
IDs to the canonical `!Spare` parking team, then clears `+0x138/+0x164`.
That strongly places it beside player recycle/retirement machinery, but it does
not prove the field's semantic name.

Because no proven fresh-game producer exists, the clean-room keeps
`contract_special_state_138` neutral and returns
`SPECIAL_STATE_DEFERRED` for nonzero special states. This is recorded as a
legacy/original-save/recycle compatibility boundary rather than inventing a
fresh-game producer. It does not block the Gate-11 fresh core-management loop.

Gate-11 audit then identified the next reachable fresh-game gap: the startup
`0x61DF90 -> 0x41E510` youth path is fully represented in the RNG replay but
not yet materialized in GameState as the user's separate 20-slot youth list and
generated-player transformation. That youth workflow is the next active task.
