> **CORRECTIVE SOURCE AUDIT, Recovery556, 12 October 2026:** The 0x40-byte `0x876C50` source pool identified below is the original **Static.dat competition definitions**, not a special source pool of staff candidates. Native `0x4F7020` is called directly during the game's Static.dat file load at `0x50D4C8`, and consumes 193 competitions followed by 1,053 rounds. The existing `reconstruction/fm2001_data.py` parser already decodes these source records correctly. Also the kind1 / competition ID27 special subclass's vft+0x24 is **0x5B6380** and returns 1 (same as other leagues). Its vft+0x28 is **0x4FAFE0**; the earlier table shifted this slot. The older unknown-file/unknown-special-kind1 statements below are **SUPERSEDED**, not implementation blockers. See detailed correction at the end. Other candidate-state/CRT/UI unknowns remain open.

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


## Corrected source identity and exact actual Static.dat record verification (Recovery556)

The previously listed source-owner address `0x876C48` is the original **competition-definition array owner**. In the original loader:

1. `0x50D443..0x50D45D` opens literal `"static.dat"` from the original executable at `0x827E98` with read-binary mode and retains its original FILE pointer in ESI.
2. `0x50D47D` reads the original 209 country records, `0x50D48D` reads the 209 nationality name-group labels. Further original position-related vectors are read through `0x50D4BD`.
3. **`0x50D4C2` passes the SAME FILE handle to `0x4F7020`**. `0x4F702C` calls generic array deserializer `0x64CB40` with `0x876C48`, followed at `0x4F7038` by a second array deserializer on `0x876BD0`. The original `0x876C48` element vft+0x0C = `0x40F760` reads exactly **53 bytes serialized per 0x40-byte expanded competition object**, matching `reconstruction/fm2001_data.py` original COMPETITION_RECORD_SIZE=53.
4. Actual private extracted `FM2001/Static.dat` was independently raw-byte retrieved from owner Drive and SHA-256 verified: **86,929 bytes**, SHA256 `e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8`. Starting at verified offset `0x2726`, original u32 source competition count is **193**, IDs exactly 0..192, then 193×53-byte competition records. After these rows, exact offset `0x4F1F` contains source u32 **1,053**, beginning the original round array read second by `0x4F7020`.
5. All 193 actual serialized competition entries have original kind byte at record+14: **34 kind1 leagues, 29 kind2 cups, 130 kind3 dummy leagues**. Source competition ID27 is kind1, confirming the special Scotland subtype. This is original corpus evidence, not evidence that all 193 instantiate/are eligible in current runtime or that particular countries have a particular number of active candidates.
6. Existing **`FM2001Database._parse_competitions`** already reads `Static.dat + 0x2726`, count, 53-byte rows, exact kind+14, source index+0, country/region+27, parent reference+4; existing **`_parse_rounds`** reads source offset `0x4F1F`, 1,053×36 bytes. Future reconstruction **must reuse those verified original fields**, not add a separate 0x40 record parser/new synthetic staff data pool.
7. **Second independent virtual-table correction:** actual `0x7C9C94+0x24 = 0x5B6380`, constant tag 1; `+0x28 = 0x4FAFE0`, the adjacent dynamic serialization function. ID27 is a special league subclass with added behavior, but its original virtual+0x24 remains the same class1 tag. All four kind1/2/3 object virtual+0x24 results are now source-qualified for these classes.

**Interpretation:** `0x4F7380` constructs active runtime COMPETITION objects and groups certain competitions by country. CSupportStaff method `0x4CB2B0` later uses those runtime competition groups when composing staff details/associated records. This is NOT a source for six staff personal names, which are selected separately from the original PLAYER source groups `0x421BA0`. Do not rename or reclassify the player-name tables.

**Remaining true blockers:** exact runtime instantiated active competitions, their dynamic virtual methods/fields and their grouping order (especially country+0x50), source startup ordering and shared CRT state, screen control callback/hit ownership, and original seven-row modal Apply/Cancel/return. Neither original EXE nor Windows GUI was run.

Reproduce by disassembling `0x50D443..0x50D4D0`, `0x4F7020..0x4F7042`, `0x40F760..0x40F8B3`; raw read `.rdata` at `0x7C9C94..0x7C9CC4`. Verify the authenticated original `Static.dat` 193 records at `0x2726`, each 53 bytes; next u32 at `0x4F1F` is 1053. No original bytes copied into Git.

**Next action:** inspect the existing runtime competition initialization and original `0x4F7380` to establish actual active club-country competition candidate membership from existing `FM2001Database.competitions`, then source-reconcile `0x4CB2B0` conditional counts and RNG. Do not add extra direct shared RNG calls until exact startup ordering and actual selections are proven. Continue actual seven-row PSupportStart modal/TeamSelect source interaction; Gate13–17 remain OPEN.


## Recovery556: root-competition qualification and native comparator mapped onto existing parser fields

Direct source evidence proves which original competitions enter each country vector during **initial** `0x4F7380` construction. `0x4F70E0` maps serialized competition parent reference (expanded record+0x08) into an instantiated source parent pointer, using NULL when original `-1`. The shared constructor `0x4F3BE0` writes **that actual parent pointer to runtime object+0x04** (`0x4F3BFF`) and stores **negative** source signed WORD+0x16 as runtime object+0x18 (`0x4F3C20..0x4F3C26`). Native `0x4F7380` at `0x4F746E` and `0x4F7512` includes **only object+0x04==0**: those are **root competitions**, not a generic dynamic “active flag.”

The country index producer `0x4F8FF0` follows runtime object+0x20 to the 0x40-byte original competition definition and reads definition+0x24, which derives from **Static.dat record+27** and is already represented by `CompetitionDefinition.country_region_id`. On root objects, the native +0x48 list contains **kind1 leagues (including special ID27) and kind3 dummy leagues**, excluding kind2 cups. The native comparator `0x4F79D0` places tag1 before tag3, then compares runtime object+0x18 descending, which is equivalent to **`CompetitionDefinition.initialization_order_value` ascending**. Native tie comparator returns 0; original `qsort` tie order is not source-proven. Any code that needs one exact pointer index into tied candidates must fail closed until ordering is verified.

With the authenticated ORIGINAL `Static.dat` 193 entries (not synthetic data):
- **178** root entries: 23 league, 25 cup, 130 dummy league.
- **153** root league/dummy-league entries are eligible for source country+0x48 candidate vector.
- These 153 entries span **108** distinct country/region indexes; largest group contains 15.
- There are **12** country/kind/initialization-order tie groups where pointer order is unqualified (e.g., country33 league order9 has IDs24,83; country116 dummy order0 has 15 IDs).
- These counts describe the original **fresh sorted input definition stage** and are NOT assertions that all 153 options are relevant to one selected club, original match schedule, all modes or that a particular live staff assignment has been reproduced.

Already parsed `FM2001Database.competitions` has source ID, parent, kind, country and signed initialization order: reuse it. A bounded, source-defined grouping helper can reproduce membership and **strictly ordered non-tied** groups without changing shared RNG or inventing ties. Future actual CSupportStaff +0x5C must still account for dynamic competition membership, user-selected country, original input and calendar state and shared-CRT ownership.

Reproduce: `objdump` native `0x4F70E0..0x4F722C`, `0x4F3BE0..0x4F3C3F`, `0x4F7380..0x4F75AA`, `0x4F79D0..0x4F7A28`, `0x4F8FF0..0x4F900F`. Source original `Static.dat` length 86929, SHA e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8. No original process was executed; no original binary or dataset was committed.


## Recovery556 grouped source component, explicit integration/test boundary

Staged `reconstruction/original_supportstart_country_competitions.py` and `test_original_supportstart_country_competitions.py` on this EXISTING unopened feature branch. This pure grouping projection takes already-decoded `CompetitionDefinition` objects from the original `FM2001Database` parser, source-validates their 0..192 IDs/country indices/kinds/parent references, returns initial country root membership and root league/dummy membership, and exposes a **source-strict index order only if the original comparator has no tied keys**; any tied group raises `OriginalCompetitionNativeTieError` before being used as an exact sorted source pointer array. It consumes ZERO RNG, does not fabricate full staff, and never mutates GameState or the GUI. Dedicated synthetic original-shaped regression cases cover root/child/cup distinction, special league ID27, kind/source-order sort, 0.0-tie refusal, and fail-closed invalid records.

Independent local processing of the authenticated raw original `Static.dat` reverified 178 root/153 eligible/108 country groups; **this is a private-source corpus cross-check, not an execution of the newly authored GitHub Python tests.** Because a fully runnable current repository checkout was not available in the working shell and a GitHub-only code file cannot substitute for test execution, focused test suite, full suite, asset checks and actual player-visible integration are presently **UNVERIFIED**. No PR or CI was opened merely to prove a source helper; review and run tests at a coherent upcoming milestone. Do not merge on an unexecuted test claim.

Next: qualify original `country+0x50` and live copied competition-vector state at `0x4CB2B0`, reconcile conditional draws against the shared CRT, and connect staff names and seven selector rows to source modal/TeamSelect Apply/Cancel. Also trace source owner+0x24 callback and physical row actions. Gates13–17 and original/Windows GUI acceptance remain open.


## Recovery556 exact dynamic country+0x50 RNG-bound boundary

A further authenticated-original x86 cross-check of the full CSupportStaff virtual+0x5C function `0x4CB2B0..0x4CB5B7` isolates a critical outstanding **dynamic runtime value** rather than inventing one from the decoded Static.dat:

- `0x4CB348` reads original country record `[esi+0x50]` into the method's local DWORD `[esp+0x7C]`. `0x4CB3A7` loads that local and `0x4CB3B9` stores it as a separate stack counter `[esp+0x14]`.
- `0x4CB42E/0x4CB433` uses this **country+0x50** counter directly as the bound to `0x64D540`. `0x4CB493` independently indexes the separately copied original country **+0x48 pointer array**. The two source values are not proved interchangeable. If current runtime count or context differs, the candidate pointer and downstream RNG state differ.
- Original country constructor `0x410BD0..0x410BFB` zeroes array pointers/counts `+0x38..+0x4C`, but does **not** write `+0x50`. Original static-country parser `0x411740..0x4117D0` copies source fields through `+0x34` and sets byte +0x54=1, but does **not** write `+0x50`; and original competition root builder `0x4F7380..0x4F75AE` explicitly populates +0x40/+0x44 and +0x48/+0x4C arrays with no direct +0x50 assignment. These three bounded negative results do **not** prove +0x50 is never written by a *different* game phase. **Do not initialize it from +0x4C or a constant.**
- The source-selected candidate virtual +0x24 tag1 veto at `0x4CB4C3` is independent of the (possibly different) next child chosen through candidate+0x34 and candidate+0x3C; the actual chosen competition class and selected country's dynamic +0x50 provenance remain necessary for full RNG accounting.
- Prelude `0x64CCD0` called at `0x4CB2E1` performs date/ordinal arithmetic using `0x66A518` (not an obvious direct call to `0x64D540`), but the separate helpers, country-state mutation and shared process seed must be reconciled before claiming globally no indirect random draws.

**Next targeted source step:** inspect every native writer or initializer of **DBRCountry+0x50** during the canonical new-user startup and the accepted root-competition subgroup; identify when the selected user's country+0x50 receives a valid bound, including country-vector lifecycle after `0x4F7380`. Then determine MSVC CRT initial checkpoint and dynamic chosen object states. A new port feature should consume source-proven inputs from the existing `FM2001Database.competitions` and fail closed for unqualified dynamic state. No live RNG or GUI changes made.
