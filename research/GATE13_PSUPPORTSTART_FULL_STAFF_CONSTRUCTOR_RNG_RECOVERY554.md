> **CORRECTION 12 October 2026, Recovery555:** The original CSupportStaff virtual+0x5C is **0x4CB2B0**, NOT 0x4CB0F0. The latter is virtual+0x58. Previous statements below using the +0x58 club scan and its 4–10 RNG draw estimate as if the fixed fresh-staff constructor invoked them are **SUPERSEDED**. Do not use the previously reported 12–18 draws-per-staff lower bound. See detailed corrective source audit appended below. No production RNG was changed.

# Recovery554: original fixed SupportStaff constructor consumes additional shared CRT draws

The original `footballmanager.exe` (SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`)
was statically inspected to check the missing six original staff names
in the context of the existing already-shipped reconstruction's
`support_staff.generate_fixed_initial_staff` behavior.
**No original game process or Windows11 GUI was launched.**

## Correct original SIX fixed staff constructor chain

- `0x4D1760` calls `0x4C9D40` six times with
  native types `1,2,3,4,5,13` in that exact order.
  This is the fixed *fresh user* initialization.
  A separate `0x4C9CCF` path also calls
  `0x4C9B30` six times, but **that is a distinct
  original path** and must not be conflated
  with fresh-user initialization.
- For EACH `0x4C9D40` type:
  1. `0x4C9D5A–0x4C9D70`: **RNG(25)**
     plus 25, source staff age-like field.
  2. `0x4C9DA9–0x4C9DF6`:
     **RNG(2)** plus native
     `0x4FA520` competition context tier.
     This is the small rating-like field already
     represented by `generate_fixed_initial_staff`.
  3. `0x4C9E1D→0x4CA2F0` constructs
     a full native CSupportStaff object.
     Constructor `0x4CA321–0x4CA334`
     obtains current user/club country identity
     from the source DBRUser+0x5B4 club and
     calls `0x4CA660`. That calls
     `0x421C00`, performing **two separate
     original name-selection RNG draws**
     via `0x421BA0`, with possible **extra
     first-name retry** when original source
     first text equals `"-"`. Choice
     pool is the existing native nationality
     filtered player group when count>10,
     otherwise the global player pool.
  4. `0x4C9E55` calls CSupportStaff
     virtual+0x28 `0x4CA790`,
     whose tail at `0x4CADB0` invokes
     **RNG(20)** while computing a
     distinct native staff+0x08 value.
  5. `0x4C9E5C` calls CSupportStaff
     virtual+0x30 `0x4CA640`, which
     invokes **RNG(30)** and writes
     staff+0x14 = 1..30.
  6. `0x4C9E63` calls native
     virtual+0x5C `0x4CB0F0`,
     which traverses actual original clubs.
     Any extra RNG calls/side effects
     on this last path are NOT YET qualified.

This chain proves an **additional four or
more native draws** after the two
age/rating draws when the source staff
is fully constructed (two name draws,
RNG20 and RNG30, with potential retries
or extra calls in native vft+0x5C).

## Important distinction from the current reconstruction

The already-merged `reconstruction/support_staff.py`
`generate_fixed_initial_staff()` intentionally
represents only **RNG25 + RNG2**
and returns `SupportStaffState(staff_type,
age_like,rating,status)` without original
name, RNG20-derived native field,
RNG30-derived native field or
native virtual+0x5C side effects.
Its unit tests can pass, while an actual
fresh original staff launch will still
diverge in subsequent shared CRT draws
if that minimal helper is used as if it
fully consumed original constructor RNG.
Do **not** silently patch the production
RNG stream by adding arbitrary additional
draws or claim six names are reproduced
without reconciling original process seed,
the true ordered +0x5C effects and the
selected user's actual club-country.

The existing `startup_rng.py`
already implements `generated_name_source_ids`,
`generated_name_rng_bound` and
`select_report_setup_player_ids` for
the correct player-owned `0x421BA0`
name path. It should be reused with ONE
correct shared CRT RNG owner in the
future full SupportStart transaction,
not cloned as an independent per-editor
random stream. Independently checking
all source real 30064 Master.dat/Core.str
player eligibility values produced
**zero** differences versus its current
decoded-string algorithm, and source-correct
filtered name group count=23,392.
The new SupportStart feature tests now
cross-check the pre-existing owner.

## Exact private reproduction

```bash
objdump -D -Mintel --start-address=0x4d1760 --stop-address=0x4d17e5 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9d40 --stop-address=0x4c9e7f footballmanager.exe
objdump -D -Mintel --start-address=0x4ca2f0 --stop-address=0x4ca340 footballmanager.exe
objdump -D -Mintel --start-address=0x4ca660 --stop-address=0x4ca6d0 footballmanager.exe
objdump -D -Mintel --start-address=0x4ca790 --stop-address=0x4cadd5 footballmanager.exe
objdump -D -Mintel --start-address=0x4ca640 --stop-address=0x4ca652 footballmanager.exe
objdump -D -Mintel --start-address=0x4cb0f0 --stop-address=0x4cb300 footballmanager.exe
```

**Next:** fully trace `0x4CB0F0` and
the source DBRUser/club country input,
then add a transactionally safe
source-owned six-staff full constructor
that reuses existing `startup_rng`
group and shared CRT state. Connect
it to actual player-visible original
PSupportStart seven-row names, ownership
and Apply/Cancel/TeamSelect return;
do not simulate unproven native actions.
All Gates13–17/real Windows11 GUI
acceptance remain OPEN.


## Further source closure: 0x4CB0F0's native per-staff RNG branch

Exact original `0x4CB0F0` was inspected through
`0x4CB2AD` rather than treating virtual+0x5C
as an opaque post-creation helper:

1. Scans native original `0x874B90`
   CLUBS at 0x2A8 stride, comparing
   expanded club+0x10 to the passed
   source group/competition parameter.
   Retains **at most 24** matching
   source club pointers on its stack.
   This data family is unrelated to
   `0x421BA0` name selection, whose
   native nationality group is populated
   from PLAYERS.
2. Always invokes `0x64D540(3)` at
   `0x4CB16D` and adds 1, yielding
   native count **1–3**.
3. For each selected item (1–3):
   - `0x4CB1A1` invokes
     `0x64D540(matching_club_count)`
     to choose one eligible club from
     the bounded original pointer array.
   - `0x4CB1CE` invokes
     `0x64D540(3)`.
   - `0x4CB1D7` invokes
     **another `0x64D540(3)`**.
   - It uses those source results to
     populate/schedule several source
     staff record strings/values, before
     incrementing the slot+0x30 cursor.
4. For selection counts <=2, it
   populates extra default strings
   from static source literal `0x874BA0`
   **without an extra direct RNG call**
   within `0x4CB256..0x4CB2A1`.

This establishes at least **one RNG(3) plus
three RNG calls per each of 1–3 items**
inside virtual+0x5C alone, i.e.
**4–10 additional bounded CRT draws**
per normal full native staff constructor,
independent of the preexisting
RNG25, RNG2, two native staff-name
choices, RNG20, RNG30 and possible
first-name retry. The exact
`matching_club_count` argument and
Native pointer-array ownership must
be qualified at the selected user
source context, and the called
`0x64CCD0` preamble and text
formatter `0x66876F` need
cross-call audits before claiming
there are no further hidden draws.

**No synthetic RNG calls were added to
production**: the source currently stores
only a minimal age/rating staff projection.
A six-staff sequence with this many omitted
draws must never be used as proof of an
original-equivalent shared CRT checkpoint
or to unblock draft PR638's Inbox click.

Reproduce from authorized original:
```bash
objdump -D -Mintel --start-address=0x4cb0f0 --stop-address=0x4cb2b0 footballmanager.exe
```

## Correction: double native staff name-generator invocation in fixed staff setup

**Critical independent vtable cross-check** (after the preceding report):
actual CSupportStaff vft base `0x7C6834` at **`+0x10`** is
**`0x4CA660`**, the *same original staff name-generator* used in the
`0x4CA2F0` constructor. Native `0x4C9E3C..0x4C9E4C` retrieves
current user's club `+0x14` source country, pushes it, and invokes
**vft+0x10 = `0x4CA660` AGAIN**. This source call occurs **after**
`0x4CA2F0` has already invoked `0x4CA660` at `0x4CA334`.
The second call therefore regenerates/overwrites the first name+surname
created during construction. It is **not** a no-op country setter.

Every successfully constructed fixed staff therefore has **two calls
to `0x421C00`** prior to its vft+0x28/+0x30/+0x5C calls:
minimum **FOUR original RNG name selections per staff**, not two,
plus independent retry *pairs* when first-name source string is exactly
`"-"`. Native `0x4CA660` loops back to `0x4CA66B` on the sentinel,
re-executing **BOTH** `0x421BA0` picks (two RNG calls) on each retry.
Previously staged remarks that a retry consumes only an extra first-name
draw were incorrect for **SupportStaff** (other report-setup name routes
can follow different loops).

This changes the source-confirmed **minimum per-staff** RNG direct call
lower bound to:

- RNG(25), RNG(2): 2
- constructor name pair + explicit vft+0x10 name pair: **4**
- vft+0x28 RNG(20), vft+0x30 RNG(30): 2
- vft+0x5C source RNG(3) item count + 3 draws for each of 1..3 entries:
  **4–10** more
- **TOTAL minimum source-direct calls: 12–18 per staff** depending on item
  count, *before* first-name retry loops and any additional indirect calls.

The earlier “four or more after age/rating” and “two selected names per
staff” descriptions in this report are superseded by this corrected trace.
This still does **not** prove a particular shared-CRT fresh-game seed,
exact output staff name, or that vft+0x5C cannot make additional indirect
random draws. In particular, the actual vft+0x5C argument propagation
must be studied across the CSupportStaff caller frame before reproducing
the eligible club set. **Do not implement additional live RNG draws from
the 12–18 lower bound alone.**

Reproduce:
```bash
objdump -s -j .rdata --start-address=0x7c6834 --stop-address=0x7c6895 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9e2a --stop-address=0x4c9e6a footballmanager.exe
objdump -D -Mintel --start-address=0x4ca2f0 --stop-address=0x4ca33f footballmanager.exe
objdump -D -Mintel --start-address=0x4ca660 --stop-address=0x4ca6d0 footballmanager.exe
```


## Recovery555: corrective source audit of real fixed-staff constructor vtable

The private original 4,714,541-byte footballmanager.exe was independently downloaded and SHA-256 verified as 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. This was a static PE read, not original process execution.

The actual CSupportStaff vtable at 0x7C6834 was cross-checked with a PE VA-to-raw-offset little-endian DWORD reader:

| Slot | Actual callee |
| --- | --- |
| +0x10 | 0x4CA660, name generator |
| +0x28 | 0x4CA790, RNG(20) type-dependent state |
| +0x30 | 0x4CA640, RNG(30) |
| **+0x58** | **0x4CB0F0, a DIFFERENT method** |
| **+0x5C** | **0x4CB2B0, the actual postconstructor method** |

The actual fixed-staff factory 0x4C9E4C calls +0x10, 0x4C9E55 calls +0x28 with a pushed -1, 0x4C9E5C calls +0x30 without an argument, and **0x4C9E63 calls +0x5C without an argument**. The calling conventions independently confirm the slot correction: 0x4CA790 ends with ret 4, 0x4CA640 with ret, **0x4CB2B0 with ret**; the incorrectly attributed 0x4CB0F0 ends with ret 4.

### Actual +0x5C method at 0x4CB2B0

1. Reads the currently selected user club nationality via DBRUser+0x5B4 -> club+0x14, selects original 0x6C-byte country record at 0x874BE0, calls 0x4CB5D0 on this record and 0x4D1830 on three data fields at +0x38/+0x40/+0x48. The latter helpers and list cardinalities remain to be qualified, not invented.
2. Calls original shared bounded RNG(3) at 0x4CB3A0, adds one, and initializes 1–3 source attempts.
3. In the conditional live-candidate path at 0x4CB42E, calls bounded RNG(group count) at 0x4CB433, followed by RNG(selected candidate quantity) at 0x4CB4A5. Selected object virtual+0x24 is a veto at 0x4CB4C3. Rejection loops before the accepted candidate text/extra RNG path; actual group identity, count and callback veto semantics are not yet proven.
4. After an accepted candidate, resolves original club text through 0x4F4940/0x40DA70 and calls bounded RNG(3) **twice** at 0x4CB507 and 0x4CB510; writes source staff text via 0x66876F. The separate default-fill route at 0x4CB3CE copies native literal 0x874BA0 without those two accepted-route calls. A fixed 4–10 RNG cost cannot be asserted.
5. Returns at 0x4CB5B7 with plain ret. The formerly analyzed 0x4CB0F0 function scans a different club collection, limits a local array to 24 pointers and has its own RNG pattern. Those facts are valid for **vft+0x58 only**, not the fresh-staff factory.

**Corrected scope:** RNG25, RNG2, TWO full native name-generator calls (each two source-player selections with both draws repeated for any first-name '-' retry), RNG20 and RNG30 are direct, source-verified constructor calls. Actual +0x5C additionally always calls RNG3 and has conditional country-group/candidate draws with possible repeats. The total and seed checkpoint remain UNKNOWN until 0x4CB5D0, 0x4D1830, 0x4F4940, selected-record virtual+0x24 and the relevant live source group populations are traced. Do not add arbitrary RNG calls to the live shared CRT; do not claim reconstructed initial staff names or unblock Inbox PR638 from this partial trace.

Reproduce on the hashed original with objdump disassembly around 0x4C9E37–0x4C9E66, 0x4CB0F0–0x4CB2B0, 0x4CB2B0–0x4CB5B8, and vtable raw data 0x7C6834–0x7C6898. No original GUI playtest or Windows11 release acceptance has been performed. Gate13–17 remain open.
