# Gate 13: live original Inbox first-selection source and implementation (Recovery 535)

## Original reference and confidence

Reused separately verified 4,714,541-byte original `footballmanager.exe` SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Source-static proof (not original game observation):
- `PMessageRow::0x46E705` constructs native 532×18 normal row wrapper `0x945E30` (verified `FM2001_Art/Generic/EAMail/text_grid_nor.444`).
- Neutral event `PMessageRow::0x471B80` compares `this` with selected native `0x87675C`. A different row saves new pointer, calls `0x470B40` (selected wrapper `0x945DF0`, `text_grid_sel.444`), makes three child controls visible and updates preview `0x471620`. Switch first deselects the prior row via `0x470B90` (normal wrapper and hidden children).
- A second event on the same native row goes to `0x471270` modal with record-specific dispatch, then `0x472770` delivered view rebuild and reset. Its action labels/returned choice/ESC transition are not accepted yet; no port mutation on re-press is permitted.
- PEAMail panel native (0,148,800,530), CMessageList offset (233,30,545,160), eight source row slots each (233,178+20×i,532,18). Half-open screen hit acceptance is a bounding rectangle on displayed `PMessageRow` owners, not free clicks anywhere in list, header, or queued events.

## Port slice

Normal `OriginalGameTkHost.on_click` now checks source-owned current delivered Inbox viewport for displayed native rect before unrelated grid handling. It calls the existing source-verified neutral callback helper `original_eamail_neutral_row_dispatch`, and first click retains selected row ordinal/identity, redraws with exact original selected EA444 image loaded using the same verified quantization/decoder, then a switch deselects the old row. The host clears selection on rebuilding a different PMenu panel/return; a disappeared row is not reusable. Popup-open input is not stolen from PMenu.

Reclick preserves actual mailbox and refuses to simulate an unverified modal, unread flag, reply or other game action; it is an explicit known player-workflow gap, not completion. Original message text glyphs/colored markup, preview text, status/highlight/hover/icon sprites, native choice/Escape, scroll/filter controls, physical Win11 input and original-process observation still absent.

## Regression and acceptance

New tests exercise ordinary source TeamSelect→selected manager→PMenu→real delivered rows and host click method; native screen corner/end/gap hit bounds; exact selected image role vs normal; switching; repeated press not mutating delivered mailbox; reject unavailable selected art or stale selection. Tests/mock/source projection are NOT a source-original runtime playtest. Keep Gate13 and 14–17 OPEN until full GUI original-journey checks.
