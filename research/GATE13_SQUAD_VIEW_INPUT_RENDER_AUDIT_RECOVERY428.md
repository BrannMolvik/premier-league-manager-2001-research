# Recovery 428 — missing live Squad view-button input and alternate-view pixels

_9 October 2026 KST. Audit-only crosscheck of original-source research and Codex reconstruction at `cbbb15d9242883f2f5185a002b0a5e7443a53ba1`, against main `ff7a7701749ce0c8455de9ae15838dbe0d0a69b7`. **No implementation**, no Codex branch edits, no binary extraction/source-original launch, and no tests or CI dispatched._

## CONFIRMED: the original has three Squad view controls and container transitions

`research/GATE13_SQUAD_RESOURCE_CORRELATION.md` traces `PSquadScreen` constructor/setup to controls 3/4/5 and original event handler `0x4B8E70`, with these PSquadScreen-local locations and native outcomes:

| ID | Original text | PSquadScreen-local origin | Source-backed owner transition |
| --- | --- | --- | --- |
| 3 | `1ST & RES` | `(37,92)` | first-team list left, reserve list right; second-list visible, pitch not visible |
| 4 | `1ST FORM` | `(113,92)` | first-team list left and pitch visible at index 0; second-list hidden |
| 5 | `RES. FORM` | `(189,92)` | reserve list left and pitch visible at index 1; second-list hidden |

`reconstruction/original_squad_resources.py::SQUAD_VIEW_TRANSITIONS` represents exactly those *post-acceptance container* transitions. It explicitly does **not** map a pointer/key event to them. The native panel origin y=79 gives screen button top y171 for all three, and the original imported button art has frame size 73x25; `test_original_squad_top_controls.py` separately asserts control 3 `(37,171,73,25)`. These coordinates alone do not prove original pointer acceptance or press/hover timing; do not implement a guessed click-to-event mapping without tracing the native control's input virtual.

## CONFIRMED reconstruction limitation #1: no live mouse path to Squad view action

- `reconstruction/original_management_presenter.py::source_accepted_squad_view_transition` accepts one control ID, builds the panel snapshot, then commits `self.squad_view_control_id`; it deliberately accepts **no mouse coordinates**.
- `reconstruction/original_game_host.py::apply_source_accepted_squad_view` calls that method and redraws, but its docstring explicitly says **no modern pointer/key event is mapped**.
- Read-only inspection of `original_game_host.py` found that `apply_source_accepted_squad_view` is defined once, without a live caller; `on_click` checks menu-popup open, Squad row drag, fixture controls, PMenu candidate rows, and League Fixture grid, but does not dispatch control ID 3/4/5 from Squad top-button pointer presses.
- **User-visible consequence:** the three initial button bitmaps render, but their ordinary pointer route to switch roster/pitch presentation is not integrated. The programmatic method is not a usable substitute for the original in-game event. Do not mislabel existing source-button art as working controls.

## CONFIRMED reconstruction limitation #2: permitted container transitions with withheld visuals

- `_draw_squad_top_controls` has an explicit `if transition.control_id != 3: return 0`. In that case, **all** of the top-control overlays are withheld, including the common buttons, paired roster chrome and title from `build_fresh_squad_top_render`.
- `_draw_squad_rows` has the same guard and withholds player rows for controls 4/5. Existing code comments explain that formation/pitch membership and post-event button pixels are not source closed.
- `test_original_game_host.py::test_post_transition_squad_pixels_fail_closed_until_their_state_is_proven` asserts rendering control 4 produces zero images; `test_original_management_presenter.py::test_source_accepted_squad_view_transition_tracks_only_proven_container_state` exercises 4 and 5 only at the abstract presenter layer. Therefore this is **deliberate fail-closed incompleteness**, not proven unintentional new regression and not evidence that a Windows user clicked a mapped formation button.
- **Consequence for release:** even once original input is wired, enabling those transitions without source-backed art/rendering would result in blank Squad panel layers for those views. Correct remediation must preserve native alternate-view container visibility, pitch geometry, first/reserve membership, full top-button states and redraw order rather than merely routing a click to the presenter.

## Distinct unresolved original-selected-row issue

The separately confirmed `build_fresh_squad_top_render` currently repeats one disabled `stats_grid_disabled.444` crop across 20 rows. The **original's selection-dependent blue background** still requires a hash-gated original executable trace of final `PSquadPlayerRow` vftable `0x7C57BC`, its draw/update/mouse/selection producer and `0x443E70` child texture `+0x2C`. Do **not** conflate the Squad view-button selected frame (native control 3 vs 4 vs 5), player-name text color predicates, per-row highlighted background, and pitch FormationText animation frames; these are different original owner/state contracts.

## Source access blocker and exact next steps

This recovery independently attempted both a minimal `container.exec` shell command and a private `python.exec` command; both failed **before execution** with `caas.internal.errors.ClientError`. Original archive location persists in Library per `research/ORIGINAL_SOURCE_LOCATOR.md`, but no executable hash, original disassembly, new renderer test, or real Windows 11 playtest was performed. Continue source work only once private execution is available, beginning with SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Recommended audit ordering to Codex: (1) source-close final populated row `0x7C57BC` selected-background wrapper and exact blue pixels; (2) source-close original button-pointer acceptance and frame transitions for IDs 3/4/5 as distinct from abstract `0x4B8E70` container actions, then implement original-look alternate panel pixels when authorized; (3) separately trace original EAMail `0x65` factory (derived/unverified low byte-table candidate `0x47CA04`) and live inbox; (4) original PMenu animation input/timing. Keep Gate 13 OPEN and Gates 14–17/Windows 11 full-scope release unverified. ChatGPT autonomous role remains **audit_only** and Codex remains implementation owner.

_This report is intentionally a factual audit checkpoint rather than a CI or original-runtime result._
