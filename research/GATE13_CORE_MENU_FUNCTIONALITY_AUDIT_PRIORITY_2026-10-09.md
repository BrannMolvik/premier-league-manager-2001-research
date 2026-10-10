# Gate 13 core-gameplay and PMenu original-fidelity audit — priority directive

_9 October 2026 KST. Daniel-directed. Audit-only assignment; Codex owns implementation._

## Why this outranks isolated cosmetic investigations

Daniel identifies the most significant regressions as the broken main first-team/Squad management screen, missing or nonfunctional inbox, and wrong menu selection, destination/pathing and basic management actions. A screen that merely displays player numbers while the original menu or inbox cannot be used is not an acceptable playable implementation. The original Windows 11 compatibility port is the only current scope; modern UI, Settings and visual improvements remain deferred.

**Immediate audit priority is the original end-to-end player journey and functionality**, above isolated palette, bitmap, FastView, Gate-14, release-provenance or minor styling research. Preserve existing evidence; do not infer that selection-dependent row artwork is correct merely because newer Codex work restores some blue cells.

## Required evidence-based audit order

### P0-A. PMenu selection and destination graph (first)

Build a **complete menu/action map** starting at the actual management PMenu root. Check original executable factory/caller/flag and original language/resource data against the current implementation, not against speculative replacement menus.

- Distinguish nine documented root categories, 28 static child entries, and the separate five-row team-order subtree whose ownership remains unresolved.
- For each root/child entry identify **original item identity, parent/root ownership, control and action type** (expand/collapse, navigable panel, dialog, command, modal, close/back, etc.), factory/action target and actual integrated destination (if any).
- Verify pointer down/up and hover, enabled/disabled and selection bits, title/child activation, popup visibility/overlay, dismiss-on-outside-click, repeat click, update/animation frames, route transitions, and what happens on failed/unintegrated destinations.
- Follow **source input → dispatcher → factory/handler → state update → actual visible destination → close/back/return**; do not equate recognized menu IDs with working navigation.
- For unsupported routes, label precise missing stages rather than silently treating every child as a separate missing full-screen presenter.
- Independently compare at least two clubs/states for shared PMenu behavior. Southport is only a reproducible fixture, not a special case.

### P0-B. Inbox / original EAMail route (second)

Trace root ID `0x1`, child ID `0x65`, original PEAMail factory `0x47AEC0`, specific constructor `0x474B10`, final PEAMail vtable `0x7C2950` and CMessageList `0x7C2A50` into the original visible inbox.

- Identify panel hierarchy and exact geometry, graphics/fonts/text, list and message-row ownership, source message collection and **global ordering/interleave**, filtering/read/unread/selection state, message detail and actions, action targets, dismiss/return and persistence.
- Compare current runtime dispatch and panel coverage. Original PEAMail panel identity has been proven, but the clean-room does not yet integrate it: **do not call inbox fixed or playable**.
- Do not substitute generic Tk widgets, merge independent message families with guessed sort order, or treat recovered event producers as proof of complete inbox layout/semantics.

### P0-C. Main first-team/Squad screen and core controls (third)

Reconstruct a **control-by-control original-to-current comparison** of the first visible club-management landing, including PMenu and central header, **1ST / RES / combined view**, player names, roles, statuses, selection-dependent backgrounds, button hover/press/disabled states, formation/tactics tabs, row selection/drag/drop and active first/reserve membership.

- Check the actual original panel/control owner tree, draw/z-order, source assets, coordinates, fonts, flags, live data binding and changes after a control press.
- For first-team/reserve/formation, verify each selectable tab shows the correct original destination and functionality; a visually clickable control leading to a blank/unintegrated surface is a functional defect.
- Verify all club-neutral behavior across Southport and another club. Audit the **most current Codex branch** separately from `main` and say which implementation/version is being described.
- Distinguish recovered basic blue populated cells from still-unresolved full selection/lineup palette-state mapping; don't make palette work a prerequisite for finding broken tab/menu routes unless it directly blocks them.

### P0-D. Main management actions, progression and returning (fourth)

Follow a user's ordinary route:

`PStartMenu → New Game/TeamSelect → choose club → first-team/Squad → PMenu → EAMail → back → formation/tactics → fixtures/table → NEXT/MATCH/advance → return to management`.

For each path record original input/control owner, factory/dispatch, live game-state transition, visible result, back/navigation behavior, and clean-room result. Include original Save/Load/Calendar/Cup/management actions as applicable; determine whether each is a panel, dialog, command or modal rather than assuming an identical presenter shape.

- Audit specifically **ordinary original-look NEXT/MATCH reachability**, not merely the distinct development-mode controller that can play fixtures.
- Do not claim a separate generic developer test UI restores the original in-game paths.
- Check whether resource-loading/input suppression, repeated snapshot recomputation or other reconstruct-only mechanisms prevent response or discard clicks; distinguish code-level risks from measured Windows latency.

## Evidence standard / deliverables

Audit the original canonical hash-gated shipped executable, original resources/data and recorded valid original observations; corroborate important prior address/CFG/RTTI claims rather than treating old research or current tests as proof. Label every finding **CONFIRMED / PROBABLE / UNRESOLVED** and each fidelity comparison **EXACT / COMPATIBILITY-EQUIVALENT / PARTIAL / WRONG / UNKNOWN**.

Persist **one auditable menu-to-function matrix** with columns:
`original menu/control, parent/child, original evidence (addresses/resources), native action kind, original destination/side effects, current main outcome, current Codex branch outcome, observed defect, severity, confidence, missing source proof, minimum corrective recommendation`.

This matrix must describe every mapped child even if original semantics remain unknown; explicitly distinguish **working**, **click accepted but nothing usable opens**, **not wired**, and **unknown**. Include end-to-end route tests/receipts where actually available and make missing Windows observations explicit.

After each useful audit finding, append evidence to the fidelity ledger and a concise independent **Codex implementation handoff** ranked by main-menu usability, inbox functionality, main first-team interaction, pathing and NEXT/MATCH. Do not edit Codex branch, implement game code, merge, mark a gate complete or create another acceptance package. Keep canonical original resource/screen mappings and Windows11-only freeze.

### Stop/reprioritize condition

Until these core player paths are fully mapped and the major functional defects are identified, **do not select narrow color/texture/Font/ FastView or Gate-14 work merely because it is easier**, unless a concrete source dependency directly blocks one of the above audit questions. When original source access is blocked, audit the next actionable core path in the repo and explicitly name the missing evidence.
