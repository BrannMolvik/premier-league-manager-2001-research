# Original management menu and Inbox functionality audit

12 October 2026. Baseline `main` **aed9029a354a5a7af2e5279f65aad5d05059a0cd**.
Independent implementation branch `codex/original-menu-inbox-audit`.
SupportStart/staff, simulation, RNG ownership and `agent-runtime` are untouched.
The separate performance experiment is preserved at local commit `da7ce0fa`
on `codex/issue482-graphics-performance`; it is not part of this fix.

## Evidence and limits

Canonical original executable rehashed before bounded, read-only Capstone
inspection: SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`,
4,714,541 bytes. Private Drive metadata was checked; the already-present
authorized local identical executable was reused. Original resources/fonts
remain subject to existing size/hash/header validation. No original program
was executed; raw disassembly and proprietary executable remain outside Git.

SOURCE-VERIFIED below means a manually followed instruction/owner/argument
chain, not a candidate byte hit, historical research assertion, passing Python
test or observed original gameplay. This run has **no interactive Windows
acceptance**. Earlier research is not authoritative where contradicted below.

## Menu root cause and correction

Three incorrect constructor interpretations had propagated into code/tests:

| Item | Before this fix | Canonical native source / correction |
| --- | --- | --- |
| Title background | `0x8002` for every enabled title, forcing atlas row 2 and suppressing hover row 1 | Constructor selection is zero; title `+0x4C` updates only the arrow. Background is `0x2`; hover adds `0x8`. |
| Label colors | Normal child black, selected child white | `0x6529F0`: selected uses `+0x46` black; normal uses `+0x44` white. Titles remain normal white. |
| Child text origin | Inset `(0,12)`, line `(30,17)`, clipped at row bottom | Inset `(12,0)`, line `(42,5)`. Original fonts and half-open clip remain unchanged. |

The error was **stack argument forwarding**, not a release event leaving all
buttons down. At `0x47A910` / `0x47AAC0`, `0x6528D0` receives:

`(30,0,wrapper,0,font,0x2001,0,offsetX,0,white,black,12)`.

Title wrapper/font are `0x943810/0x8A3550`, child
`0x9437D0/0x8CAB80`; `offsetX` is 0 / 12. The final 12 is the notification
mask, not selection or a Y offset. The title arrow's separate `0x8000`
setup must not be attributed to its background.

`0x6528D0` forwards **A1..A6,A8..A12** to `0x651E30`; the latter returns
44 bytes. With the saved ESI still on stack, `0x652911 [esp+0x20]` retrieves
**A7**, and `0x65291A -> vtable+0xB0 -> 0x652B10` clears selection.
`0x651E30` stores forwarded B7/B8 at `+0x40/+0x42` and B9/B10 at
`+0x44/+0x46`. `0x6520C0` uses `+0x40` for X, `+0x42` for Y and adds
`29//2-line_height//2` vertically. Constructor color triples are all-white
then all-black in A10/A11. This supersedes the Recovery 177/179 offset,
constructor-selection and color claims in `GATE13_PMENU_CHROME_TRACE.md`.

## Menu behavior: original versus reconstruction

| Interaction | SOURCE-VERIFIED original | Current correction / boundary |
| --- | --- | --- |
| Fresh management / opening | PMenu initially off stack; fresh tree Team root 2 expanded, Squad child `0xCE` selected. Header event 2 pushes menu (`0x432690 -> 0x5EBEA0`). | Existing routing retained; only active child has selected background. No fabricated all-clear. |
| Hover | `0x47ACF0` handles SelectBmp child ID2 and changes bit `0x8` on arrow/background, independently of bit `0x8000`. | Existing animation retained. Atlas selector `0x47AC00` prioritizes disabled, selected, hover, normal (3/2/1/0). Titles now reach hover frame. |
| Press / release | SelectBmp `+0x6C=0x64F7A0`: enabled and not-held gates, local press bit `0x10`, parent action `+0x10` on press. `+0x70=0x64F860` clears press bit; parent `+0x14=0x428AE0` is no-op. | Existing press routing retained. Release must not clear tree selection or expansion. No new pressed-background frame invented. |
| Expand category | `0x47AC60` rejects already-expanded root; closes other expandable roots and sets chosen root bit0. `0x4825E0` changes its arrow only. | Existing expansion retained; active child can be hidden under another category without being deselected. |
| Select screen | `0x47AD60` rejects selected/guarded child; calls factory `0x47AEC0(id,0)`, changes child selection only after nonnull success; `0x482700` updates arrow and background. | Existing transactional supported-panel navigation retained; selected child remains black on atlas row2. Unimplemented destinations remain fail-closed. |
| Close / reopen | `0x432970` dismisses through `0x4329F0` at x<524 or y<96 and x>700. Open does not call `0x482BF0` (the separate direct-selection/reset factory). | Existing popup/tree ownership retained; reopen keeps expanded root and active child. Exact hidden animation timing is not newly qualified. |
| Navigate with popup open | `0x47AD60 -> 0x5ED2A0` removes/re-pushes an already-open menu around content replacement. | Popup remains open on supported child navigation; not forced closed to resemble a modern menu. |

The four menu assets and two concrete label fonts are unchanged. No blanket
state reset, timer, replacement widget or new menu destination was added.

## Inbox functional completeness at this baseline

| Feature | Original evidence | Actual reconstruction / missing work |
| --- | --- | --- |
| Open Inbox | Header ID1 `0x4326D6 -> 0x482BF0(0x65)` and PMenu EAMail child `0x65`; active singleton guard | Both entry routes connected. Earlier audits saying no PEAMail destination are stale. |
| Delivered messages / ownership | `DBRUser+0x6B4` delivered append list, distinct from pending MPM envelopes | Real per-manager delivered owner and bridge implemented for initial `EAMPlayerAskTransferListsub` only. Not a complete native message-class system. |
| Ordering / filtering | `0x472680` ten predicates; `0x472880` sort, five comparators; fallback date comparator `0x472C60` strictly newer first | <=16 initial-subtype insertion order supported; equal-date stability retained. >16 hybrid sort and multi-row player-string comparator fail closed. Filter/sort buttons not connected in ordinary host. |
| List / viewport | `0x471D20` reads sorted `+0x68` array / `+0x6C` count; eight rows, 20px pitch; max scroll=count-8 | Source data bounds and actual 532x18 normal/selected strips implemented. Ordinary scrolling is not connected; only first viewport painted. |
| Names / subject / date | Row buffers `+0x174/+0x74/+0x274`, child IDs2/3/0; typed player/club descriptor, original STR/IDX | Transfer subject and localized date retained; names require proven association snapshot and fresh one-user nickname context. Glyph-mask helpers exist, but **host does not paint row text**. |
| First selection | Rechecked `0x471B80`: different row selects sprite (`0x470B40`), calls message virtual `+0x1C(0)` and preview `0x471620`; does not enter modal/clear status bit2 | Sprite/pointer selection only. Body/RNG production is deliberately incomplete; selection is not full native functionality. |
| Repeat activation / read state | Same row calls `0x471270`; `0x4712FA` clears record `+8 bit0x02` before modal. `0x471780` chooses `+0x70C/+0x73C` status controls from that bit | Repeat press fails closed; no PEAMMessage, mutable native status or status icons. Do not label first selection as “mark read”. Exact read/unread resource-wrapper mapping is not newly certified here. |
| Preview / body | `0x471620` and subtype virtual formatting, distinct blank-selection state | Disabled original preview at (246,343), 532x187, is painted only with no selection. Selected formatted body/enabled art absent. Retained templates/reason fragments are not complete displayed messages. |
| Links / tagged names | Row `0x471C50` resolves tagged descriptor through `0x5CE9B0` before panel dispatch | Raw target/association and tagged glyph helpers exist; no live link hit/dispatch/rendering in ordinary Inbox. No synthetic universal player/club links. |
| Previous / next | Detail results6/7 at `0x471564/0x47153A` use previous/next sorted-array index; enable bounds computed in `0x471270` | Original assets retained; no functional detail controls. Must preserve filtered-array index, not mailbox serial order. |
| Delete / reply / subtype actions | Result8 invokes message `+0x44` then `0x471150`; results9..11 invoke subtype `+0x20(result-9)` and conditional follow-on dialog/queue | No live actions. Graphic filenames alone do not prove full labels, confirmation, recipient, mutation or message-specific effects; subtype-specific source trace still required. |
| Detail Escape / return | Recovery441 closes `0x473870 -> 0x6539F0 -> PostMessageA(WM_USER,16) -> MyWindow 0x532B80 -> result16 -> 0x5EB920`. Before dispatch, list refresh restores `+0x127C` | No live modal owner; host's generic Escape/fullscreen compatibility binding is not native Inbox close. PMenu can navigate to supported panels, not proof of native previous-screen parity. |
| Progression / saves | Delayed transfer envelope `0x613EE0` pipeline and delivered user owner are separate | `_finish_shared_primary_day` processes qualified due events. `internal_save.py` snapshots/restores delivered mailbox, pending queue, order/serials, association and retained reason. Mutable read/action state and all other classes absent; retention helper is not full automatic expiry. |
| Multi-user / Windows acceptance | Native owner-specific list/selected user | Registry/recipient guards exist; full 2–6-user UI, multiple original club comparisons and interactive Windows Inbox acceptance not demonstrated. |

**Conclusion: Inbox remains PARTIAL and unsuitable to label original-equivalent.**
No Inbox production change is safe to fold into this small menu correction.
Existing first-select/repeat/owner/save tests are retained; the host test now
also locks both current RNG streams against consumption by incomplete preview
or rejected detail. This does not validate those streams as correct ownership.

### Precise next implementation slices (review before changing shared code)

1. Independently source-close the CRT thread-local `0x66951C -> 0x66D553`
   owner from startup/schedule/day progression to first preview. **PR #638 stays
   DRAFT/BLOCKED**; do not advance only `match_rng`, invent a reason or merge it.
2. Connect already-qualified row text/glyph colors/clipping and status-icon
   wrapper ownership without pretending body/actions work; then wire existing
   native filter/sort/scroll data only within their proven input limits.
3. Once the body producer/owner is closed, implement real PEAMMessage 710x420
   source layout, typed links, result dispatch, scroll restoration and mutable
   record persistence. Trace delete/reply subtype effects before enabling them.
4. Obtain fresh authorization before any interactive comparison; test more
   than one original club/mailbox and the full open/select/detail/return/save
   journey. Passing source-shaped tests cannot substitute for that receipt.

## Verification

The non-interactive menu journey exercises real host pointer routing through
open, hover, press, release, two category expansions, successful Fixtures
selection, dismiss and reopen. Pixel composition tests check corrected frame,
color and label geometry. An opt-in, canonical-hash-gated Capstone regression
checks constructor/forwarding/draw/color instruction landmarks against the
licensed executable (`FM2001_ORIGINAL_EXE`); no original bytes bundled in tests.

Focused/full regression results are recorded in the PR. No gate closure,
package-launch or complete Windows gameplay acceptance is claimed.
