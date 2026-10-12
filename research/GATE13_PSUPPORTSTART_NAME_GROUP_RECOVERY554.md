# Recovery554: correct original SupportStart nationality name pool owner

The original shipped `footballmanager.exe`, SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`,
was statically traced again to reconcile a **material owner mistake**
in unfinished Recovery553 research.

## Correct source sequence

- `0x50D630` loads the original `Master.dat` 1246-club
  expanded owner `0x874B90`, 30064-*player* expanded owner
  `0x875640`, and separate 1612 managers.
- `0x50D6B6→0x4F6EB0` calls **two different
  group-building routines**, NOT a single club-name builder:
  - `0x411440` iterates 1246 clubs, grouping each
    expanded club by nationality field `club+0x14`
    into **country records `0x874BE0+0x38/+0x3C`**
    (country vector stride0x6C). This is **NOT**
    the name candidate table read by `0x421BA0`.
  - `0x4F6F45` calls **`0x411A10`** on owner
    `0x874BC8`, whose vector `0x874BD0`
    stores 209 **name-group** records at 0x14 stride.
    This clears and rebuilds group `+0x0C`
    pointers and `+0x10` counts by walking
    all **30064 expanded PLAYER** records from
    `0x875640` at stride0x250.
- The native filtering inside `0x411A10` directly peeks
  original player first/surname raw Core.str bytes:
  firstNamePtr[1] != '.', surnamePtr[0] != 'N',
  surnamePtr[1] != 'o', surnamePtr[2] != '.'.
  Rejections skip group membership; the nationality
  grouping key is **player native+0x12** (original
  serialized Master.dat player+8 u8), not club ID.
  The same pass builds counts, allocates source
  pointers and fills them in original player order.
- `0x421C00` uses original `Static.dat` country
  row+0x0C group mapping (209 country records,
  59 non-identity, sentinel country199 maps group26).
  It asks `0x421BA0` for **two separately selected
  player pointers**, reading selected first+0x08
  and independently selected surname+0x0C.
- `0x421BA0`: if **filtered group player count >10**,
  selects from `0x874BD0 group+0x0C` array
  (source player pointers). Otherwise falls back
  to the **GLOBAL 30064-player** source pool
  `0x875638` with stride0x250, including
  players excluded by the group filter. **Neither
  branch selects club names or managers.**
- Group construction does NOT consume random numbers.
  The two `0x421BA0` draws and potential first-string
  sentinel retry do consume original shared CRT
  random state; **the source checkpoint is not
  verified** and no exact initial staff names may
  be fabricated.

### Independent real original byte-level verification

Private authorized `Master.dat` (3,391,446 bytes,
SHA-256 `183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8`)
and `Core.str` (351,695 bytes,
SHA-256 `b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06`)
were read directly in the shell. A source-byte faithful
filter (including original string pointer lookahead,
not Python `len()` short-string substitution) found:

| Source property | Confirmed |
|---|---:|
| Source player records | 30,064 |
| Player records accepted for groups | **23,392** |
| Rejected first name second byte '.' | 1,636 |
| Rejected surname first byte 'N' (after earlier filter) | 693 |
| Rejected surname second byte 'o' (after earlier filters) | 4,343 |
| Original 209 groups with >10 eligible players | **93** |
| Original groups with <=10 eligible players | 116 |
| Eligible group 1 count | 208 |
| Eligible group 26 count | 2,548 |
| Eligible group 0 count | 1 |
| Groups 199,208 eligible count | 0 each |

**These results directly contradict Recovery553's**
club-count threshold (36 groups with >10 clubs)
and `original_supportstart_club_name_source.py`.
That bogus source branch and its tests must be
deleted from the unfinished feature branch; the
private disassembly was decisive. Its staged
`source_original_name_group_route` is replaced
with correct filtered-player groups.

### Implementation scope

`reconstruction/original_supportstart_name_group_source.py`
now parses source country indirection, authentic Master
player records and Core.str raw bytes, constructs
name-group player index tuples exactly as source
`0x411A10`, then chooses the correct filtered
or global player **candidate pool**, without invoking
random and without requiring a club-count hypothesis.
The feature tests use explicit small source-shaped
fixtures and check both branches and failures;
private real-source 23,392/93 counters were verified
independently, NOT CI-run from this GitHub branch.
Original executable and source datasets stay private.

### Original disassembly reproducibility

```bash
objdump -D -Mintel --start-address=0x4f6eb0 --stop-address=0x4f6f4f footballmanager.exe
objdump -D -Mintel --start-address=0x411440 --stop-address=0x411558 footballmanager.exe
objdump -D -Mintel --start-address=0x411a10 --stop-address=0x411b61 footballmanager.exe
objdump -D -Mintel --start-address=0x421ba0 --stop-address=0x421c49 footballmanager.exe
objdump -D -Mintel --start-address=0x418bf0 --stop-address=0x418c0b footballmanager.exe
```

**Still outstanding:** source shared CRT TLS seed at original six
staff births, source GUI hit-owner callbacks, real selected
staff names and GUI lifecycle, end-to-end Apply/Cancel/
TeamSelect return and Windows11 acceptance; Gates13–17 OPEN.
