# Recovery531: producer-time native EAM player-association lifecycle persistence

**12 October 2026 KST. Gate 13 OPEN.** Based on authenticated static analysis and [producer source audit](GATE13_EAM_PLAYER_ASSOCIATION_PRODUCER_SNAPSHOT_NATIVE_RECOVERY531.md), native `0x5CE660` captures signed `DBRPlayer+0x72` at **message creation** into its kind2 descriptor+8. Source player +0x72 can change after creation; never use current `player.club_id`, `loan_club_id` or sender key during Inbox display to infer the historical descriptor word.

This change introduces one explicitly qualified, **optional** signed 16-bit `verified_native_association_word_at_creation` datum on:
- `PlayerTransferRequest`: accepts only actual signed shorts or `None`. Caller alone must prove the current native +0x72 mapping *at producer time*.
- `OriginalPendingTransferEAMQueue`: transports that identical word with the original MPM envelope and persists through its modern snapshot.
- `OriginalDeliveredEAMailboxes`: copies the request snapshot into the frozen delivered EAM record at native due dispatch and saves/restores it separately from pending state.
- `internal_save.py`: preserves the same optional word on outstanding actionable transfer requests. Legacy modern saves lacking the field still restore `None`, never reconstruct a historical value.
- Targeted regressions test all signed limits, typed invalid and spoofed values, old records, unknown keys, producer-time snapshot persistence after a synthetic intervening live transfer/loan, pending->due->delivered and two independent save restore paths.

**Explicit scope limit:** `GameState._retain_player_transfer_request` does not yet supply this optional native field, because a globally coherent +0x72 runtime mirror through original transfer/loan/youth mutations is **not yet source-qualified**. Existing delivered mail thus carries `None`; this is provenance-correct plumbing, **not** a now-renderable Inbox or claim of source-verified club text, GUI or an original save file. Unverified positive-association text remains blocked, and legacy input is never rewritten as if native source-verified.

**Next P0:** Source-map +0x72 mutation ownership against actual reconstructed transfer/youth/loan phases, then provide independently qualified producer-time signed value in `GameState._retain_player_transfer_request` and add a genuine integrated port roundtrip regression with changing clubs after producer but before delivery. Resolve native `0x40DA70` club text and `0x9844D8` extra fragment, localized date `0x64D150`, native row fonts/sprites/status, two Inbox menu entry routes, row/detail/choice/Escape return, >16 source sorter. Gates13–17 and native Win11 visible acceptance remain unpassed.

**Source evidence:** verified original `footballmanager.exe` 4,714,541 bytes SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; private static disassembly only. No original binary committed or run.
