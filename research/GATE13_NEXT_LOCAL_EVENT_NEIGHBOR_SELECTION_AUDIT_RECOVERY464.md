# Recovery 464 — original Side conflict checks only the selected calendar slot and its immediate neighbors

_10 October 2026 KST. Continuing exactly the Recovery463 source audit. Independent **AUDIT ONLY**; Codex alone owns reconstruction/game-code changes, CI, merge, Windows11 release and Gate13–17 acceptance._

## Live provenance and falsifiable reproduction

- Live repository before audit: `main` **`b1f98544fb5043ef379c55fbafcfc1c092892585`**, `codex/gate13-windows-playability-recovery` **`0ae745d1b56f45cade460f03cd893849a2f53b45`**. Read `research/CURRENT_STATE.md` and `agent-runtime` gen463: `worker_role=audit_only`, `implementation_allowed=false`. No Codex implementation commit since 9 October's font ownership work.
- Independently verified authorized original **`/mnt/data/fm2001_private/footballmanager.exe`**, size **4,714,541**, SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** using `sha256sum`. Original EXE was **never run**, and no original game executable, art, raw disassembly or saves were committed.
- Reproduce original PE with `objdump -d -Mintel --start-address=0x615f40 --stop-address=0x616074 footballmanager.exe`; `0x510320..0x51037E`; `0x513FE0..0x513FF5`; `0x514520..0x514564`. Earlier Recovery463 already source-closed the chain `Event::0x514520→Side::0x510320→0x513FE0→0x615F40→0x510BA0`; this recovery tightens **which neighbors, in which order, and which event gets wrapped**.

## A. EXACT original `0x615F40` localized search and selection order

The original `Side::0x510320`, when cache `Side+0x04` is not already resolved and the generic reference resolves, follows old `Event+0x08` links via `0x513FE0` to their **terminal source Event**. If terminal `Event+0x10 != -1`, it picks that Event's calendar using `0x510300`, then calls `0x615F40` with (calendar owner in ECX, the resolved reference selector, terminal source Event).

Native `0x615F40` takes **`Event+0x10` as a relative calendar *bucket index*** at `0x615F47`, NOT an absolute date or a globally sorted fixture rank. It uses the selected calendar's day-array pointer and size `+0x00/+0x04`:

1. **Same slot first:** at `0x615F51..0x615F5A`, read the calendar array's bucket-head pointer `days[relative_index]`, pass head and reference selector to `0x616020` to find the first source-eligible related Event in the linked chain.
2. **Exclude self when necessary:** at `0x615F66..0x615F79`, when the returned related Event **is the terminal Event itself**, resume `0x616020` from **`Event+0x04`** (next link in the same bucket); when a *different* related Event was already returned, keep it instead. Thus another eligible Event *ahead of self* in a bucket has priority; if self was first, look past it.
3. **Previous bucket second:** if the same-bucket successor search found none and `relative_index>0`, check **`days[relative_index−1]`** with `0x616020` at `0x615F7D..0x615F95`; use its first eligible related Event if present.
4. **Next bucket third:** only when previous is also absent and **`relative_index+1 < calendar+0x04`**, check **`days[relative_index+1]`** at `0x615F97..0x615FB4`.
5. **Nothing found:** `0x616018` exits without a wrapper action. **There is NO unbounded scan across all later fixtures** in this `0x615F40` routine, no absolute-date sort, and no implicit search of the *other* calendar family. (Other original functions may of course inspect other slots or calendars.)

The local helper **`0x616020`** walks source linked Events through **`Event+0x04`** and, per node, invokes Event virtual **`+0x18`** to obtain payload. It rejects payloads with **`+0x44 & 0x20`** set, constructs the reference selector via `0x4F2CB0`, and calls that candidate Event's virtual **`+0x04`** to test matching participants; returns the first qualifying Event, or **null**. This source-local filter is different from the manager-specific `0x615D10→0x615C50` NEXT filter, which has additional payload flag and side-effect/owner gates. Native `0x615F40` assumes its initial self-inclusive search has a valid source result in the intended caller state; do not turn the low-level entry into a generic unsafe scanner accepting arbitrary unrelated Events.

## B. EXACT original conflict/priority resolution — source only wraps one of the two local Events when qualified

Once the selected other Event `ESI` is non-null at `0x615FB6`, original method compares **polymorphic Event virtual `+0x08`** on both the candidate and the original terminal `EDI`:

| Original source branch | Condition | Exact call and target |
| --- | --- | --- |
| `0x615FBA..0x615FD2` | `other.vft+0x08 > original.vft+0x08` | `0x510BA0(original_Event, discriminator=0)` |
| `0x615FDE..0x616003` | `other.vft+0x08 == original.vft+0x08` **and** `other.payload+0x44 & 1 !=0` | `0x510BA0(original_Event, discriminator=0)` |
| `0x61600F..0x616013` | Otherwise (other priority lower, or equal with source payload bit0 clear) | `0x510BA0(other_Event, discriminator=0)` |

The last call happens to the **related Event**, not invariably the original Side's terminal Event; this is why cache effects may affect *a different fixture*. These calls are exactly the **three direct `0x510BA0` instructions already counted in Recovery462**, not newly discovered additional wrapper-producing call sites. The original `0x510BA0` itself guards Event+0x08 clear and payload+0x44 bit0x40 clear, and its requested displacement is relative bucket +7, subject to native insertion conflict handling. **Do not infer a football meaning** (which club is at fault, replay, home/away priority) from raw virtual+0x08 ordering without independently typing that method's return values.

## C. Bounded safety consequences for current Codex implementation

Existing Codex `HumanGameplayController.advance_original_management_turn` (blob `980f9af731ae2aa5ee2ed14694c8b60fb22c37d7`, around line1571) increments the game day, invokes `state.invalidate_primary_schedule_wrapper_links()`, and then calls `_process_current_primary_day(native_primary_order=True)`. Its `primary_schedule_shadow.py` `invalidate_unmodelled_wrapper_links()` downgrades **all** previously CLEAR future entries to UNKNOWN. On a due event it then can throw `RuntimeError('Original NEXT current-day wrapper lifecycle is unresolved')` after mutating date and shadow. This remains a documented P0 transactional/coverage gap (Recovery460), **not** proof the original globally invalidates all events. Quiet days can also erase the displayed future qualified match (Recovery461).

**This recovery narrows one original dependency family further:** the indirect `0x615F40` wrapper producer caused by one uncached `Side` has *selected calendar*, terminal Event, **same-slot head-order, previous-slot and next-slot** candidate dependencies. If the runtime can **prove** all those dependencies inert from source predicates/Side cache and previous side effects, it can preserve CLEAR evidence for unrelated events. If it cannot, mark **those affected candidates** unknown or reject the advance without mutating state. This localized proof must not be generalized to other original wrapper writers at `0x4A801F`, `0x5E3C34`, `0x615C33`, `0x615DD7`, or to arbitrary extra original virtual callbacks.

**Atomicity constraint:** Native NEXT/Side candidate search can itself mutate wrapper links before final candidate return (Recovery463). A clean-room *read-only preview* cannot simply execute the mutating source callbacks on a live state then decide "unknown" after advancing the calendar; it needs an owner-consistent plan/replay model, an explicit state snapshot/rollback, or a source-proven fail-closed preflight **before** changing calendar, RNG, match results or actor selection. This is an implementation acceptance requirement for Codex, not a claim the original software has transactional rollback.

## D. Exact deterministic Codex acceptance tests to add before normal NEXT click integration

1. **Same-day head order:** bucket has original Event and one other eligible same-club Event before/after it. Verify the first eligible source `0x616020` result, self-skip from `Event+0x04`, and which original Event is chosen for `0x510BA0`. Reversing linked-node order must be observably different when source prescribes it.
2. **Neighbor precedence:** no same-bucket eligible other Event, but eligible *both previous and next* bucket. Verify **previous wins**, not earliest arbitrary next-date; then remove previous and verify next selection. At index zero, previous must never be dereferenced; at final index, next must not be accessed.
3. **Payload/reference gates:** skip other payload bit0x20; make reference-mismatch chain, equal/lower/higher vft+0x08 priority with peer payload bit0 clear/set. Verify exact original-vs-peer wrapper choice, and wrapped/link guard bits before any mutation.
4. **Side cached vs uncached:** `Side+0x04` cache short-circuit vs new source resolution `0x510320`, terminal follow-through of `Event+0x08` chain `0x513FE0`, original final link recheck `0x615C50`; a candidate that gains a wrapper while being inspected must not remain the accepted NEXT event.
5. **Transactional fail-closed:** when one source dependency is unsupported, controller refuses with **same** calendar date, RNG state, player/manager state, fixture results and shadow certainties after the refusal; simulate human due day and quiet day. The current Codex implementation *does not yet meet this*.
6. **Real controls:** after qualified backend behavior, actual original UI PBg ID3 NEXT click (rect700,0,100,95), source roster 407FE0/407F40 acceptance/refusal and multi-human manager rotation must work in actual Windows11 game. A direct backend test or screenshot of MATCH caption is insufficient.

**Source support:** instruction-level selected routine and hash-verified original are EXACT; side cache/content predicates and per-event dependency closure are PARTIAL; real fixture occurrences and final original Windows11 input outcomes UNKNOWN. No UI/gameplay code was modified. **Gate13 remains OPEN; Gates14–17 and original-scope verified Windows11 release INCOMPLETE.**
