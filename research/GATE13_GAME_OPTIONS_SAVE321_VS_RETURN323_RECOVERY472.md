# Recovery 472 — current Game Options: Return works, Save still does not

10 October 2026 KST. Audit only. Canonical main 7376fec54016dffdd892a71cd9b93679f687174a; current Codex b36276e4eaf987a9e8eb59a1d78e8f3e9ada7bbb. No code, saves, original binary, tests or CI changed by this worker.

## Versioned native-source comparison

- **Child 0x323 Return to Main:** Original PMenu 0x47C928 calls PStartMenu 0x4C3280 and returns a NULL factory result, not a content panel. Latest Codex implements return_to_pstartmenu, preserves gameplay session and supports Continue. Its own FakeTk/withdrawn Windows-Tk tests report success, but normal physical-mouse Windows acceptance remains unverified.
- **Child 0x321 Save Game:** Distinct original 0x47C889 -> PSaveGame constructor 0x4802F0 with final RTTI vtable 0x7C34D0, native 760x500 panel. PSaveGame event6 invokes source save writer 0x50D9B0, creating/overwriting numbered games/%d.sav slots, and event7 invokes 0x50E1F0 to delete and compact numbered slots using DeleteFileA/MoveFileA. In current Codex original_pmenu_activation.py this child still maps to generic open_panel; original_management_presenter.py builds only Squad 0xCE, League Fixtures 0x25C and Tables 0x25A and raises for 0x321. Thus ordinary MENU Save is **not implemented**, even though Return works.
- **Child 0x322 Settings:** Original 0x47C8DD constructs a distinct object through 0x46A120. The current generic unsupported panel is not a source-approved excuse to introduce modern Settings.

Historical original source provenance: GATE13_SAVE_GAME_PSaveGame_NATIVE_OBJECT_AUDIT_RECOVERY453.md, GATE13_PSAVEGAME_NATIVE_EVENTS_SAVE_DELETE_SLOTS_AUDIT_RECOVERY454.md, and GATE13_PMENU_ALL_28_NATIVE_DISPATCH_AUDIT_2026-10-09.md. Original root footballmanager.exe 4,714,541 bytes, SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3, was independently hash-gated in those prior recoveries; current trivial container execution still fails caas.internal.errors.ClientError. No new PE trace or original Windows window performed here.

## Why backend internal saves do not close the GUI gap

Original 0x50D9B0 serializes manager-owner data using 0x413E20 and iterates all registered original users through count 0x8755E4. Latest Codex internal_save.py has a different modern versioned format, one nullable HumanManagerState, and two source-specific pending mail lists, with no delivered per-manager EAMail mailbox. Original native save *byte* layout for user+0x6B4 remains UNKNOWN. Do not require identical binary serialization in a compatibility port without proof, but do require faithful persistent game behavior and genuinely playable normal Save/Load controls.

## Codex-only acceptance

Preserve fixed 0x323 Return/Continue. Integrate actual child 0x321 panel and native slot selection, guarded create/overwrite/delete/compact/save/load and original return/keyboard actions. Verify temp-directory roundtrips and two distinct club users without touching actual user saves, then prove multiuser/mail persistence and real Windows11 normal mouse acceptance. No silent saved status, fabricated generic file picker or conflation with Return-to-Main. Source modal confirmation behavior still unresolved and must remain qualified.

Classification: exact historical original source identities, confirmed newest Codex branch UI omission, conditional internal-save scope risk, unknown original native save byte layout and Windows UI parity. Codex sole implementer. Gate13 OPEN; Gates14–17/full Win11 original-scope release incomplete.
