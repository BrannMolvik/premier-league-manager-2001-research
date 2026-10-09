# Recovery 447 — exact native NEXT scheduled-event eligibility, participant matching, and live side-effect gate

_9 October 2026 KST. Independent **AUDIT ONLY** work continuing source-first P0-D NEXT/MATCH from Recovery446, not a new feature. Original-only Windows 11 compatibility; Codex implementation branch and all game/source assets remain untouched._

## Canonical provenance and repository state

- Current main at start: `341be1684a8178c0d5a231a9641ed3f0f021319f`. Source directive `research/CURRENT_STATE.md` keeps the genuine interactive management game journey (first-team, inbox, PMenu, NEXT/MATCH) ahead of visual or later-gate work. Agent runtime confirms `worker_role=audit_only`, `implementation_allowed=false`.
- Authorized original `/mnt/data/fm2001_private/footballmanager.exe` was **rehash-checked locally**: size **4,714,541**, SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. No original game process was launched, and no proprietary bytes/disassembly/art are uploaded.
- Source reproduction (original PE): `objdump -d -M intel --start-address=0x615c50 --stop-address=0x615e20 footballmanager.exe`; `0x510a40..0x510a73`; `0x4f2830..0x4f289d`; `0x5140c0..0x514109`; `0x514520..0x514564`; `0x4321e4..0x432241`. Vtable slots are verifiable with `objdump -s --start-address=0x7c4ce4 --stop-address=0x7c4d31` (Match) and `0x7c9fe8..0x7ca014` (PostponedEvent).

## A. Original ordinary manager-specific lookup is a filtered native event query

The actual **`PBg NEXT`** path `0x4321E4..0x43220C` gets current manager via `0x4139D0`, reads user **`+0x5B4`** schedule/participant selector, invokes `0x4079D0` to get its calendar collection and calls **`0x615D10`** with user selector, current date **`0x9847FC`**, and literal **1**. This is a source-specific manager/event query; it is not just a global 'next fixture date' scan.

`0x615D10` subtracts collection base `+0x08` from the supplied date and walks its day-pointer array (bounded by collection `+0x04`) in increasing slot order. For each day it calls the linked-node selector **`0x615C50`** with an explicit combination of arguments: the current manager selector, no payload `+0x4C` equality restriction, an enabled return/search mode, and two false flags. These literal argument values matter; they are not defaults guaranteed for other consumers of `0x615C50`.

### `0x615C50` eligibility gates — source instruction boundary

After obtaining the candidate **Event** and its polymorphically resolved match/event payload via original Event virtual **`+0x18`**, the ordinary call above applies:

| Stage | Original addresses | Exact source requirement / effect | Type/status |
| --- | --- | --- | --- |
| Payload exists | `0x615C65..0x615C74` | Event's virtual `+0x18` must return non-null payload | CONFIRMED |
| Payload status bit 5 | `0x615C76..0x615C8C` | `(payload+0x44 & 0x20) == 0` for ordinary NEXT caller's false flag | CONFIRMED |
| Manager/participant selector | `0x615C97..0x615CB3` | when manager selector is non-null, a `0x4F2CB0` original selector object is built and passed to event virtual **`+0x04`**; result must be nonzero | CONFIRMED |
| Original event linkage | `0x615CC1..0x615CC6` | `Event+0x08 == 0`; preexisting linked/wrapper state skips candidate | CONFIRMED |
| Payload status bit 6 | `0x615CC8..0x615CD3` | `(payload+0x44 & 0x40) == 0` | CONFIRMED |
| Payload status bit 0 | `0x615CD5..0x615CDD` | for literal false argument5 of NEXT, `payload+0x44 & 1` skips candidate | CONFIRMED |
| Deferred native update | `0x615CDF..0x615CEB` | `0x514520(Event)` invokes guarded operations on *underlying payload* subcontrols `+0x14` and `+0x28`; `Event+0x08` is checked **again** afterwards. Event is returned only if it remains zero | CONFIRMED callback and recheck; specific mutation effect UNKNOWN |

Other `0x615C50` callers may supply non-null `payload+0x4C` equality filter or different booleans; they must be audited independently. For the ordinary NEXT lookup, the three required status bits together mean payload **`+0x44 & 0x61 == 0`** on the eligible path, *in addition to* the independent manager match, event-link check and native revalidation. These masks are **not** yet named 'completed', 'postponed', 'human', 'AI', etc.; names require separate status-field producers and consumers.

**Subtle but important:** `0x615C50` is **not a purely observational predicate**. It invokes `0x514520` before returning a qualifying candidate. That method checks `Event+0x08` and payload flags `0x20/0x40` before calling virtual functions on payload fields `+0x14/+0x28`, then original `0x615C50` checks `Event+0x08` again. These operations may make a previously considered event ineligible. Exact side-effect semantics need original object types/state testing, but simply filtering pre-cached immutable fixtures would miss this source-order behavior.

## B. Concrete Match and PostponedEvent selector ownership

The original MSVC `Match` vtable **`0x7C4CE4 +0x04 -> 0x510A40`** and `LeagueMatch` vtable **`0x7C4C24+0x04 -> 0x510A40`** implement the manager-specific event predicate:

- `0x510A40` checks participant reference objects at **`Match+0x14`** and **`Match+0x28`** using **`0x4F2830`** and returns true if *either* matches the original selector argument.
- `0x4F2830` is **structured reference equality**, not just integer club-ID comparison. If the reference's virtual `+0` resolves to non-null, it compares the resolved source reference pointer/value to the selector's resolved result; otherwise it checks original reference fields `+0x0C` (16-bit kind), `+0x08` (identity/context) and `+0x0E` (16-bit selector). Source predicates can therefore compare unresolved symbolic references with full identity data rather than only a materialized direct club ID.
- Original `PostponedEvent` vtable **`0x7C9FE8+0x04 -> 0x5140D0`** delegates its event predicate through the wrapped Event pointer at **`PostponedEvent+0x14`**; the wrapper does **not** independently replace participant matching. Source `PostponedEvent` virtual `+0x18 -> 0x514100` separately delegates underlying payload resolution.

This closes an essential source link: **the returned NEXT event is attached to either original match participant reference, and postponed wrappers preserve the underlying event's reference-selection behavior**. Existing multi-club eligibility cannot safely be collapsed into `club_id in (home_id,away_id)` when original references remain symbolic.

## C. Explicit current Codex/main comparison and scope boundary

The current Codex `reconstruction/primary_schedule_shadow.py::direct_fixed_league_header_candidate` is explicitly a **bounded fail-closed fresh direct LeagueMatch projection**. It uses preserved day order/head order and participant references but refuses many symbolic, postponed or non-fixed-league entries; its own docstring limits the scope. That is not evidence the whole startup scheduling reconstruction is wrong.

However it is also **not equivalent to the original full `0x615C50` filtering/side-effect contract**, since the original includes payload `+0x44` bit masks, opaque payload subcontrol callbacks, source link state and polymorphic wrapped Event selector. Likewise `next_match_date` is a bounded calendar-level helper rather than live NEXT gameplay. **This is a verified integration/coverage gap, not a finding that existing bounded code violates its own contract.**

The live `reconstruction/original_game_host.py::on_click` on both main and the current Codex head **still does not dispatch ordinary native-look NEXT button input** through `PBg` ID3 / `0x432190`; real `PResults`, inbox and 1ST/RES formation click paths are missing. The latest Codex `original_management_next.py` provides source bitmap/caption/hover only. This remains the priority P0 functional defect; the native lookup filter does not by itself close Gate13.

## D. Minimum handoff and remaining original-source questions

1. **Codex-only implementation:** wire source-qualified native NEXT physical control acceptance and original conditional game path, then extend the *bounded* schedule projection only with source-verified Event payload flags, wrapped Event source predicate, manager reference identity and deferred update semantics. Avoid unconditional day increment and arbitrary absolute-date sorting.
2. Audit original payload `+0x44` bit `0/5/6` producers and meaning, payload `+0x14/+0x28` callback classes and possible event `+0x08` mutation, before assigning player-facing status labels.
3. Validate source eligibility and date choice with at least **two managers/clubs**, distinct calendar families, direct vs symbolic participant references and clear/linked postponed-event state. No live original Windows test was performed here.
4. Then finish PResults return-input event producer, EAMail usable panel, original 1ST/RES FORM click path and PMenu outcomes. No modern UI or gameplay guesses; retain EXACT/PARTIAL/UNKNOWN fidelity categories.

**Audit-only checkpoint. No game code/assets/saves changes, no Codex branch edits, no CI or Windows acceptance. Gate13 remains OPEN; Gates14–17/full original Windows11 release remain INCOMPLETE.**
