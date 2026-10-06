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

## Current implementation boundary

No new Squad frame is enabled by this research checkpoint. Merged behavior
remains:

- direct frames 0/1/2;
- exact alternate On-loan frame 13;
- positive current-day Cup-Tied frame 3 when source context is proven;
- Non-EU and unresolved negative paths fail closed.

## Exact next source task

1. Trace the producers/semantic identity of DBRPlayer embedded
   `+0x198/+0x18`, gate `+0x1A0`, and globals `0x8755E8/EC/F0`.
2. Reconcile the now-closed sticky bit-11/registration lifecycle with the clean
   runtime and add frame 12 only with equivalent record/cutoff semantics.
3. Only after the embedded-value/cutoff transition is source-closed should the
   mode-1 negative Cup-Tied fallback be promoted into live presentation.

Gate 13 remains open independently for Daniel's normal Windows 11 acceptance in
issue #482.
