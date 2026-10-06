# Gate 13 Squad status lifecycle: special Non-EU and mode-1 Cup-Tied fallback

_6 October 2026. Recovery 342. Evidence tier: first-hand disassembly of the hash-verified canonical executable._

## Source identity

The authorized Library disc archive was rematerialized and the root executable
was re-extracted from the MODE1/2352 Joliet image. The recovered executable is
4,714,541 bytes and independently hashes to:

```
SHA-256 footballmanager.exe:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
```

No executable, disc image, archive, or raw disassembly is committed to Git.

## PSCF status override order

`DBRPlayer::0x418360` applies these relevant override branches after the
direct Injured/Banned/International statuses:

1. alternate On-loan frame 13 when the loan flag is active and current/registered
   club identities differ;
2. special Non-EU frame 12 when the player has DBRPlayer `+0x14` bit 11, its
   registration record resolves, and that record's cutoff predicate is false;
3. Cup-Tied frame 3 from `0x418480`;
4. lower status-bit/table fallbacks.

This preserves the already-merged fail-closed requirement that a represented
Non-EU state blocks lower Cup-Tied publication until the special registration
lifecycle is modeled exactly.

## Bit-11 predicate and startup lifecycle

`0x41B490` reads DBRPlayer `+0x14` bit 11. `0x41B4A0` sets it.

`0x421760` is the exact eligibility predicate already reconstructed as
`derive_non_eu_status()`:

- for club country ID 33, it checks the player's nationality country's
  `european_index == 0`;
- otherwise, only player EU-status code 1 enters the alternate branch, where an
  unresolved nationality or nationality-country `eu_status_flag == 0`
  qualifies.

The loaded-player pass at `0x421CE0` iterates the runtime player array, calls
`0x421760`, and for every positive result calls `0x417A20`. `0x417A20`
sets bit 11 and calls `0x4E9F10` to create the player's registration record.
Therefore the clean startup `RuntimePlayer.non_eu` value is backed by the same
native eligibility predicate rather than by a presentation-only guess.

## Registration record and frame-12 cutoff

The record constructor `0x4E99D0` stores:

- `+0x04`: player ID;
- `+0x14`: DBRPlayer `+0x154`;
- `+0x18`: `+0x14 - 365 * RNG(4)`;
- other counters/fields not needed by the current status decision.

Independent constructor/contract tracing closes DBRPlayer `+0x154` as the
player's contract-expiry date. The shared month-advance behavior is already
represented by `contract_expiry_from_month_span()`.

`0x4E9BE0` returns true exactly when:

```
current_game_date <= record.cutoff_14
```

Because `0x418360` returns frame 12 only when this predicate is false, the
special alternate Non-EU status is shown when:

```
bit11 && registration_record_exists && current_game_date > record.cutoff_14
```

For the normal initialized record, `record.cutoff_14` is the player's
contract-expiry date.

`0x4193E0` obtains the bit-11 registration record and updates its `+0x14`
cutoff from the player's current `+0x154` contract expiry through
`0x4E9BA0`. The contract-renewal/finalizer paths call this update when bit 11
is active, so the status cutoff follows the live contract expiry rather than a
one-time startup copy.

`0x41AFE0` is a full player reset/removal path. When bit 11 is active it clears
the bit and removes the corresponding record from global collection
`0x876B30`. This is a proven clearing lifecycle, but it is not evidence that
ordinary club transfers clear the bit.

## Ordinary transfer bit-11 transition source-closed

The ordinary transfer mutation `0x422F70` installs the destination club in
DBRPlayer `+0x10/+0x72`, resets other transfer-related status bits, and ends
by calling the contract finalizer `0x4192B0`. The complete function body was
checked through its `ret 0x0C`: none of its status masks clear bit 11.
`0x4192B0` writes the new contract expiry to `+0x154`; when bit 11 was
already active it calls `0x4193E0`, which resolves the bit-11 registration
record and synchronizes its cutoff through `0x4E9BA0`.

The previously separate `0x4EF600` path is now tied to ordinary transfer
completion events. Its only two direct call sites are:

- `0x5EAEFD`, in the class whose native event name is
  `TransferDealConcluded`;
- `0x5EAF57`, in the class whose native event name is
  `FreeTransferDealConcluded`.

Both conclusion handlers invoke `0x4EF600` with mode 0 for their transfer
subobject. `0x4EF600` resolves the player, calls exact eligibility predicate
`0x421760`, and on a positive result calls `0x41B4A0`. The latter is a
direct unconditional setter: it ORs DBRPlayer `+0x14` with bit 11 and returns
true. On a negative eligibility result, `0x4EF600` does not clear bit 11.

A newly set post-transfer bit need not already have a record. The status
override at `0x418360` calls `0x41B4D0` before testing the frame-12 cutoff;
`0x41B4D0` looks up the player in global collection `0x876B30` and, if the
bit is active but the record is absent, calls `0x417A20` to create it before
returning the record. Thus the transfer conclusion can set the bit and the
native status/contract paths lazily materialize the corresponding record.

The source-backed ordinary-transfer transition is therefore sticky rather than
symmetric: an eligible transfer can set bit 11, while a later ineligible
transfer leaves an already-active bit intact. The proven clearing path remains
the full reset/removal routine `0x41AFE0`, which explicitly clears bit 11 and
removes the player's record from `0x876B30`. The broader initialization/reset
routine `0x4185B0` also contains a bit-11 clear as part of its wholesale
status reset, but it is not part of `0x422F70` or either concluded-transfer
handler.

## Mode-1 Cup-Tied fallback correction

The `0x418480` mode-1 negative fallback is now narrowed further:

- a positive `0x4F8E40` collection lookup still returns Cup-Tied immediately;
- otherwise `0x419350` succeeds only when DBRPlayer `+0x1A0 > -1`;
- `0x419350` then returns the DWORD at embedded object
  `DBRPlayer+0x198 + 0x18` through helper `0x4EBE80`;
- global selector `0x8755E8` chooses cutoff `0x8755EC` for mode 1 or
  `0x8755F0` for mode 2;
- the fallback is positive only when the recovered player value is greater than
  the chosen cutoff.

Earlier wording that treated `0x419350` as a list-first-element lookup is
incorrect and is superseded by this trace. The semantic meaning and producer
lifecycle of embedded `+0x198/+0x18`, `+0x1A0`, and the two global cutoffs
remain unresolved, so the negative mode-1 path stays fail-closed.

## Recovery 346 transfer-history identity

The remaining embedded mode-1 fallback state has been narrowed further from
first-hand source tracing:

- DBRPlayer `+0x198` is the embedded `CPlayerTransferHistory` object;
- DBRPlayer `+0x1A0` aliases that object's `+0x08` club-table index/club ID;
- `CPlayerTransferHistory +0x18` is a transfer/join-history date;
- startup initializes that date from normalized DBRPlayer
  `+0x158` current-club join date.

The remaining mutation boundary is the `0x422E7E` call into
`CPlayerTransferHistory::0x4EBF60`. Its full argument mapping must be closed
before the clean runtime can claim equivalent history updates. The producer and
semantic identities of global selector/cutoffs `0x8755E8/0x8755EC/0x8755F0`
also remain unresolved.

## Current implementation boundary

PR #497 candidate `45c5c0e09c9fec420160e9e60eedf304423fcfd9`
implements the now source-closed special Non-EU lifecycle:

- direct frames 0/1/2 remain highest priority;
- exact alternate On-loan frame 13 remains higher priority;
- active bit 11 plus `current_date > contract_expiry_date` publishes frame 12;
- active bit 11 with a still-current cutoff allows the lower positive
  source-qualified Cup-Tied predicate to run;
- ordinary completed transfers apply the source-proven sticky bit-11 set-only
  transition;
- missing/invalid cutoff state and the unresolved mode-1 negative Cup-Tied path
  remain fail-closed.

The exact candidate is green in reconstruction run `37467142990`, Gate-13
presentation run `37467143159`, and asset-policy run `37467143070`.

## Exact next source task

1. Finish the `0x422E7E -> CPlayerTransferHistory::0x4EBF60` argument/update
   mapping and identify every mutation of embedded `+0x18` / `+0x08`.
2. Trace the runtime producers and semantic identities of
   `0x8755E8/0x8755EC/0x8755F0`.
3. Only after that value/cutoff transition is source-closed should the
   mode-1 negative Cup-Tied fallback be promoted into live presentation.

Recovery 347 rematerialized the authorized Library archive successfully, but
the current execution sandbox cannot launch shell/Python processes. That is an
execution-environment blocker, not source loss; the exact trace above remains
the next private-source action when a functioning sandbox is available.

Gate 13 remains open independently for Daniel's normal Windows 11 acceptance in
issue #482.


## Recovery 353 — transfer-history constructor/update mapping

First-hand disassembly of canonical `footballmanager.exe`
(SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`)
closes the remaining `0x422E7E -> CPlayerTransferHistory::0x4EBF60`
argument mapping.

The caller stages six DWORD arguments across the callee-cleanup boundaries of
`0x5E43B0` and `0x5E48D0`. At the final call, `ecx` points at embedded
DBRPlayer transfer history `+0x198`, and `0x4EBF60` stores:

- `CPlayerTransferHistory +0x08` <- sign-extended DBRPlayer `+0x74`;
- `+0x10/+0x14` <- qword/double result from `0x5E48D0`;
- `+0x18` <- zero-extended DBRPlayer WORD `+0x18C`;
- `+0x1C` <- global `0x9847FC`;
- `+0x20` <- zero.

The exact callee is a six-DWORD setter and ends in `ret 0x18`.
Nearby `0x4EBF90` independently writes only transfer-history `+0x18`, while
`0x4EBF00` serializes `+0x08`, the qword at `+0x10`, `+0x1C`,
`+0x20`, and `+0x18`.

The Cup-Tied selector/cutoff globals are narrowed but not yet source-named.
Direct read sites at `0x40729B`, `0x4180B0`, `0x418426`, and
`0x418533` consistently implement:

- selector `0x8755E8 == 1` -> cutoff `0x8755EC`;
- selector `0x8755E8 == 2` -> cutoff `0x8755F0`;
- comparison against the value returned through `0x419350`.

All three globals are zero in the PE image, have only those direct absolute
read xrefs, and have no direct absolute store xrefs. Their runtime initialization
is therefore still unresolved and likely indirect or part of a larger
contiguous global state load. Keep the negative mode-1 Cup-Tied fallback
fail-closed until that producer and the precise `0x419350` value meaning are
source-closed.


## Recovery 354 — correction: transfer-history +0x18 is an appearance count

Recovery 353 closed the mechanical setter/getter path but retained an inherited
description of transfer-history `+0x18` as a date. Further first-hand
disassembly disproves that interpretation.

The DBRPlayer source field is WORD `+0x18C`. Its lifecycle is:

- `0x41B7E0` runs from the appeared-player post-match path and increments
  WORDs `+0x188`, `+0x18A`, and `+0x18C`;
- `0x41BA00`, used when the player does not appear in the relevant match
  context, increments `+0x18A` but not `+0x188/+0x18C`;
- `0x41BCB0` tests `+0x18C` at the exact milestones 10, 20, and 50;
- `0x41B22F` separately requires `+0x18C > 15` in another player-event
  branch;
- `0x422E4C -> 0x4EBF60` snapshots zero-extended `+0x18C` into embedded
  transfer-history `+0x18` before the later reset path;
- `0x423029` clears DBRPlayer `+0x18C` to zero as part of that wholesale /
  current-club reset;
- `0x419350` checks transfer-history `+0x08 > -1`, calls getter
  `0x4EBE80`, and returns exactly transfer-history `+0x18`; otherwise it
  returns `-1`.

Together these operations source-close `+0x18C` / transfer-history
`+0x18` as an actual-appearance count associated with the prior/current club
tenure, not a calendar date.

This also narrows the previously neutral Cup-Tied globals: `0x8755EC` and
`0x8755F0` are numeric appearance-count cutoffs selected by
`0x8755E8` modes 1 and 2 respectively. The rule names, units beyond this
count comparison, and producer/configuration loader are still unresolved.

A separate structural false lead is closed: global `0x874B88` is initialized
by `0x40BBB0` as a four-DWORD dynamic-array header
(vtable/count/data/fallback), with 0x2A8-byte elements. Therefore addresses
`0x8755E8/EC/F0` are not fields at offsets `+0xA60/+0xA64/+0xA68` of
that object. Tactics string helpers that use those offsets on other object
types are unrelated and must not name the Cup-Tied globals.

The negative mode-1 Cup-Tied fallback remains fail-closed until the standalone
global selector/cutoff loader is source-closed.
