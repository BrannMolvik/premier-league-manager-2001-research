# Recovery 446 — native Event/Match scheduling classes, original bucket insertion and postponed-event wrapper

_9 October 2026 KST. Continue active Recovery445 original-file fidelity audit, Daniel's P0-D NEXT/MATCH normal game path. Audit-only scope; Codex owns implementation. No proprietary data/assets committed, no original-game process execution, Windows 11 visual receipts, CI, source implementation or gate closure._

## Reproducible canonical source

At the start of this recovery, GitHub main was `ccc5e00bc4918fc45a10da2bd76e4c9e2f3de4b0`, Codex `8702eded049643220bf4b590d8d45c2197cfd42a`; `research/CURRENT_STATE.md` confirms original first-team, inbox, PMenu and genuine NEXT/MATCH functional fidelity remains ahead of cosmetic audits. The authorized original PE `footballmanager.exe` (4,714,541 bytes) was **rehashed** privately:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Private source reproducer: GNU `objdump -d -M intel` on the hash-matched PE with ranges `0x510300..0x5103C4`, `0x5103D0..0x51051A`, `0x510520..0x51055C`, `0x510BA0..0x510C09`, `0x5140B0..0x514110`, `0x615890..0x615AD1`, `0x615C50..0x615E15`, `0x61614E..0x61623A`, `0x4A8435..0x4A84B4`. For MSVC RTTI, inspect the little-endian 32-bit COL pointer at `vtable-4`, TypeDescriptor at `COL+0x0C`, null-terminated decorated type at `TypeDescriptor+8`. The original executable and raw disassembly stay outside Git.

## A. Exact concrete original scheduled classes — new class-identity closure

These are **ORIGINAL EXECUTABLE RTTI NAMES**, not class names invented by clean-room code:

| Original class | Final vtable VA | RTTI TypeDescriptor | Source constructors / dynamically returned payload |
| --- | --- | --- | --- |
| **`Event`** | `0x7C4D70` | `0x81B1F0`, `.?AVEvent@@` | `0x510380` constructs core calendar event, assigning initial relative offset `+0x10=-1` |
| **`Match`** | `0x7C4CE4` | `0x81B3F8`, `.?AVMatch@@` | `0x5103D0` calls `Event::0x510380` then overwrites final vtable `0x7C4CE4` |
| **`LeagueMatch`** | `0x7C4C24` | `0x81B410`, `.?AVLeagueMatch@@` | `0x5104F0` calls `Match::0x5103D0`, then overwrites final vtable `0x7C4C24`; original caller `0x61622B` constructs 0x50-byte instance in source calendar |
| **`CupMatch`** | `0x7C9D9C` | `0x81BA80`, `.?AVCupMatch@@` | `0x510520` calls `Match::0x5103D0` and overwrites final vtable, original factory call `0x6162F5` |
| **`PostponedEvent`** | `0x7C9FE8` | `0x828240`, `.?AVPostponedEvent@@` | `0x510BA0` and `0x6161A0` allocate 0x1C and call base Event `0x510380`, then set final `0x7C9FE8` |

## B. Original calendar entry data fields and allocation sequence

The base `Event::0x510380` receives the address of a selected calendar collection and installs its own vtable. It initializes:

- `Event+0x08 = 0` (original native neutral link/control state);
- `Event+0x10 = -1` (unscheduled relative slot sentinel);
- `Event+0x0C = 2 * old_collection_ordinal + source_calendar_family_bit` at `0x5103A9..0x5103B8`. The family bit is **1 only** if collection pointer equals **`0x947AF0`**, otherwise 0 for `0x947AD8`. It increments that collection's ordinal counter **`collection+0x0C`**.

Thus **`Event+0x0C bit0` is the two-calendar family discriminator**, but upper bits also preserve a collection-local ordinal. It must not be modeled as an independent scalar one-bit field if the rest of the word participates in source ownership/serialization. `0x510300` later reads exactly this bit to choose `0x947AD8` vs `0x947AF0`; this reconciles Recovery445's relative-date mapping with original construction provenance.

The calendar insertion routine `0x615A60`:

1. obtains original current date-like global **`0x9847FC`**, computes **`minimum_relative_slot = current_date - collection+0x08 + 1`**, and chooses max of that value and requested slot;
2. uses `0x615890` conflict searching to displace insertion where needed (the full rule is partly retained by the existing clean `primary_schedule.py`/`primary_schedule_shadow.py`, but not a universal gameplay NEXT shortcut);
3. computes the chosen bucket index into collection's day-array `[collection+0x00]`, writes **`Event+0x10 = chosen_relative_slot`** at `0x615AC3`, links old head into **`Event+0x04`**, then installs this event pointer as the new bucket head at `0x615ACB`.

This closes the Event+0x10 **producer and its exact offset-to-calendar-base relationship**. During PResults the original `0x4A8467..0x4A8471` compares these stored Event-relative offsets across manager users *before* `0x510A20` converts the winning relative offset with its own collection+0x08 base. The event class and calendar assignment are therefore a **real original polymorphic scheduling contract**, not arbitrary fixture dates or generic one-day advance.

## C. Event versus underlying Match payload and postponed wrapper

- `0x615D10` first calculates requested `date - collection+0x08`, iterates native day-bucket heads and calls **`0x615C50`** to select eligible **Event** objects by original source callback/flag conditions. It can return polymorphic `Match/LeagueMatch/CupMatch` event objects, and there is a distinct `PostponedEvent` wrapper path.
- The `Match/LeagueMatch/CupMatch` final vtables' **virtual `+0x18 -> 0x6559A0` returns `this`**, whereas **`PostponedEvent` virtual `+0x18 -> 0x514100`** follows **`PostponedEvent+0x14` wrapped original event** and delegates that event's **virtual `+0x18`**. This is why blindly reading a native Event as an unwrapped match payload is unsafe.
- **`PostponedEvent::0x510BA0`**, only when its original **`Event+0x08` is zero** and its delegated underlying payload **`+0x44 bit0x40` is clear**, constructs a 0x1C-byte wrapper: `0x510BCB` obtains original calendar collection from `0x510300`, `0x510BD5` calls `Event` base constructor, `0x510BDE` attaches prior source Event to wrapper **`+0x14`**, `0x510BE4` installs final `PostponedEvent` vtable, then calls **`0x615A60` with source requested relative slot `old Event+0x10 + 7`**.
- There is also a native `PostponedEvent` construction path at `0x6161A0` with the same `0x510380` base initializer and derived vtable, corroborating that the wrapper is part of calendar/event machinery. **Unknown:** when these paths fire for actual clubs/matches, whether seven units always means seven elapsed real-world days in every calendar family, whether a postponed event is visibly reflected as a fixture postponement, and exact payload record flags. Do not hardcode a universal “one-week postponement” football rule from one relative-slot `+7` source consumer alone.

**Status:** class/vtable/constructor, wrapper delegation, bucket offsets/head insertion and these specific predicates are **EXACT original-source facts**. The scheduling meaning of every payload flag/selection rule, original cross-manager calendar epoch differences, user-visible consequence, lifecycle/save and Win11 input remain **PARTIAL/UNKNOWN**.

## D. Current implementation contrast and Codex handoff

- **Current Codex (head above)** `reconstruction/primary_schedule.py` and `reconstruction/match_schedule.py` already model native schedule bucket placement, conflict checks and linked-list order for original league/cup fixtures. Do NOT call their whole fixture engine missing or regress source-proven startup placement.
- However `reconstruction/primary_schedule_shadow.py::invalidate_unmodelled_wrapper_links` explicitly **downgrades old clear wrapper-link states to UNKNOWN after a reschedule pass**. Its own comment identifies unmodeled native post-start wrapper-link producers. That is consistent with the now-proven `PostponedEvent` source owner; it is **not** evidence that runtime postponed-wrapper reconstruction is complete or original multi-manager NEXT scheduling is available.
- Codex's current normal original-looking management `on_click` still **does not dispatch NEXT input** through original `PBg+0x524` child ID3, gated source `0x5D39C0/0x64F7A0` → original `0x432190` game branches. The game also lacks ordinary native PResults panel, inbox, and 1ST/RES FORM tab clicks. This remains a **P0 functional gap**, even with sophisticated isolated startup scheduling tests.
- **Precise implementation handoff:** preserve `Event` separate from underlying `Match` payload, calendar family/ordinal bitfield `+0x0C`, relative slot sentinel/insertion `+0x10`, linked per-day head order, `PostponedEvent` wrapping/delegation and `+7` guarded rescheduling *only when source predicates are truly modeled*. Validate normal NEXT through at least two user managers/clubs with distinct scheduled candidates, respecting selected-user save/restore before PMenu reentry, and actual Windows 11 click/transition receipts. No simple absolute-date global-sort substitution.

**No implementation, CI, binary release, original Windows runtime run or gate closure. Gate 13 is OPEN; Gates14–17 and original-country Windows 11 release remain incomplete.**
