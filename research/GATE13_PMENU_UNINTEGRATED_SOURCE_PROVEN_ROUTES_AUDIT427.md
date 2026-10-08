# Recovery 427 — audit of source-proven but unintegrated PMenu destinations

_2026-10-09 KST. Independent audit-only source review. Canonical technical main before this checkpoint: `26af5b6ae3f9c2f885d5b877185b5f400d71bde3`; Codex implementation head unchanged at `cbbb15d9242883f2f5185a002b0a5e7443a53ba1`. No implementation, test/CI, original launch, assets, saves, merges or gate status changes._

## Confirmed source-backed identities with missing integrated destinations

`reconstruction/original_management_navigation.py` records four canonical executable factory-mapped management panels from `0x47AEC0`. Cross-check against `reconstruction/original_management_presenter.py::build_management_panel_snapshot` and the `research/GATE13_MANAGEMENT_SCREEN_EVIDENCE_LEDGER.md`:

| PMenu child | Original identity, constructor and vftable | Current integrated outcome | Classification |
|---|---|---|---|
| `0x259` Calendar | `PCalendar2k`, factory case `0x47C62B`, constructor `0x47CCB0`, TypeDescriptor `0x81CA18`, vftable `0x7C2F04` | Presenter raises `OriginalManagementPresentationError` | **CONFIRMED missing integrated route**, original geometry/assets/actions unresolved |
| `0x25A` League Tables | `PLeagueTables`, case `0x47C6D1`, constructor `0x448640`, TypeDescriptor `0x81B458`, vftable `0x7C00C8` | Has integrated presenter/partial original panel | **CONFIRMED bounded integrated route**, not full original-play acceptance |
| `0x25B` Cup Tables | `PCupTable2000`, case `0x47C67E`, constructor `0x44EC80`, TypeDescriptor `0x81BA30`, vftable `0x7C0A78` | Presenter raises `OriginalManagementPresentationError` | **CONFIRMED missing integrated route**, cannot blindly reuse league-table list and styling |
| `0x25C` League Fixtures | `PLeagueFixtures`, case `0x47C724`, constructor `0x46D470`, TypeDescriptor `0x81C550`, vftable `0x7C24B8` | Has integrated presenter/partial original panel | **CONFIRMED bounded integrated route**, not full original-play acceptance |

The native PMenu tree contains a `0x259` **title root** and distinct `0x259` **child** node. `original_pmenu_activation.py::source_pmenu_node` resolves `row_kind` and `menu_id` jointly to disambiguate them. A proposed Calendar repair must likewise distinguish root expansion from the child `PCalendar2k` factory action; `menu_id` alone is insufficient to decide the action.

**High-value implementation handoff to Codex (not authorization for this audit-only worker):** after resolving the user's top-priority original blue Squad selected-row background and EAMail/overall menu issues, use the proven four-panel factory comparison to source-trace Calendar and Cup Tables before integrating them. Preserve the original screen-specific constructors, resource/layout evidence, callbacks and save semantics. No generic fallback panel or assumed inheritance from League Tables.

## Avoid overstating the 3-of-28 limitation

Recovery 426 showed only Squad, League Fixtures and League Tables currently have presenter routes among 28 static PMenu child entries. This is a valid `build_management_panel_snapshot` coverage count. But some children (e.g. `SAVE GAME`, `SETTINGS`, `RETURN TO MAIN MENU`) may be actions/dialogs rather than full content-panel replacements; their original dispatch semantics must be independently traced. The deficit is **25 unsupported menu child actions in this integration**, not yet a proof of 25 independent missing screens. In particular `EAMail` `0x65` is a confirmed accepted-but-unintegrated user-visible inbox route, while its specific factory case remains unresolved (`0x47CA04` is only the arithmetic low dispatch byte candidate documented in Recovery 425).

## Source/acceptance limit and next exact task

A trivial local `container.exec` probe again produced `caas.internal.errors.ClientError` before any command execution. No original ZIP/executable hash, vftable decoding, dynamic GUI or Windows 11 test was performed in Recovery 427. Existing original ZIP is stored in ChatGPT Library, not considered lost. The old `research/CURRENT_STATE.md` lead still identifies Gate 13 external normal-menu/TeamSelect/Squad Windows input/visual/latency acceptance as open; Gate 17 requires complete shipped scope.

Next independent original-source audit **when execution works**: hash-verify original `footballmanager.exe` (`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`), then trace final populated Squad row vftable `0x7C57BC` and `0x443E70` child `+0x2C` artwork state before using a guessed blue selection background. Next EAMail `0x65`: verify the native `0x47AEC0` branch/byte-table case and RTTI; subsequently inspect PMenu animation `0x6527F0` tick and `0x432970` pointer dismissal owner. Classify newly decoded results confirmed/probable/unresolved. Keep implementation branch untouched, Gate 13 OPEN, worker `audit_only`.
