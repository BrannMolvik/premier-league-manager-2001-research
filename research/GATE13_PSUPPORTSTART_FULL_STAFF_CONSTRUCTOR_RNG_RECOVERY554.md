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
