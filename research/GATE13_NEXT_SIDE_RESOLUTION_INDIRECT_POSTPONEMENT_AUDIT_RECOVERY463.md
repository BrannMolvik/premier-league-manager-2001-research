# Recovery 463 — tomorrow's Side-resolution pass can create postponed wrappers indirectly

_10 October 2026 KST. Independent original executable **AUDIT ONLY** under `research/CURRENT_STATE.md`. Continuing the exact Recovery462 per-event wrapper qualification question, not restarting previous gates or creating game code. Codex exclusively owns source implementation, Windows11 acceptance and CI._

## Repository and original provenance

- Verified `main` at start **`deac105647aba3a947787677532168c9d9475a19`**, agent-runtime Recovery462 `audit_only / implementation_allowed=false`, Codex implementation branch **`0ae745d1b56f45cade460f03cd893849a2f53b45`** unchanged. Issue [#482](https://github.com/BrannMolvik/premier-league-manager-2001-research/issues/482) remains open; no new playable implementation or Windows11 receipt.
- Authorized privately-held original `footballmanager.exe`: **4,714,541 bytes**, SHA256 independently checked **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. Native `objdump -d -Mintel` and original RTTI/vtable only; no source bytes/art/saves uploaded.
- Reproduce exact calls with `objdump -d -Mintel --start-address=0x6165d0 --stop-address=0x616612 footballmanager.exe`, `0x514520..0x514564`, `0x510320..0x51037E`, `0x513FE0..0x513FF5`, `0x615F40..0x616074`, `0x510BA0..0x510C0A`; original `Side` vtable `0x7C4D50` has **virtual +0x00→0x510320**, verified from `.rdata` bytes.

## A. Complete original indirect call chain and guards

Recovery462 correctly distinguished current-day `0x615C10` direct `0x510BA0` checks from PResults' following-day `0x616600→0x6165D0→0x514520` participant-resolution operation, but left its **indirect mutation** unresolved. The actual original executable provides a source-verified chain:

```text
PResults::0x4A7280
   -> 0x616600    (one selected calendar, current_date - calendar_base + 1)
     -> 0x6165D0 (iterate linked Events in one next-day bucket)
       -> 0x514520(Event)
          require Event+0x08 == 0, payload != NULL,
                  payload+0x44 bits0x20 and0x40 clear
          -> payload Side+0x14 virtual+0x00
             [0x7C4D50, concrete Side::0x510320]
              require Side+0x04 == 0 and generic source 0x4F28A0 returns non-null
              -> 0x513FE0(original Event reference)   // follow Event+0x08 chain to terminal
              -> if terminal Event+0x10 != -1:
                   original source calendar 0x510300
                   -> 0x615F40(event references, selected calendar)
                        -> 0x616020 eligible related-event scan
                        -> conditional 0x510BA0(chosen Event,0)
                            require chosen Event+0x08 == 0
                                    and chosen payload+0x44 bit0x40 clear
                            -> new PostponedEvent, old Event+0x08=new wrapper,
                               native insertion requested at old relative slot+7
          [0x514520 tests Event+0x08 again]
          -> only if still clear, resolve second concrete Side+0x28 virtual+0x00
```

**Exact machine-call edges:**
- `0x616600` reads original current date **`0x9847FC`**, subtracts selected calendar base `+0x08`, **increments** relative slot at `0x61660A`, and invokes `0x6165D0` at `0x61660C`. `0x6165D0` obtains that *single* bucket's linked list and calls `0x514520` on each Event at `0x6165E7`.
- `0x514520` checks the Event's `+0x08` link first (`0x514524`), payload via Event vft+0x18 (`0x51452D`), and clear status bits **0x20 and 0x40** (`0x514536..0x514548`). It invokes **virtual +0x00** on embedded concrete Side at payload **`+0x14`** (`0x51454A..0x514550`), then **rechecks Event+0x08** at `0x514552..` before invoking the second Side at `+0x28` (`0x514559..0x51455F`).
- Original `Side` vft **`0x7C4D50` +0x00→`0x510320`**. Within it, the branch with uncached `Side+0x04=0` and successful `0x4F28A0` calls **`0x513FE0`** at `0x510337`, checks the resulting event **`+0x10 != -1`** at `0x510342`, selects calendar `0x510300` and invokes **`0x615F40`** at **`0x510355`**.
- **`0x513FE0`** loops through the event `+0x08` links until the terminal Event (see `0x513FE4..0x513FF4`); do not assume the related input is always the immediate Event rather than an existing wrapper-chain endpoint. `0x510320` later also conditionally updates source-side data (`0x51035A..0x510373`).
- **`0x615F40`** looks up candidate events from a selected collection's relative bucket index and immediate adjacent source positions (`0x615F51..0x615FB4`); its helper **`0x616020`** skips candidates when their resolved payload's **`+0x44 bit0x20`** is set, and calls the candidate event's virtual **`+0x04`** with an original `0x4F2CB0` reference selector (`0x616032..0x616058`). On matching/ordering branches it may invoke the same `0x510BA0` at `0x615FD2`, `0x616003`, or `0x616013`. These are **three of the seven direct CALL sites already counted in Recovery462**, *not three additional instruction sites*.
- `0x510BA0` has its own guards and may do nothing; passing through `0x615F40` does **not** mean every Side resolution postpones a fixture.

## B. Correct interpretation and new implementation consequence

**New source-backed finding:** PResults' **tomorrow-bucket Side resolution is NOT necessarily read-only**. It can reach **the very same native PostponedEvent creator indirectly** via `Side::0x510320→0x615F40`. Moreover, `0x615F40` may choose a *related source Event* from the bucket or adjacent indexed positions, not necessarily the one currently passed to `0x514520`. Consequently, a per-date model that only audits “today's direct wrappers” and assumes tomorrow's participants are passive would be incomplete.

This **does not** restore the Codex global blanket invalidation as an exact original rule: the verified source chain is gated by **the next-day bucket, each Event's linkage and payload flags, Side source resolution/cache state, terminal wrapper-chain state, original participant predicate, and nearby candidate event order**. It demonstrates a *bounded indirect dependency graph*, not “every future match becomes UNKNOWN on any quiet day.”

**Codex-only implementation handoff, now qualified:**
1. Source-qualified per-event shadow must include or conservatively track **side-reference resolution/cache**, **source event terminal wrapper link**, **nearby bucket candidate references**, **calendar family/relative slot**, and the **post-callback link recheck**. Even without complete implementation, preserve UNKNOWN precisely when this dependency cannot be proven.
2. For quiet-day NEXT and tomorrow's future fixture, test a benign Side resolution case retaining source-verified clear links *and* a conflicting Side resolution case where `0x615F40` selects and wraps another eligible event. For an unknown participant/reference, **refuse without advancing date or RNG**; do not force all wrappers clear or erase all source confidence.
3. For source-complete fixed-League paths, test an actual normal PBg ID3 click feeding Codex's existing bounded `HumanGameplayController.advance_original_management_turn`, reaching pending human pre-match and returning through original PResults without mutating the game before a failed guard. Verify across **two actual clubs**, **two human managers in one save**, and real Windows11 normal input. The clicked NEXT button and simultaneous TeamSelect are still missing in current Codex and main.
4. Do **not** ask Codex to redo bitmap/pixel audit, reimplement its existing match simulator, or overwrite original source art; return to functional implementation.

## B2. Follow-on source step — ordinary NEXT candidate discovery can postpone and then skip its own candidate

The **same `0x514520→Side::0x510320→0x615F40→0x510BA0` indirect chain** is *also entered during ordinary original NEXT candidate discovery*, not only during PResults tomorrow refresh:

- `0x615D10` scans the source calendar day buckets and invokes common candidate filter **`0x615C50`** at `0x615D3B` with its manager selector and source flags. The previously source-verified `PBg::0x432190` NEXT action calls `0x615D10`.
- `0x615C50` first checks payload presence, status and current Event+0x08 unlinked state (`0x615C65..0x615CDD`), then **calls `0x514520(Event)` at `0x615CE1`**.
- As the present Recovery463 source chain shows, `0x514520` can resolve a concrete Side and call `0x615F40`, which can conditionally create a new `PostponedEvent` through `0x510BA0` and set an Event's +0x08 wrapper link.
- Crucially, **`0x615C50` rereads candidate Event+0x08 at `0x615CE6`** and when nonzero continues scanning at `0x615CED`; only when still zero does it return the Event at `0x615CF8`. Thus an otherwise initially eligible Event may be **skipped after native candidate-time Side resolution changed its wrapper linkage**.
- This source behavior is distinct from `0x615DA0` explicitly invoking a payload virtual +0x64 conflict check (Recovery447); neither native event *query* can automatically be represented by a pure function that only reads cached fixture dates.

**New implementation boundary:** the source-equivalent NEXT selector cannot be certified just by looking at the first clear wrapper and assuming it stays clear. It needs the original candidate-time Side resolution and its **post-resolution Event+0x08 recheck**, or must refuse unknown dynamic cases before mutating the saved game state. A date-only, display-derived selector is insufficient. Conversely blanket UNKNOWN across all future event owners after every day increment remains unsupported by these narrowly scoped original call chains.

**Evidence reproduction:** `objdump -d -Mintel --start-address=0x615c50 --stop-address=0x615cfb footballmanager.exe` and `--start-address=0x615d10 --stop-address=0x615d55`; linked methods `0x514520`, `0x510320`, `0x615F40`, `0x510BA0` as cited in Section A. **CONFIRMED** native call and recheck sequencing; **UNKNOWN** frequency/pattern of real-game candidates affected, Windows input outcomes and all other indirect writers.

## C. Limits and known unfinished gates

- **CONFIRMED in original executable:** precise indirect virtual dispatch through next-day Side resolution into `0x615F40` and the existing `0x510BA0` guarded creator; chain-following in `0x513FE0`, second-Side call suppression when Event+0x08 becomes linked, additional candidate-specific filter `0x616020`.
- **NOT CONFIRMED:** the concrete frequency or particular club/date fixture effects of this path in a live original game; exact range of the scan's “adjacent” indices as original user-visible concepts, effects of every other virtual producer, and whether any particular fresh direct League event is always retained unlinked.
- **No original program or Windows11 GUI was run. No gameplay/Codex code, assets, user saves, CI/merge, Windows build or gate state was changed.** Gate13 OPEN; Gates14–17 and full original-scope Windows11 release INCOMPLETE.
