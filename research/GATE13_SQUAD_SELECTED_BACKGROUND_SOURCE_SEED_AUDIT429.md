# Recovery 429 — missing Squad selected-background resource and final-vtable trace coverage

_9 October 2026 KST. Read-only original-behavior audit of main `1f3664e9e1ce51276087711e4e18a50fc5018822` and Codex implementation head `cbbb15d9242883f2f5185a002b0a5e7443a53ba1`. No implementation, source-original execution, source asset import, save/schema/GUI change, or gate closure._

## New confirmed reconstruction/resource facts

1. **The only imported stats image in the Codex branch's `original_assets/source/FM2001_Art/Coaching/stats/` is `stats_grid_disabled.444` (12,324 bytes).** GitHub's actual directory listing confirms `stats_grid.444` is **not** imported there. This is a bounded repository observation, not a statement that the canonical original disc lacks the file.
2. `reconstruction/original_squad_top_controls.py` defines only `SQUAD_FIRST_GRID_PATH = 'FM2001_Art/Coaching/stats/stats_grid_disabled.444'` and expects native image geometry **729x16**. `build_fresh_squad_top_render` crops its first **328x16** pixels and repeats the *same* decoded PNG at all 20 y origins for each first/reserve list. The `OriginalSquadTopResources` data type has exactly one `first_roster_grid` field, with no enabled/selected/native-frame alternative or per-row state.
3. The Codex 9 October handoff independently records original `stats_grid.444` loader `0x5FBE64`, raw handle `0x943030`, wrapper `0x943010` via `0x5FBEB0`, and crop (0,0,328,16), plus a distinct `0x5F9A94/0x5F9AE0/0x943FD0` crop (239,0,89,16). These are **genuine original-loader/geometry leads, not proof of a highlighted player row**. `blue_toggle.444` is already imported under `Coaching/squad` but the broader original-source trace identifies multiple non-general-Squad owners, so using it as a substitute remains disallowed.

**Classification:** **CONFIRMED present-port resource and state-layer gap; UNRESOLVED original selection frame/paint mapping.** The original file likely has relevance because of its loader and crop, but the exact owner, compositing z-order and selection-controlled dispatch must be proven before source import or rendering.

## New diagnostic impediment: existing source tracer does not seed the final row class

`reconstruction/gate13_squad_source_trace.py`'s `SQUAD_VTABLE_SEEDS` currently contains only:

- `CBasePlayerList`: `0x7C5BC8`
- `FormationText`: `0x7C5700`
- `PSquadPitch`: `0x7C54A8`
- `PSquadScreen`: `0x7C5CA4`

It **does not include `PSquadPlayerRow`'s final vftable `0x7C57BC`**. Its default `--vtable-slots 24` option increases entries *per existing seed*; it does not add another seed. Running the documented CLI unchanged therefore cannot enumerate the requested final player-row vtable. This is a **CONFIRMED tool coverage limitation**, not a defect in the source executable.

The module's `squad_trace_report(pe, ..., vtable_seeds=...)` API already accepts custom `(label, VA)` seeds as an argument. **No repository/code change is required for a private analyst run**: after checksum-verifying canonical `footballmanager.exe` (expected SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`), call this existing Python function in the trusted private work environment with `vtable_seeds=(("final PSquadPlayerRow", 0x7C57BC),)`, optionally `with_disassembly=True`, and store evidence JSON **outside Git**. `screen_vtable_candidates` emits sequential pointer candidates only; confirm section membership, MSVC RTTI, final constructor installation, actual reachability, slot invocation, parent transforms and producer/read data flow before labeling any original effect.

Follow these existing independently recovered original anchors **in that order**: `0x4B6E80` base constructor -> final `0x4B6ECC` vtable overwrite; `0x443E70` texture wrapper retained at row child `+0x2C`; `0x4B56B9 -> 0x4B7FD0` list setup/owner transforms; the `0x5FBE64` candidate image wrapper and any exact native selection/hover/animation state transitions. Avoid conflating the final `0x7C57BC` with the intermediate `0x7C457C` base object.

## Separate original persistent lineup state is **not** a blue-background mapping

`reconstruction/original_squad_row_style.py` proves another distinct native state family:
- first-team active/substitute predicates `0x417EE0/0x417F00`, `DBRPlayer+0x14` bits `0x10/0x20`;
- reserve active/substitute predicates `0x417EA0/0x417EC0`, `DBRPlayer+0x174` bits `0x01/0x02`;
- `0x5D6C50` uses them in fixed priority for **name text RGB**; it is explicitly not evidence of the row-image selection state.

Neither those mask values nor native 4218E0 lineup-membership codes establish a selected blue background. A future trace may test whether texture updates *read* these masks, row focus/press bits or another flag, but may not simply assume a mapping.

## Current blocker and continuation

A minimal `container.exec` process failed **before executing** with `caas.internal.errors.ClientError` in Recovery 429. The authorized ZIP remains identified in ChatGPT Library, and its temporary materialization was demonstrated in Recovery 425. This is a command execution blocker, **not** proof of missing original bytes. No new original hash/disassembly, tests, original game launch or Windows 11 acceptance were performed.

**Exact next:** privately decode the final player-row vtable with custom `vtable_seeds`, then the actual `+0x2C` texture object ownership and selected-state producer. Only after original evidence settles per-row resource/frame/composition semantics can Codex integrate original blue backgrounds. Then proceed to EAMail `0x65` factory dispatch/RTTI and complete PMenu input/frame-timing comparisons, always preserving original behavior. Gate 13 OPEN; Gates 14–17 and full Windows 11 release unverified. This worker remains **audit_only**; Codex implementation branch untouched.

_This is an isolated audit checkpoint to remove ambiguity from the next original-source investigation, not an implementation instruction, and dispatches no CI._
