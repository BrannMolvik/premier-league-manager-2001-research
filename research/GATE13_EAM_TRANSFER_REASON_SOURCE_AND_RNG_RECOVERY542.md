# Recovery 542: native transfer reason PHRASE selector and exact CRT mapping

## Authenticated original evidence

Original privately stored disc-root `footballmanager.exe` 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Original extracted `EnglishEAM.idx` SHA-256 `bd0e2b804f1ce85011509ff828cdc70f2409509537ec61a012d1fa0175932367` and `EnglishEAM.str` SHA-256 `98387ef673e87a02cf2cab7349770a4415f29fd381877b603922302c3e3f174f`. Actual original bytes examined locally, without launching original code, from the user's authenticated private source.

### One original player journey

Original selected user opens delivered `PEAMail` through header/PMenu, first neutral selects original `PMessageRow` and calls record virtual +0x1C(argument 0). Original transfer request `EAMPlayerAskTransferListsub::0x56FBA0` takes 0x56FD65, reads record+0x3C, conditionally consumes exactly one original CRT output when -1, writes the reason once, then calls original dynamic formatter. The template's `{PHRASE:PLAYERASKTRANSFERLISTREASON}` token is installed as a native `0x7D6200` processor with source token literal `0x8327FC`. The callback `0x60FE40` reads the stored reason (native processor +0x10), selects exactly one of seven source text slots, formats its source text and copies the resulting fragment.

### Exact seven source slots

Original `0x60FE40` requires reason in [1,7] before native jump table `0x60FEF4`. Branch targets 0x60FE58, 0x60FE61, 0x60FE6A, 0x60FE73, 0x60FE7C, 0x60FE85, 0x60FE8E access native language-slot pointers starting 0x87A70C and decreasing 4. Original `englisheam.idx` loader maps slot `0x87AC28 - 4 * ordinal`, hence these are IDX ordinals **327–333**. SHA-verified actual `EnglishEAM.idx[327..333]` maps STR IDs **326–332**, each a different full original player reason. The exact words are read at runtime from the existing shipped original `EnglishEAM.str`, rather than duplicating or fabricating phrase text. Values 0, -1, 8+, boolean/string values cannot be promoted to a valid reason by the modern port.

### Crucial arithmetic, independently challenged

Original `0x66951C` updates shared CRT LCG `state=(state*0x343FD+0x269EC3)&0xFFFFFFFF` and returns `rand15=(state>>16)&0x7FFF`. Original `0x56FDD0..0x56FDF9` takes that 15-bit result, multiplies by 7 and uses signed multiply-high by **0x80010003**, addition, signed shift 14 and sign correction, then substitutes 1 for zero. A separate original-instruction emulator over **every 0..32767 input** proved exact equivalence to `max(1,(rand15*7)//32767)`. This is **not** a uniform seven-way choice. Complete-source output histogram: reason1 9362, reasons2–6 each 4681, reason7 **one** (the input 32767). Do not replace by Python `randrange(1,8)`, by `rand15 % 7`, or by division by 32768. The test independently implements the signed magic computation and compares all 32,768 results, not an assertion derived from the simplified port function alone.

### Port scope and still missing

Source-backed `original_eamail_language.py` now returns the SHA-checked native reason string when a **preassigned** valid reason exists, and exposes a pure 15-bit value->reason helper with **no RNG draw or state change**. Actual real selected manager delivered `OriginalEAMNativeRowSource` may read the original reason string only from a previously assigned `original_preview_reason_native_i32`; -1 remains None and is never randomly filled during an innocent row paint, sort or snapshot. Tests exercise source IDs, byte identity, arithmetic exhaustive range/counterexamples, real live delivered rows, read-only behavior, absent and corrupt reasons. The record's native reason and internal save roundtrip were separately source-integrated in PR636.

**Original-process observation:** NO. **Source original proof:** YES for the bounded reason callback/selection. **Reconstruction tests:** PR exact-head CI required before merge. **Port visible preview:** NO. **Windows 11 GUI acceptance:** NO. Gates 13–17 remain OPEN.

**Next P0:** establish which *shared stateful* native CRT RNG instance feeds 0x66951C at original first-press timing and how to preserve it in the live controller. Source qualify manager (current DBRUser+0x5B4)/player (record+0x40) typed formatter `0x612FD0/0x659810`, source paragraph markup and native font RGB/clip. Integrate ONE honest complete first-click preview in actual Tk host using verified artwork at screen (246,343) and preview eCText child at (252,349,520,175), then message status/modal/ESC/return. Continue entire R1 match modes, season/countries/leagues 2–6 humans, Gates13–17 release audit. No original executable execution was authorized or performed.
