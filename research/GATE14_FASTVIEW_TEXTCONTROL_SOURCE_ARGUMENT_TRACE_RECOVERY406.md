# Recovery 406: source-closed generic TextControl argument boundary for FastView score/table

_8 October 2026 KST. Independent Gate-14 original-source research work-ahead; earliest incomplete validation gate remains Gate 13._

## Canonical evidence and reproducibility

Original authorized disc source: `footballmanager.exe`, extracted from Joliet root of original raw MODE1/2352 track. Verified extracted PE32 SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** against the repository-pinned canonical executable. This is the installed game's original executable evidence, not current reconstruction behavior or an unrelated crack copy.

Without Capstone in the execution image, disassembly was inspected using GNU objdump on the **verified original executable**. Reproduce privately outside Git:

```sh
sha256sum footballmanager.exe
objdump -D -M intel --start-address=0x527960 --stop-address=0x527a5f footballmanager.exe
objdump -D -M intel --start-address=0x527ba0 --stop-address=0x527be8 footballmanager.exe
objdump -D -M intel --start-address=0x6845e1 --stop-address=0x684620 footballmanager.exe
objdump -D -M intel --start-address=0x4834d0 --stop-address=0x4834d8 footballmanager.exe
objdump -D -M intel --start-address=0x64f3c0 --stop-address=0x64f3d1 footballmanager.exe
```

Bounded caller windows were also decoded at score composite base `0x51A730..0x51AB30`, LeagueTable row `0x51D730..0x51DCB0`, and heading `0x51DCB0..0x51E000`. When disassembling caller fragments, start at a known instruction boundary rather than an arbitrary byte offset; instructions from an unaligned subrange can be misleading.

## Recovered calling convention: five 32-bit constructor arguments

Canonical `0x527960` is a C++ **thiscall-like** constructor, with `ecx` holding the destination control object and **five caller-pushed 32-bit stack arguments**, as proven by `ret 0x14` at `0x527A5C`. The constructor's frame/SEH prologue has a net 0x30-byte stack depth after saved registers. Named semantic roles below are bounded by the actual consumer instructions, not guesses about the final on-screen text.

| Stack parameter at entry | Direct constructor consumer | Proven immediate role | Remaining uncertainty |
| --- | --- | --- | --- |
| Arg 1 `[entry_esp+0x04]` | `0x5279C4` loads `[esp+0x3C]` after temporary pushes; `0x5279D1..D3` forwards to `0x64F3C0`, which writes its passed value to member `+0x24` | Stored base-control configuration value | Exact semantic name/owner not yet independently closed |
| Arg 2 `[entry_esp+0x08]` | `0x5279D8` reads `[esp+0x38]`, then dereferences `+0,+4,+8,+0xC` and computes widths/heights for `0x6503F0` | Pointer to a source rectangle (left, top, right, bottom) | Original interpretation of every orientation/clip flag remains bounded |
| Arg 3 `[entry_esp+0x0C]` | `0x5279E2` reads `[esp+0x44]`, `or ... 0x8`, forwards the result to `0x6503F0` | Native control flag/bitmask with bit 3 forced on | Individual bits and color semantics not established by this step |
| Arg 4 `[entry_esp+0x10]` | `0x527994` reads `[esp+0x40]` and calls `0x6845E1` for object member `+0x40`; that helper copies a string-like source object | Source text/string-object input | EA-facing literal/format/update producer is **not** recovered |
| Arg 5 `[entry_esp+0x14]` | `0x5279B8` reads `[esp+0x48]` after an outstanding cdecl helper argument and passes it to `0x527BA0` | Selector index for one of five global font-related pointers | Meaning and selected index values for individual live rows remain unresolved |

The nontrivial stack offsets above are reconciled with helper return conventions: `0x6845E1` ends with `ret 4`, `0x4834D0` with plain `ret`, `0x527BA0` with plain `ret` and `0x64F3C0` with `ret 8`. `0x5279C8` performs an `add esp,8` for two outstanding temporary cdecl pushes. This establishes the entry argument mapping independent of inferred names from neighboring instructions.

### Exact font-pointer dispatch

`0x527BA0` reads its sole stack input at `[esp+4]`, bounds-checks it against 4 and jumps through a five-entry lookup table at `0x527BD4`. The five arms return:

| Index | Returned VA |
| ---: | --- |
| 0 | `0x87BEA0` |
| 1 | `0x87BE90` |
| 2 | `0x87BE80` |
| 3 | `0x87BE30` |
| 4 | `0x87BDF0` |

Any index greater than 4 returns null from `0x527BCE`. This proves a finite **selector-to-global-resource address mapping**, not the identities of five specific `.fnt` files or a particular visible string.

## Bounded direct FastView caller evidence

The known ScoreComposite/LeagueTable owners have at least the following **six decoded direct** `call 0x527960` sites, aligning with the existing source-trace candidate inventory. These are only calls found in the bounded windows, not a claim that the constructor has only six callers globally:

| Owner | Call VA | Third argument (native flag) | Fifth argument (selector index) |
| --- | --- | --- | --- |
| ScoreComposite base | `0x51A8C1` | Literal `0x22` | Loaded from owner-relative `[ebp+8]` |
| ScoreComposite base | `0x51A93C` | Literal `0x21` | Loaded from owner-relative `[ebp+8]` |
| ScoreComposite base | `0x51A9D2` | Literal `0x24` | Loaded from owner-relative `[ebp+0xC]` |
| ScoreComposite base | `0x51AA83` | Literal `0x24` | Loaded from owner-relative `[ebp+0xC]` |
| LeagueTable row | `0x51D8FB` | Computed in `esi` from row input/state, no unconditional literal | Literal selector index `0` |
| LeagueTable heading | `0x51DDF3` | Literal `0x24` | Literal selector index `0` |

These arguments are determined by the five immediately preceding `push` instructions and the callee's five-argument cleanup. Specifically the row/heading constructors choose the same selector **index 0**, returning global pointer `0x87BEA0`. This is a genuine narrowing of the previously unproven source font selection, though the concrete original font filename/byte identity behind that global must still be verified before rasterization.

## Explicit unresolved boundaries and next step

This source pass does **not** prove any resulting visible row/heading captions, text producer updates, font file names, 16-bit color/style alpha rules, exact draw pixel outputs, global FastView z-order, audio, 3D choreography or original match presentation acceptance. No reconstruction code or pixels were changed.

Next source-backed task: examine the canonical initializer/loaders for the five selector-global pointers `0x87BEA0, 0x87BE90, 0x87BE80, 0x87BE30, 0x87BDF0` and the row/heading arg-4 string construction/refresh producer. Prove exact font object identity and text values before enabling the static score/table controls in the port. Use the existing private tracer and preserve bounded source windows outside Git. Keep Gate 13 open until actual private Windows 11 startup-HWND/DPI receipt and menu/Squad visual/latency acceptance. This Gate-14 research is authorized independent work-ahead only, not a gate close.

## Recovery 407: reconcile earlier source-verified font-selector identities

_8 October 2026 KST. Cross-document original-source evidence reconciliation, **not** new original-executable disassembly._

The Recovery-406 five-index dispatcher is now cross-checked against two previously verified global-initializer/source-font traces. The mapping below is limited to selectors whose object loaders were already independently source-closed:

| Generic selector index | Dispatcher wrapper VA | Verified font object | Original file | Existing source evidence |
| ---: | --- | --- | --- | --- |
| 1 | `0x87BE90` | `0x9197E0` | `Fonts/Zurich_BdXCn_BT_18pixel.fnt` | `research/GATE14_FASTVIEW_POSSESSION_SOURCE_TRACE.md` Recovery 200: `0x603670` initializes wrapper; `0x6042A8..0x6042F5` loads object from literal `0x839F00`; SHA-256 `4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd` |
| 3 | `0x87BE30` | `0x8CAB80` | `Fonts/Zurich_XCn_BT_16pixel.fnt` | `research/GATE14_FASTVIEW_DIRECT_HEADER_TEXT.md` Recovery 375 correction: literal `0x839E30` at `0x6044AC`, `0x657650` loader call `0x6044F9`; SHA-256 `e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18` |

The earlier preliminary style-3 association with 18-pixel *regular* Zurich in `GATE14_FASTVIEW_DIRECT_HEADER_TEXT.md` was explicitly superseded by its Recovery-375 correction; do not reintroduce that stale mapping.

**Source limits:** selector **0** (`0x87BEA0`), **2** (`0x87BE80`) and **4** (`0x87BDF0`) have no independently source-closed font object/file mapping in this reconciliation. In particular, the LeagueTable row and heading both pass selector **0**, so neither font choice nor text pixels can be inferred from the proven 1/3 cases. ScoreComposite's four variable selector inputs from `[ebp+8]`/`[ebp+0xC]` likewise cannot be presumed to equal index 1 or 3 without owner-value tracing. Text/string producers remain unresolved for both owners.

**Execution infrastructure boundary:** private original archive still resolved and materialized from the documented Library identity, but subsequent container and Python process invocations failed with `caas.internal.errors.ClientError`, including a trivial command. Therefore no fresh executable tracing, font0 mapping, or renderer verification is claimed from Recovery 407. This is a *runtime tool failure*, not evidence that the authorized source archive is inaccessible.

**Exact next executable research:** on a healthy source execution sandbox, verify canonical PE32 SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, inspect writes/initialization for **`0x87BEA0`**, resolve its pointed font object and literal loader/path first, then source-trace LeagueTable arg-4 string initialization/refresh. Separately trace the ScoreComposite owner-relative selector inputs before choosing any source font. Avoid duplicating the already-proven index-1/3 loader traces. Until these identities and values are closed, do not enable new score/table text pixels or alter Gate-13/14 acceptance claims.
