# Gate 11 Morale Lifecycle

_Last updated: 29 September 2026_

## Scope

This note records the source-backed ordinary DBRPlayer morale work reached from
Gate 11. It separates confirmed executable behavior from still-unintegrated
morale producers.

Canonical executable:

```text
FOOTBAL.EXE
SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
```

## Confirmed state field and tuning

DBRPlayer byte `+0x18E` is the live morale value. The tuning loader around
`0x505700` maps the following original keys:

| Address | Original key | Runtime meaning |
| --- | --- | --- |
| `0x821C20` | `unhappynessrequestnewcontract` | morale decrease amount used by `0x5D8430` |
| `0x821C21` | `unhappynesslostmatch` | post-match loss decrease |
| `0x821C22` | `unhappynesswonmatch` | post-match win increase |
| `0x821C23` | `unhappynesswontrophy` | trophy-related morale amount; producer not yet integrated |
| `0x821C24` | `unhappynessnotplayed` | eligible non-appearance decrease |
| `0x821C25` | `maximummorale` | upper morale cap |
| `0x821C26` | `loanmorale` | increase used by `0x41A9D0` |
| `0x821C27` | `signednewcontactmorale` | increase used by contract/signing paths |
| `0x821C28` | `dangermoralelevel` | threshold consumer; not yet integrated |

The shipped values used by the current post-match slice are:

```text
GoodLeadership       25
UnhappyLostMatch      7
UnhappyWonMatch      10
UnhappyNotPlayed      8
MaximumMorale       100
```

## Exact primitive arithmetic

### Decrease: `0x41BA80`

The function always consumes one scaled `RNG(2)`. With base amount `B`:

```text
modifier = -1
if leadership >= GoodLeadership: modifier -= 2
if age > 15:                     modifier -= 1
if age < 11:                     modifier -= 1
amount = B + RNG(2) + modifier
```

If `amount <= 0`, morale is unchanged. Otherwise it subtracts the amount and
clamps at zero.

### Increase: `0x41BB10`

The function always consumes one scaled `RNG(2)`. With base amount `B`:

```text
modifier = 2 * (leadership >= GoodLeadership)
modifier += (age > 15)
modifier += (age < 11)
amount = B + RNG(2) + modifier + 1
```

The result is capped at `MaximumMorale`.

The explicit final `+1` is instruction-visible at `0x41BB66`. This corrected
a newly added regression that initially expected one point too little.

## Premier League post-match ownership and RNG order

The club post-match pass `0x404CE0` walks the club roster in roster order.

For a player who appeared, it routes to `0x41B7E0`:

- loss flag: call `0x41BA80(UnhappyLostMatch)`;
- win flag: call `0x41BB10(UnhappyWonMatch)`;
- draw: neither morale primitive runs;
- then run the already-recovered `0x41B870` Form transition for that same
  player before advancing to the next roster entry.

For a player who did not appear, `0x41BA00` first applies the source-backed
availability gate. Eligible non-appeared players consume `RNG(10)`; values
0..3 call `0x41BA80(UnhappyNotPlayed)`. Unavailable players consume no
not-played morale RNG.

Therefore morale and Form draws are interleaved per roster player. They must not
be implemented as separate whole-roster phases.

## Clean-room integration

Commit `0b567986ec8b51b9f66c8e038de7aa9726088535` integrated the recovered
post-match morale path into both AI and human Premier League fixture completion.

Commit `130a929fe1e5505a77951b7c190b1d9e374f1b57` corrected the
`0x41BB10` regression expectations to include the executable's explicit final
`+1`.

GitHub Actions at `130a929f`:

- reconstruction suite: **668 tests run, 2 failures**;
- both failures are the unchanged pre-existing secondary-schedule assertions;
- all morale tests pass;
- repository asset policy passes.

## Signed-contract finalizer: `0x419210`

Direct reinspection of the canonical executable closes the exact trailing order
of the common signed-contract finalizer.

After its status/event work, `0x419210` does:

```text
0x41927F xor eax,eax
0x419281 mov ecx,esi
0x419283 mov al,[0x821C27]      ; SignedNewContactMorale
0x419288 push eax
0x419289 call 0x41BB10          ; exactly one RNG(2)
0x41928E mov byte [esi+0x164],0 ; renewal-suggestion latch
```

So the morale draw occurs **before** the final `DBRPlayer+0x164` clear. This
matters to deterministic state observers even though the latch does not alter
the arithmetic itself.

The clean-room now centralizes this exact trailing slice in
`apply_signed_contract_finalizer_morale`. Ordinary completed transfers, AI
renewals, and both youth contract paths use it. The destination/contract state
is installed by each caller first; the helper then consumes
`SignedNewContactMorale RNG(2)` and clears the renewal-suggestion latch.

## Loan assignment: `MPMLoanPlayer -> 0x41A9D0`

RTTI already identified vtable `0x7D7D54` as `MPMLoanPlayer`. Its
constructor at `0x61B5E0` schedules execution for current date **+2 days**
and stores the player/destination identifiers at object `+0x08/+0x0C`.
`MPMLoanPlayer::Execute` at `0x61B620` eventually resolves those records and
calls `0x41A9D0`.

The exact materialized ordering inside `0x41A9D0` is now bounded:

1. write the temporary/loan club ID to player `+0x10` while registered club
   `+0x72` remains unchanged;
2. perform destination-club bookkeeping;
3. update the recovered loan/status state, including calling `0x41EDF0`
   before setting `DBRPlayer+0x14 bit 6`;
4. perform the remaining controlled-club bookkeeping;
5. only at `0x41AA3A..0x41AA43`, load `LoanMorale` from `0x821C26` and call
   `0x41BB10`.

Therefore **LoanMorale is the final operation in `0x41A9D0`** and consumes
exactly one `RNG(2)` after the loan state has already been installed.

The clean-room function `complete_player_loan_assignment` materializes only
the already-understood state slice: `loan_club_id`, the proven loan-list
clear, then `LoanMorale`. Status bits whose runtime meaning is still neutral
are deliberately not guessed.

This also proves that the fresh startup loan-list replay must **not** add a
LoanMorale draw for the Matthew Upson/Watford candidate. The user-controlled
Arsenal branch at `0x41AAE0` queues the loan proposal/event and consumes its
separate `RNG(5)`; it does not execute `0x41A9D0` at that point.

## Request-new-contract morale is load-only on the fresh path

RTTI identifies vtable `0x7D7D74` as `MPMNewContractRequest`. Its virtual
action at `0x5D8430` resolves the stored player ID from object `+0x08`, loads
`UnhappyRequestNewContract` from `0x821C20`, and calls `0x41BA80`.
Therefore an executing legacy object consumes exactly one morale `RNG(2)`.

The producer audit found no ordinary fresh-game constructor:

- the generic MPM factory at `0x6139E0` maps type ID **10** to the
  `MPMNewContractRequest` vtable;
- the only literal write of vtable `0x7D7D74` is that factory case;
- exhaustive rel32 xrefs show the only call to `0x6139E0` is from
  `0x613FC0` inside the MPM deserialization loop `0x613F80`;
- `0x613F80` itself is reached from the broader save-load routine at
  `0x50E108`;
- `0x5D8430` has no direct code callers, only its vtable slot.

So the shipped executable can **load and execute** an existing serialized
new-contract-request process, but no fresh-game producer has been found.
Gate 11 must not manufacture this morale decrease in ordinary progression.
It remains a save/compatibility boundary, analogous to other loadable legacy
event state.

## Remaining ordinary morale xrefs

The signing/loan RNG-placement dependency is closed. Remaining source-backed
morale work is deliberately narrower:

- special contract cleanup at `0x41C052` also calls
  `0x41BB10(SignedNewContactMorale)`, but the `+0x138` special-state
  producer is already bounded as legacy/compatibility-only for the fresh path;
- `0x5D8430 -> 0x41BA80(UnhappyRequestNewContract)` is now bounded as a
  serialized/load-only `MPMNewContractRequest` compatibility path with no
  proven fresh producer;
- `UnhappyWonTrophy` and `DangerMoraleLevel` remain to be closed; the latter
  already has a reachable post-match consumer and is the next active slice.

Regression coverage now observes state at the instant `RNG(2)` is requested:
the signing latch is still set during the draw, while loan temporary-club and
loan-list state are already installed/cleared during the draw.
