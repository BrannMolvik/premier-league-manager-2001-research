# Recovery556: original per-country support-staff candidate source, tags, and ordering

**Source:** owner's original footballmanager.exe (4,714,541 bytes), independently SHA-256-checked in the recovery shell as `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Original binary was statically disassembled, never executed. This is neither a Windows GUI observation nor complete staff generator integration.

## The actual source candidate producer

The country record at `0x874BE0` uses a **0x6C-byte** stride. Its dynamic candidate arrays are distinct from the `0x874BD0` grouped **player-name** source:

- `0x411440` populates each country **+0x38/+0x3C** exclusively from original expanded club records (not staff candidates or generated names).
- Source `0x4F7380` reads **`0x876C50` original 0x40-byte source records** and `0x876C44` instantiated source pointer pool. `0x4F8FF0` maps each instantiated object's signed word at +0x20 to an original 0x40-stride source record's +0x24 country index and hence the country record at `0x874BE0 + 0x6C * country`.
- `0x4F746E` and `0x4F7517` qualify candidate members **only when object+0x04 is zero**, increment country **+0x44** (all qualifying members), and then call candidate **virtual+0x24**. Only virtual tag values **1 or 3** increment country **+0x4C** and enter the source country **+0x48/+0x4C** selectable candidate array at `0x4F7546..0x4F7553`.
- Country +0x40/+0x44 and +0x48/+0x4C arrays are allocated per-country in `0x4F74B3..0x4F74EE`, populated at `0x4F7520` and `0x4F7546` respectively, and **sorted separately** at `0x4F756D..0x4F75A0`. The +0x48 selectable array is sorted with the comparator at **`0x4F79D0`**, which invokes the same actual object virtual+0x24 tag and compares original object+0x18. The 0x4F79D0 comparator places tag1 before tag3; on equal tags it places larger +0x18 values before smaller. Tied records return equality, so do not invent stable native qsort tie ordering.
- At `0x4CB2B0`, real fixed-staff vft+0x5C copies this country record's +0x38, +0x40 and **+0x48** pointer arrays via `0x4D1830`, and later selects through **its copied +0x48 list** (`0x4CB493`). Source country +0x50 is copied separately and used at `0x4CB3B9 / 0x4CB433` as a bound. Country+0x50 is NOT automatically equivalent to +0x4C just because those fields are adjacent.

## Exact candidate kind source virtual+0x24

Original `0x4F70E0` constructs instantiated candidates from `0x876C50` 0x40-byte source records. Its source-kind field is **record+0x14**:

| Native source-kind branch | Constructed class | Final vtable | vft+0x24 |
| --- | --- | --- | --- |
| kind 1, source record+0x04 != 0x1B | `0x4F3F60` | `0x7C9AC0` | `0x5B6380`: returns byte **1** |
| kind 2 | `0x4F51E0` | `0x7C9B58` | `0x4F6EA0`: returns byte **2** |
| kind 3 | `0x4F3F00` | `0x7C9A80` | `0x4F3F50`: returns byte **3** |
| kind 1, record+0x04 == 0x1B | `0x4FABD0` | `0x7C9C94` | **`0x4FAFE0`**, NOT a constant-byte getter; this special object is **NOT YET QUALIFIED** |

**Critical special-case boundary:** The normal-kind paths alone do not prove that EVERY source kind1 element is accepted or that the rare kind1 +0x04==0x1B subclass has a constant eligibility tag. The source vtable for that subclass differs; do not coerce it to return 1. Recover reachability, class semantics and original input state before including it in an exact eligible count.

## Earlier stage can also consume original CRT draws

`0x4F6B10` (and analogous `0x4F6820`) use original `0x64D540(current_count)` inside a decreasing-count loop for source-record shuffling when count>1, before a comparator-based sort. These are **real original RNG consumers conditional on helper reachability and count**, not candidate selection in the later `0x4CB2B0` function itself. Their exact callers and whether they are mandatory on fresh start remain under audit. The prior fixed-staff 12–18 draw estimate is superseded regardless: both preconstruction and constructor conditional routes must be accounted for against the **same source CRT seed**. No production RNG calls were added.

## Verified control chain versus remaining unknowns

1. `0x4F7380` preallocates active source-candidate pointer list, maps entries to country records, filters by active state and dynamic tag, allocates/fills two separate per-country arrays, and sorts them.
2. `0x4CB2B0` selects from the sorted country +0x48 candidate list under conditional source bounds and a virtual+0x24 tag acceptance check, and can consume multiple bounded CRT draws.
3. Country candidates are NOT interchangeable with the `0x421BA0` **player-name** groups. Group initialization, source RNG, name RNG, support staff factory and UI/modal effects need one reconciled transaction.
4. **Still unknown:** exact original serialized producer for `0x876C50` in the current normal startup, kind1 special callback semantics/reachability, the candidate input+0x18 values and comparator ties, group count `country+0x50` derivation, potential additional RNG in indirect method calls, exact fresh-game seed and all seven user selector input/modal semantics.

## Reproduce from SHA-matched private executable

```bash
objdump -D -Mintel --start-address=0x4f70e0 --stop-address=0x4f72cb footballmanager.exe
objdump -D -Mintel --start-address=0x4f7380 --stop-address=0x4f75b0 footballmanager.exe
objdump -D -Mintel --start-address=0x4f79d0 --stop-address=0x4f7a28 footballmanager.exe
objdump -D -Mintel --start-address=0x4f8ff0 --stop-address=0x4f900f footballmanager.exe
objdump -D -Mintel --start-address=0x4f6b10 --stop-address=0x4f6ba3 footballmanager.exe
objdump -D -Mintel --start-address=0x4f6820 --stop-address=0x4f689f footballmanager.exe
objdump -s -j .rdata --start-address=0x7c9a80 --stop-address=0x7c9cc0 footballmanager.exe
```

**Next:** trace the fresh-start caller and exact source file/record producer for the `0x876C50` 0x40-byte pool, reconcile special-kind1 and +0x50 count semantics, then qualify all constructor and preconstructor CRT draws before any live SupportStart staff state modification. Continue to original seven-row modal, Apply/Cancel/TeamSelect return, selected Inbox, R1 full match, broader original leagues/multihuman and Gate13–17 Windows11 acceptance. No PR/CI triggered by this evidence checkpoint.


## Recovery556 follow-up: exact source pool owner and serialized-array boundary

Full original .text cross-reference scan of global `0x876C50` identified its construction, not just consumers:

- `0x4F38A0` zero-initializes `0x876C4C` count and `0x876C50` pointer, gives owner `0x876C48` a vtable at `0x7C9984`, and stores **`0x876C48` into indirection `0x874BA4`**.
- `0x4F38E0` obtains its owner+0x04 count and allocates **0x40 bytes per record**, initializing each element with vtable `0x7C9998`. Thus the original `0x876C50` record stride is confirmed by the native allocator, not guessed from its consumers.
- `0x4F70E0` walks this same 0x40-byte pool, using its native +0x14 byte type and +0x08 source linkage to construct the polymorphic candidate object. `0x4F7380` then maps eligible object pointers to country +0x40/+0x48 arrays. `0x4F8FF0` gets the actual country mapping from original source owner +0x24, not from the candidate name/player nationality.
- `0x4DA069`, `0x4DA0B0`, `0x4DA0C0` and `0x4DA2FF` retrieve source owner via `0x874BA4` and virtual pointer access; they are **downstream staff/mode consumers**, not proof of where the source pool was read from disk.
- No original file path or whole-catalog producer for the 0x40-byte records has yet been proven. The source vtable linkage supplies an exact independent cross-reference target for the next recovery: find **the actual loader invoking the 0x7C9984 owner** and its authenticated original file/record stream before claiming the eligible records, country populations or original deterministic RNG seed.

The source pool `0x876C50`, original club country vector `0x874BE0+0x38` and player-name group `0x874BD0` are **three different source owners**. Do not conflate them or initialize the port's visible SupportStart lists from a synthetic guessed collection.

Reproduction:
```bash
objdump -D -Mintel --start-address=0x4f38a0 --stop-address=0x4f3920 footballmanager.exe
objdump -D -Mintel --start-address=0x4f70e0 --stop-address=0x4f7257 footballmanager.exe
objdump -s -j .rdata --start-address=0x7c9984 --stop-address=0x7c99b0 footballmanager.exe
```
