# Recovery 482 — firsthand original PE: secondary event acceptance and distinct +14/+3 lookahead mutations

_10 October 2026 KST. Strict source-fidelity AUDIT ONLY. No executable was launched: this report uses read-only inspection/disassembly of the authorized shipped PE, and current GitHub code comparison. Codex alone owns gameplay code, tests, GUI and CI. Does not close Gate13._

## Canonical original source independently restored in this recovery

The private authorized `/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip` was already mounted in the working container. Fresh actual SHA256 of its 511,121,336 bytes: **`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`**, matching `research/ORIGINAL_SOURCE_LOCATOR.md`. The ZIP contains `famg2001.bin` 631,627,248 bytes MODE1/2352; its Joliet supplementary descriptor at physical sector17 yields root `footballmanager.exe`, 4,714,541 bytes. Independently extracting its original data sectors gives SHA256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**, exactly the repository's canonical original PE. This reverses the prior temporary `caas.internal.errors.ClientError` source-access blocker; it does **not** supply normal Windows 11 mouse acceptance or permit playing the private game.

Private extracted original `/mnt/data/fm2001_private/footballmanager.exe` remains outside Git. Reproducible read-only commands (with the same verified PE):
```
objdump -d -M intel --start-address=0x4a7ef0 --stop-address=0x4a7f42 footballmanager.exe
objdump -d -M intel --start-address=0x4a7b30 --stop-address=0x4a7c90 footballmanager.exe
objdump -d -M intel --start-address=0x4a7f50 --stop-address=0x4a8062 footballmanager.exe
objdump -d -M intel --start-address=0x4a8260 --stop-address=0x4a827b footballmanager.exe
```

## A. New closed predicate: `0x4A7EF0` traverses a *filtered* secondary Event list

Input at `0x4A7EF1` is an Event-node pointer. The loop follows node `+0x04` and returns either the underlying **payload pointer** or NULL, applying this **ordered acceptance test** per Event:

1. `0x4A7EFA–0x4A7EFF`: if Event `+0x08` pointer is **nonzero (already linked)**, skip the node.
2. `0x4A7F01–0x4A7F05`: if byte Event `+0x0C & 1 == 0`, skip. This is the actual source bit predicate, not a guessed "unplayed" or "injured" label.
3. `0x4A7F07–0x4A7F1A`: invoke Event virtual `+0x18` to obtain payload, then payload virtual **`+0x28`**. If returned integer equals **2**, skip. For any other value, continue evaluating; the semantic enumeration of return values is not established.
4. `0x4A7F1C–0x4A7F2F`: read pointer at payload `+0x4C`, then that pointed object's `+0x04` field. If the latter is **nonzero**, invoke payload virtual **`+0x60`** and **skip if that returns nonzero**. If the pointed object's `+0x04` field is zero or the virtual result is zero, accept. Source execution assumes a well-formed payload+0x4C pointer; null/untyped input is NOT source-qualified.
5. `0x4A7F31–0x4A7F41`: otherwise advance Event-node `+0x04`; exhausted list returns NULL; qualifying item returns **payload** (EDI), not the Event-node pointer.

The executable has distinct `0x615C10` primary Event predicates. **Do not reuse the primary Event `payload+0x44 & 0x61` mask as this secondary helper's acceptance test**: its actual masks, virtuals and output identity differ.

## B. New branch-by-branch detail: `0x4A7B30` handles the two lookaheads differently

- **Current+14**: `0x4A7B31–0x4A7B67` reads global current date `0x9847FC`, targets **date+14**, bounds it via `0x616A30` against the **secondary date-indexed collection** `0x947AF0` with its date origin `0x947AF8`, and calls the filtered `0x4A7EF0` on that bucket. For each qualifying payload, `0x4A7B70–0x4A7BAB` resolves its two side/ref objects at payload `+0x14` and `+0x28`, invoking **`0x50EE00` with literal argument `0x16` and the payload** on each; continues from the original Event's next node. This is an actual side-dependent producer, not a zero-effect scan. The football meaning and RNG/write side effects inside `0x50EE00` are not closed here.
- **Current+3**: `0x4A7BAF–0x4A7BF0` separately obtains `date+3` within `0x947AF0` and calls the same `0x4A7EF0` filter. Each accepted payload leads to **`0x50F3C0`** with literal `0x16` for both payload side references at `0x4A7BF4–0x4A7C20`. Only then `0x4A7C25–0x4A7C61` resolves each side and invokes **`0x4A7F50(side_owner, current+1, current+3)`**, which is capable of scheduling postponements. The two original lookahead producers `0x50EE00` and `0x50F3C0` are **not interchangeable** merely because the same payload is passed.
- **Tail call**: after the +3 branch, `0x4A7C75–0x4A7C89` calls `0x4A7C90` separately with literals **`0xAB`** and **`0xAE`**. Their resulting user-visible or state side effects have not been fully identified; this is evidence of another phase/order boundary, not proof of which football event they represent.

## C. Narrow native `0x4A7F50` postponement qualification

Fresh `0x4A7F50–0x4A8061` inspection confirms the existing Recovery475 source outline and further qualifies its input:

- Iterate a supplied original roster owner `+0x294` count and its 16-bit player-ID array beginning `+0x244`. Resolve player records with `0x250` stride from global `0x875640`.
- Only if player `+0x14` has **bit2** set (`shr 2; and 1`) obtain a **signed 16-bit** primary-club/source index at player `+0x10`. Negative index chooses fallback global club pointer `0x874B94`; nonnegative resolves via club-owner table `0x874B90`. The meaning of bit2 and fallback must not be guessed.
- For each day **current+1 .. current+3 inclusive**, traverse **primary** date-indexed `0x947AD8` events. Reject an Event whose `+0x08` link is nonzero or whose payload `+0x44` has bit `0x20` set. Resolve both payload sides `+0x14/+0x28` and compare concrete source pointers with the prior derived club context.
- An equal side calls **`0x510BA0(0)` at `0x4A801F`** on that original Event. This proves a specific **secondary-event-induced primary rescheduling path**, not just that a callback with a suitable name exists. Source wrapper and priority behavior of `0x510BA0` was previously proven by canonical original routine experiments, but the triggering semantic event class here remains UNKNOWN.
  
**Why this matters:** Even with all current `PrimaryScheduleShadowState.prepare_ordinary_day(current,current+1)` Side cases correct, the reconstruction cannot infer these two earlier secondary lookaheads from primary fixtures alone. A byte `+0x0C` eligibility, payload virtual `+0x28` value2, conditionally invoked `+0x60`, and two different `0x16` ref callbacks can change which source original events eventually qualify. The source-accurate result for a real career is still conditional on actual secondary source event producers.

## D. Current merged code / implementation work owned only by Codex

Current main starting HEAD `ccdc513ed098c69dbf277e1623a76e8221303b76`; Codex `e166ae4d70c32b41f8dcef86b3d3d42b19a24262`. `reconstruction/human_gameplay.py` `_advance_original_management_turn` still uses only `primary_schedule_shadow.prepare_ordinary_day` and `_process_current_primary_day`. `reconstruction/primary_schedule_shadow.py` has neither the secondary collection nor source `0x4A7EF0` acceptance virtuals. This is the **already-confirmed missing integration** in Recovery475; this report newly **closes exact original secondary filter and +14 vs +3 branch source dispatch**, not complete class identity.

Minimal Codex-only next proof: find actual class/vtables and producer for one `0x947AF0` Event; execute original `0x4A7EF0` on positive/negative canonical source fixtures (clear vs linked, +0x0C bit0, virtual +0x28==2, +0x4C/+0x04 and +0x60), then separately inspect/verify `0x50EE00` and `0x50F3C0` side effects for literal22 and bound `0x4A7C90(0xAB/0xAE)` tail; only then integrate source-owned events and `0x4A7F50` with stage/rollback and source PResults. Respect prior urgent actual first-match PPreMatch/PResults/return, Inbox and Save/Load prioritization. Neither a guessed "training" category, a global day timer, nor merged primary calendar is acceptable.

**Evidence classification:** direct exact shipped executable *addresses, branch/call order, pointer/flag checks, literal arguments*: **ORIGINAL-SOURCE VERIFIED in Recovery482**; concrete meaning of secondary event type, +0x16 semantics, +0xAB/0xAE effects, equivalence to original Windows match outcomes: **UNKNOWN**. Current Python secondary phase missing: **CODE-CONFIRMED** and historically audited Recovery475; actual source-event incidence/wrong match outcome: **CONDITIONAL and unobserved**. No game binaries, ZIP, original disassembly dumps, new implementation, CI or Windows receipt committed. Gate13 OPEN, Gates14–17 and full original-scope Windows11 release incomplete.
