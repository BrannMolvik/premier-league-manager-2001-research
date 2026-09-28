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

## Remaining ordinary morale xrefs

The next source-backed morale slice should follow the already-materialized
transfer/contract state rather than inventing passive drift:

- `0x419210 -> 0x41BB10(SignedNewContactMorale)`;
- `0x41A9D0 -> 0x41BB10(LoanMorale)`;
- special contract cleanup at `0x41C052` also calls
  `0x41BB10(SignedNewContactMorale)`;
- `0x5D8430 -> 0x41BA80(UnhappyRequestNewContract)` belongs to a separate
  request/event object and must not be attached until that producer is bounded;
- `UnhappyWonTrophy` and `DangerMoraleLevel` have source tuning but their
  ordinary producer/consumer lifecycle is not yet integrated.

Exact next task: instruction-close the ordinary signing/loan caller chains and
place their one `RNG(2)` morale draw at the correct point in the existing
transfer/contract runtime. Defer the request-new-contract event and trophy path
until their producers are independently bounded.
