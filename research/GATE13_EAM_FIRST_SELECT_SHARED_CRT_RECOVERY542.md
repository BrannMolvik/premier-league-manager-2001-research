# Recovery542: original neutral first Inbox row click, one-shot reason and shared CRT state

## Original source and complete native first-select path

The authorized original `footballmanager.exe` is 4,714,541 bytes with SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. `PMessageRow::0x471B80` with event argument 0 and another selected row pointer enters native first selection (rather than the selected-row detail modal `0x471270`). Original selected row code invokes delivered record virtual +0x1C with zero before refreshing preview; `EAMPlayerAskTransferListsub::0x56FBA0` case0 at `0x56FD65` reads native signed reason at `record+0x3C`. Its native constructor `0x56FB3C` stores -1. If -1, it makes one original CRT `0x66951C` draw, converts `rand15` with original signed multiply-high arithmetic `max(1,(rand15*7)//32767)` and writes chosen 1..7 to the same native record before dynamic message formatting. Once assigned, the handler skips the draw. Source phrase callback `0x60FE40` maps this reason to original exact `EnglishEAM.idx` entries327..333, as proven in GATE13_EAM_TRANSFER_REASON_SOURCE_AND_RNG_RECOVERY542.md. Original CRT `0x66951C -> 0x66D553` reads/writes a thread-local 32-bit RNG state, not one per message. It matches the `MsvcCrtRng.rand15()` stream used by the existing reconstructed controller for ordinary single-thread gameplay.

## Source-bounded integrated vertical slice

In `OriginalDeliveredEAMailboxes.source_first_transfer_preview_reason`, explicitly require an actual registered owner, a positive delivered native serial, exactly original transfer subtype, a qualified first-neutral-row selection, and the **existing** `MsvcCrtRng`. Only a current `-1` record consumes one `rand15()` and is immutably replaced in that user's delivered list with its chosen native signed reason; selecting it again does not draw. No pending queue, other human/manager, general mailbox/status or unsupported class participates.

The ordinary `OriginalGameTkHost._press_original_eamail_row` executes this one-shot source mutation only AFTER the existing original neutral selector `original_eamail_neutral_row_dispatch` accepts first selection, and BEFORE storing selected row and repaint. The original screen is still missing actual formatted body/preview and `PEAMMessage`; this implementation does not fake either. It neither adds a modern command/button nor makes any new inference about final source colors, links, ESC behavior or original binary save bytes.

## Negative and alternate evidence

Tests distinguish an out-of-native-row click, unqualified neutral activation, wrong source user, invalid node, pending/foreign manager, valid selected row, same-row modal fail-close, selected-row switch and return, single shared stream advancement per *new reason*, and modern JSON save/reload after a reason has been assigned. The separate source test independently checked all 32768 possible CRT inputs against the original native magic multiply. A different underlying original event thread could have another native CRT TLS block, and other source draws may alter the state before this click. The current ordinary one-window Tk route assumes the verified standard single-game GUI thread; **Windows original-process observation and interleaved native event baseline remain unverified**.

## Acceptance matrix

- Original static source proof: YES, bounded native first neutral click, reason and CRT state owner.
- Reconstruction implementation/test: PR exact-head Gate13 test required.
- Original-process observed gameplay: NO, original EXE not executed.
- Native displayed preview with body/paragraph colors/clip: NO.
- Original detail/action/ESC/return: NO.
- Genuine Windows11 mouse/save/playability acceptance: NO.

Gate13–17 remain OPEN. This shared-RNG interaction must be independently reviewed before a risky merge under WORKER_SCOPED_SOURCE_FIX_AUTHORIZATION.md; passing CI alone does not provide that review.

**Next:** original specific manager/player dynamic template formatter 0x612FD0 / 0x613040 / 0x6130A0 and 0x659810, full eCText 0x5D75B0 paragraph/color/clip, visible authentic preview original enabled/disabled 532x187 asset at (246,343) and body text child (252,349,520,175), all result/read/modal/ESC transitions, then R1 all match modes, all original shipped nations/leagues and 2–6 humans, Gates13–17 and genuine Win11 acceptance.
