# Recovery 541 — Original transfer Inbox first-preview is a stateful reason/RNG producer

## Source identity, provenance and original call chain

Original authorized shipped `footballmanager.exe`, 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. This is **static disassembly**, not executing the original. The original neutral Inbox PMessageRow first-click handler `0x471B80` fetches the record's virtual +0x1C string **with argument 0**, so the native `EAMPlayerAskTransferListsub` implementation enters `0x56FBA0` case0 branch `0x56FD65` and follows the recovered original body text source `0x8797A0` (EnglishEAM IDX ordinal1314, STR ID943).

Reproduce independently with:
```sh
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x56fba0 --stop-address=0x56fe68 footballmanager.exe
objdump -D -Mintel --start-address=0x66951c --stop-address=0x66953e footballmanager.exe
objdump -D -Mintel --start-address=0x471b80 --stop-address=0x471c60 footballmanager.exe
```

## Confirmed native mutation order

1. At `0x56FDB1..0x56FDB7`, the native variant0 body formatter **reads the message record +0x3C signed DWORD**, comparing it to `-1`. This is the native reason-selection state, not a plain text field. When already different from -1 it branches directly to `0x56FDF5` with the existing field in EAX.
2. Only when the native record+0x3C is -1, `0x56FDC9` calls original `0x66951C`, whose underlying RNG object at `0x66D553` is advanced with **seed = seed × 0x343FD + 0x269EC3 (32-bit wrap)**, then emits **(seed >> 16) & 0x7FFF**. These are directly visible `0x669521..0x66953D` native instructions. It is a stateful RNG step, not a deterministic string lookup or caller-supplied argument.
3. The returned RNG number is transformed by a multiplication involving native constant **7** at `0x56FDD5` and a signed multiplication by native magic `0x80010003` at `0x56FDD0..0x56FDEC`; when result is zero, code substitutes **1** at `0x56FDF0`. The exact source arithmetic can be reproduced instruction-for-instruction; do NOT label the result a specific textual reason or assume an unverified 1–7 inclusive semantic contract from this calculation alone.
4. At `0x56FDF5..0x56FDFE` it **writes the resulting reason integer back to record+0x3C**, before retrieving current user `0x4139D0` and the original body source slot `0x8797A0` (`0x56FE01..0x56FE1A`). Native `0x612FD0` then builds a typed formatter context and `0x659810` formats into `0x947AA0`; it does not return a static template as user-visible final preview.
5. The alternate `0x56FC92` (arg1, source pointer `0x87979C`, EAM IDX1315) and `0x56FBC5` (arg2, source pointer `0x879798`, IDX1316) contain parallel read/randomize/store branches using the same record+0x3C, and all **three independently SHA-verified original EnglishEAM IDX positions 1314,1315,1316 reference STR ID943**. Same source text is not evidence that the other variants have identical contextual effects or UI actions.

## Consequences for current reconstructed player route

Existing merged PR634 strict source template and PR635 `OriginalEAMNativeRowSource.source_original_unexpanded_preview_template` correctly expose an **uninterpolated source-only** value and explicitly do NOT mimic first-click formatted body. This is essential because **the native visible preview is not a pure read**: if the original record reason is unset, the first body generation writes the chosen value and consumes RNG. A source-only projection must never trigger the RNG early or mutate a player record merely for preparing row art. Conversely, a future real first-click preview must preserve exactly this native mutation at the source-qualified timing, including durable record field/state and save/reload implications. There is no verified live engine-native typed reason field in the current stage; do not map to an arbitrary modern numeric field or random library.

**NEXT P0:** recover native `EAMPlayerAskTransferListsub` constructor +0x3C initialization and the corresponding modern delivered-record persistence mapping; identify exact reason phrase dispatcher and native typed name/user formatter (specific `0x612FD0` object vft and `0x659810` substitution), then integrate FIRST-CLICK stateful original body creation + original preview bitmap at screen (246,343), text control (252,349,520,175), exact palette/clip, read flags and modal/Escape return. This must be tested across first/second click, save/load, multiple human managers and no-RNG-replay. No native original process was launched or Windows 11 GUI tested. Gate13–17 remain OPEN.
