# Gate 11 Out-of-contract lifecycle

Verified against the canonical FM2001 `FOOTBAL.EXE` with SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

This note continues the scouting status work after DBRPlayer `+0x14` bit 7
was identified as the original **Out of contract** state. It records the
ordinary monthly contract-maintenance producer far enough to implement the
non-user club path without replacing the original logic with a simple
`contract_expiry_date <= current_date` rule.

## Monthly caller and ordering

The normal calendar path reaches contract maintenance only on day-of-month 1:

```text
0x4A81A0 -> 0x40BB10 -> 0x4042E0
```

`0x40BB10` walks the runtime club table. `0x4042E0` walks each club roster
in stored roster order. For every player it first calls monthly development
`0x41EAD0`, then immediately calls contract maintenance `0x41ABC0`.

Therefore the source ordering is:

1. first day of the month;
2. club-table order;
3. roster order inside each club;
4. that player's monthly development;
5. that player's contract maintenance.

The monthly development arithmetic itself consumes no shared CRT RNG, so a
clean-room hook that performs the deterministic development pass before the
contract pass preserves contract RNG order as long as the contract pass still
walks club/roster order.

## User-controlled branch is separate

`0x41ABC0` begins by resolving the player's active/current club and testing
club helper `0x4037B0`, already mapped as user control. A user-controlled
player is delegated to `0x41BEE0`; the ordinary AI decision logic below is
not run for that player.

The `0x41BEE0` path is event-driven and has materially different expiry
handling. Direct tracing confirms at least one branch does not set bit 7 until
the current date is at least 21 days beyond expiry, while other expired-player
branches can alter club/roster state. This path must remain separate until its
events and transitions are completely reconstructed.

## Non-user 0x41ABC0 decision window

For a non-user club player, `0x41ABC0` compares current date + 30 days with
contract expiry `player+0x154`.

If expiry is more than 30 days away, the routine returns with **zero RNG
consumption**.

Once the player is inside the 30-day window, the routine consumes the shared
MSVC CRT stream exactly as follows.

### Rating below 50

Let `rating = 0x41E1D0(player)`, already reconstructed as the best of the
player's three preferred-role ratings.

The first draw is `RNG(100)`.

- if the first draw is below 8, the routine enters the possible-release branch
  immediately and consumes only that one draw;
- otherwise it consumes a second `RNG(100)` and renews. For a rating below
  50, the second draw cannot make the player a release candidate.

Thus a sub-50 player becomes a release candidate exactly when the first draw
is below 8, an 8% branch.

### Rating 50 or above

The routine consumes **two** `RNG(100)` draws. The first draw does not decide
the final release outcome for this rating band. The player enters the
possible-release branch exactly when the second draw is below 2.

Thus a 50+ player has the source-backed 2% second-draw release branch and always
consumes two draws inside the decision window.

## Release eligibility after the random branch

A random release candidate is still renewed unless every following condition
passes:

- registered club roster count is strictly greater than 18;
- `0x419390(player) > 104`, meaning more than 104 completed weeks at the
  current club;
- player age from `0x4173B0` is strictly greater than 23;
- `0x417580(player) == 1`.

`0x417580` is now instruction-bounded:

- it first requires `0x417460(player) == 0`;
- `0x417460` is true iff signed dword `player+0x64 > -1`;
- it then requires current/active club word `+0x72` to equal registered club
  word `+0x10`.

The clean-room equivalents are therefore the existing neutral
`ai_transfer_block_value_64 <= -1` state plus no active loan/temporary-club
assignment.

## Successful Out-of-contract transition

When all random and eligibility gates pass, `0x41ABC0`:

1. calls `0x41B530`, the already-proven transfer-list transition family;
2. sets DBRPlayer `+0x14` bit 7, **Out of contract**;
3. writes zero to player byte `+0xC0`.

Importantly, this path does **not** itself clear the player's club IDs.
Therefore Out-of-contract cannot be represented as a computed
`club_id < 0` property. It needs persistent RuntimePlayer state.

The modern neutral `startup_month_span` field corresponds to `+0xC0`, so a
successful transition can source-faithfully set that field to zero.

## Renewal path

Every non-user player inside the 30-day decision window who does not complete
the successful release path reaches:

```text
0x41AC87: push 0x0C
0x41AC8B: call 0x419190
```

`0x419190` adds 12 calendar months to the existing contract expiry and then
calls `0x419210`.

For the materialized state already represented in the clean-room runtime,
`0x419210`:

- clears DBRPlayer `+0x14` bit 7, therefore clears **Out of contract**;
- clears `player+0x174` bit 7, the already-mapped
  `signed_for_other_club` state.

The same routine also mutates still-unmaterialized status/event fields. Those
must not be invented merely to implement the recovered contract lifecycle.

## Explicit release helper is distinct

`0x4177C0` is a separate explicit release/detachment transition. On success it
clears the main status dword, sets only bit 7, clears the secondary status
dword, and detaches the player from both club IDs by writing `-1`.

That is different from the monthly `0x41ABC0` successful release branch,
which can set Out-of-contract while club ownership/roster context still exists.
The two transitions must not be collapsed into one generic “expiry” setter.

## Clean-room implementation boundary

The next source-backed implementation slice is:

- persist `RuntimePlayer.out_of_contract`;
- reproduce the non-user monthly `0x41ABC0` decision, eligibility and exact
  shared-CRT draw count/order;
- execute it on first-of-month club/roster order after monthly development;
- renew by adding exactly 12 calendar months and clearing the mapped states;
- use live `RuntimePlayer.out_of_contract` in mapped scouting;
- persist the flag in the internal save.

The user-controlled `0x41BEE0` expiry/event path and the explicit
`0x4177C0` release action remain separate follow-up work. No implementation
should claim those paths are complete merely because the non-user monthly
producer is live.
