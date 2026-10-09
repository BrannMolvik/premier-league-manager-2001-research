# Recovery 448 — native ClubRef four-kind conflict check in NEXT/MATCH postponement

_9 October 2026 KST. Independent source audit only under the binding research/CURRENT_STATE.md P0 functional-navigation priority. Codex is the only authorized game implementation worker; this research report does not change code, assets, saved game data, gate state, or Windows runtime._

## Source, live branch, and repro scope

At recovery start: main `12ad98ab37c319e8e29d42967313c21925848545`; latest Codex `codex/gate13-windows-playability-recovery` **`0188c82a988baa898bf657c372dbb4367ee2659a`** (advanced from previously observed `8702eded049643220bf4b590d8d45c2197cfd42a` by one commit specifically about native formation button/bar frame owners). The current Codex commit is **not** a verified NEXT, EAMail or Squad click-path integration. All audit work remains independent.

The authorized original `footballmanager.exe` at `/mnt/data/fm2001_private/footballmanager.exe` is **4,714,541 bytes**, SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** rechecked in this recovery. Source trace is from the canonical hash-gated PE, not clean-room names, visual inferences, or executing original Windows software.

Reproduce the relevant native disassembly with:
```text
objdump -d -M intel --start-address=0x4F2B60 --stop-address=0x4F2CB0 footballmanager.exe
objdump -d -M intel --start-address=0x510B20 --stop-address=0x510B51 footballmanager.exe
objdump -d -M intel --start-address=0x510C10 --stop-address=0x510C7F footballmanager.exe
objdump -d -M intel --start-address=0x4F3B50 --stop-address=0x4F3B64 footballmanager.exe
objdump -d -M intel --start-address=0x615D60 --stop-address=0x615DA0 footballmanager.exe
objdump -d -M intel --start-address=0x514520 --stop-address=0x514564 footballmanager.exe
```
Do not commit original binary/disassembly.

## Source-owner correction and second verified step: Match embeds concrete `Side`, not plain `ClubRef`

**Independently verified later in Recovery448; do not lose this correction when implementing the four-kind branch table.** Original MSVC RTTI distinguishes **`Side` final vtable `0x7C4D50`**, COL `0x7E54F8`, TypeDescriptor `0x81D740` (`.?AVSide@@`), from **`ClubRef` vtable `0x7C4D60`**, COL `0x7E5578`, TypeDescriptor `0x81D758` (`.?AVClubRef@@`).

Original `Match::0x5103D0` constructs the two participant objects in place at **`Match+0x14`** and **`Match+0x28`**, installing **`Side` vtable `0x7C4D50`** in each at source instructions `0x510446` and `0x5104B1`. It also initializes the match payload status field **`Match+0x44 = 0`** at `0x5104CF`. Separate `ClubRef::0x4F2CB0` creates a generic reference with `0x7C4D60` vtable. This does **not** mean every Side embedded in Match is a plain ClubRef vtable instance.

The `0x4F2B60` kind-dispatch routine is invoked by `LeagueMatch/CupMatch::0x510B20` on these **concrete Side participants**. Its first call to the participant's **virtual `+0x00`** therefore dispatches as **`Side::0x510320`**, not the base generic `ClubRef::0x4F28A0`. `Side::0x510320` first inspects Side `+0x04` cached resolved pointer and may invoke `0x4F28A0`, `0x513FE0`, `0x615F40` and `0x511350` while resolving the participant (with conditional data update at `0x510373`). **Only if that virtual returns zero** does `0x4F2B60` enter the four source kind branches. Thus conflict eligibility can depend on the source Side resolution lifecycle, not merely stored type/club IDs.

For precision, references in this report to “`ClubRef::0x4F2B60`” mean **a kind-dependent ClubRef-layout predicate called on Side-compatible references**; no standalone proof establishes that `0x4F2B60` is a virtual ClubRef member function. Its four byte-proven cases and lookup behaviors remain correct, but the concrete owner argument in ordinary LeagueMatch/CupMatch is **Side**, and the initial virtual source resolve method changes accordingly.

**Status: EXACT** RTTI, two concrete embedded Side vtables, Match payload flags zero at construction, initial dynamic virtual binding and source predicate branch. **UNKNOWN:** whether future match flags +0x44 bits0/5/6 are set by particular game conditions, precise runtime Side mutation outcomes, and physical Windows input/return.

## A. Original ClubRef-compatible layout and concrete Side call chain

RTTI: original **`ClubRef` vtable `0x7C4D60`**, COL **`0x7E5578`**, TypeDescriptor **`0x81D758`** identifying `.?AVClubRef@@`. This is the class constructed by native **`0x4F2CB0`**.

Original concrete `LeagueMatch` (`0x7C4C24`) and `CupMatch` (`0x7C9D9C`) have virtual **`+0x64 -> 0x510B20`**. It invokes **`0x4F2B60`** once for **`Match+0x14`** and, if false, again for **`Match+0x28`**, passing the candidate Event's original relative slot `Event+0x10`. If either returns true, `0x510B20` returns true to the original mutable header query **`0x615DA0`**, which conditionally invokes **`0x510BA0`** and can construct a `PostponedEvent` wrapper at a source relative slot `+7`. These are source-specific conflict/postponement predicates, not ordinary participant equality or an every-match 'advance one day' instruction.

## B. EXACT native Side/ClubRef-layout reference-kind dispatch — four distinct cases

`0x4F2B60` first calls the object's virtual **`+0x00`**. If it returns non-null, it immediately returns false for this conflict predicate. Only when that resolution returns null does it dispatch on **16-bit `ClubRef+0x0C` kind**. The four native jump-table entries at **`0x4F2C9C`** are:

| `ClubRef+0x0C` kind | Original branch / jump-table target | Source condition and traversal — do not invent soccer labels |
| ---: | --- | --- |
| **1** | `0x4F2B87` | Follows source reference `ClubRef+0x08` through `0x510C10` (repeated `+0x08` links) and compares the resulting object **`+0x10`** against the requested relative slot. It returns true immediately if stored slot >= requested. If not, it follows a separate attached reference at `source+0x4C`, checks its virtual `+0x18`, and conditionally examines `source+0x54` via `0x510C10` before a second >= comparison. Some unresolved/missing chains return false. |
| **2** | `0x4F2BE1` | Takes `ClubRef+0x08` source object, selects a calendar collection via **`0x4F3B50`**, and searches it using **`0x615D60`** with source relative slot and specific original search flag. Any returned qualifying event makes the conflict predicate true. |
| **3** | `0x4F2C0C` | Walks a **linked chain from `ClubRef+0x08` using successor `+0x10`**; for each non-null source object, selects its calendar with `0x4F3B50` and queries `0x615D60`. First qualifying result returns true, otherwise false after chain exhaustion. |
| **4** | `0x4F2C3C` | Scans calendar day buckets **from requested relative slot** to source `collection+0x04` count; walks each Event link `+0x04`; resolves event virtual `+0x18` to payload; requires payload **`+0x4C` to match `ClubRef+0x08`** and payload flag **`+0x44 bit0x20` clear**, then returns true if payload **16-bit `+0x20` is not 4**. It continues on unmatched/flagged/code4 records. |

The jump table was independently decoded from the original PE bytes, rather than inferred from case ordering:
```text
table 0x4F2C9C: [0x4F2B87, 0x4F2BE1, 0x4F2C0C, 0x4F2C3C]
```

**Crucial branch distinction:** The original postponement conflict operation is not the same as reference equality `0x4F2830` used by original manager/event selection. For a fully resolvable `ClubRef` the conflict method returns false at its opening gate, while unresolved type 1..4 references may require deeper calendar/chain searches. No higher-level labels for the type IDs or payload `+0x20` code4 are asserted without a producer trace.

## C. Nested lookup and deferred source mutations

- `0x4F3B50` selects source calendar **`0x947AF0`** if source object's virtual `+0x30` returns a truthy byte and **`0x947AD8`** otherwise; this selection is *source-object-dependent*, not equivalent to blindly choosing only based on `ClubRef+0x0C` case.
- `0x615D60` iterates buckets starting from the supplied **relative** slot and calls common **`0x615C50`** with its own literal search arguments. It is **not identical** to ordinary `0x615D10` used for the current manager's next match. Some filters differ: `0x615D60` passes a null manager/participant filter and a specified source payload constraint, whereas `0x615D10` passes a real manager selector.
- `0x615C50` conditionally invokes **`0x514520(Event)`** before returning a candidate. That helper requires `Event+0x08==0`, a non-null payload and clear payload `+0x44` bits `0x20/0x40`. It invokes the native **virtual `+0x00`** on reference objects at payload `+0x14` and (conditionally) `+0x28`. `0x615C50` then checks the Event's linkage again. Thus scheduling selection is state-aware; this audit does **not** claim which concrete mutated fields or game-visible outcomes result from every virtual call.
- The original dynamic `0x510BA0` creates a postponed wrapper only when its own guards are met. The conflict predicate returning true is **not enough** to claim that a new playable postponement will always happen.

## D. Fidelity comparison and implementation handoff

Current Codex source `reconstruction/competition_schedule.py::club_refs_conflict` is a **specific equality/source-identity contract used during startup placement**; `reconstruction/primary_schedule_shadow.py` conservatively tracks potential participants for reference kinds1..4. Both are useful and source-backed within their stated bounded scope. **Neither is an implementation of this different `ClubRef::0x4F2B60` calendar/chain conflict predicate** required by the mutable original NEXT header flow. Do not conflate them or regress the existing startup scheduler.

Main and current Codex do not yet make the source bitmap NEXT button into a normal accepted management gameplay action, nor provide the original full native EAMail and Squad 4/5 click workflow. These remain genuine **P0 original-playability blockers**.

**Codex-only prioritized handoff:** model the original four-kind conflict predicate as a distinct operation from original ClubRef structural equality, preserve the initial resolvable-reference rejection, calendar family selection, original linked-head order, kind1 prior-event chains, kind2/3 calendar lookup with their literal flags, kind4 payload `+0x4C`/`+0x44`/`+0x20` guards. Invoke deferred event updates only through source-qualified lifecycle events (PMenu/header sync and simulation), not every redraw or hover. Exercise multiple real managers/clubs including symbolic CupClubRef states; verify normal Tk input NEXT and Windows 11 interactions before closing Gate13. Still UNKNOWN: exact football meaning of each branch and whether per-club original data makes it execute.

No implementation edit, Windows-runtime execution, CI or gate completion. **Gate13 open; Gates14–17 and full shipped-scope Windows 11 release incomplete.**
