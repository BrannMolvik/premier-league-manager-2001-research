# Gate 13 Windows playtest corrections — 3 October 2026 KST

Parallel branch: `codex/gate13-windows-closure`, based on canonical
`608e4f9168939c08ddffd90f5d6fb112b5d2724e`. The independent continuous
worker and `agent-runtime` are unchanged.

## CONFIRMED: spaces are advances, not visible glyphs

Canonical executable SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Native renderer `0x657280`, specifically `0x657389/0x65738D`, compares the
input byte with `0x20` and bypasses glyph draw `0x6570F0` for space. Width
and pair-spacing advancement still occur. Original STR labels already contain
ordinary spaces. The space record points at atlas x=0, whose pixels are not
blank; rasterizing that record caused the observed apparent `!` separators.

`EAFont.render_text_alpha` now skips only space painting, preserving source
strings, advances, kerning and genuine `!` glyphs. Corrected 20px menu mask
digests are pinned in tests. Synthetic regressions exercise leading/trailing/
internal spaces, nonblank space atlas pixels and real exclamation painting.

## CONFIRMED: TeamSelect action captions

Setup `0x4D885F..0x4D891F` binds event `0x29` to global `0x98211C` and
event `0x2A` via `0x4D9270` to `0x982124`. The complete sequential English
loader binds these to IDX **2487** and **2485** respectively.

| Event | Exact English caption | Font | Width | Line origin | Clip/control |
| --- | --- | --- | ---: | --- | --- |
| `0x29` | `MAIN MENU` | Zurich_XCn_BT_30pixel | 97 | `(251,301)` | `(225,301,150,32)` |
| `0x2A` | `START GAME` | Zurich_XCn_BT_30pixel | 102 | `(450,301)` | `(426,301,150,32)` |

Both use wrapper `0x896340`, source-bound by loader
`0x604600..0x604651` to the path literal at `0x839DB0`.
This **corrects** the earlier 20px Back/Start placement inference in
`GATE13_BUTTON_NATIVE_TRACE.md`; it does not rewrite that historical trace.
The native line height is 32; style is `0x2000`, offsets zero, normal/group-2
color `0xFFFF`, group-1 color `0x0000`. Existing recovered Button frame/group
selection also selects caption color. No original RGB reinterpretation is added.

The single font was extracted with existing inventory tooling from the canonical
authorized ZIP (SHA-256 `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`),
then imported with the existing provenance importer. Font SHA-256:
`0fe5f5315006a35438d3cdca79a29e4b334ea714c76b26148b9ad0a3f666a607`.
Raw executable/disassembly/extraction reports remain private, outside Git.

## Port compatibility boundary: rejected Start

`HumanGameplayController.select_club` rejects non-Premier-League clubs before
creating a human manager. `FrontEndSession` therefore retains TeamSelect and
the chosen clubs for retry. The clean host previously caught that exception
and assigned only `last_status`, which was not visible on the canvas.

The host now displays an explicitly named **FM2001 port** error dialog, using
the actual rejection message. This is compatibility feedback, **not** recovered
original-game behavior and **not** added Conference gameplay support. A host
regression verifies visible reporting and unchanged retry state.

## Real Windows evidence (private receipts, metadata only)

| Receipt | Schema | Result | Bytes | SHA-256 |
| --- | ---: | --- | ---: | --- |
| `gate13-schema8-20261003.json` | 8 | PASS | 71613 | `14cf97fc8dc2dc672fcd050f8396cc0dc4ca31c2afaa47fc4eda4c3a25e2b61a` |
| `gate13-schema8-postfix-20261003.json` | 8 | PASS | 72432 | `a64beff49ff9cf0eeca9f8581e4f9e640eaac351427949899c35dfbded1117ac` |
| `gate13-schema8-postfix-reconciled-20261003.json` | 8 | PASS | 72432 | `a64beff49ff9cf0eeca9f8581e4f9e640eaac351427949899c35dfbded1117ac` |

All reside in `C:\Users\Brann\Documents\FM2001-audits`, outside Git.
Platform: `Windows-11-10.0.26200-SP0`. The original receipt was not overwritten.
The post-fix real Tk run verifies both action-caption contracts and native
PhotoImage dimensions, first-screen navigation, hierarchy population and the
existing explicit Squad/Fixtures/PMatchInfo/Tables bitmap loop. It is not a
pixel-for-pixel original-game comparison, nor a human recognizability judgment.

The reconciled receipt was generated after merging canonical main
`9b554eb6f9a5eae5c0b6f31205d9ed07aefaa658` into this branch. Its deterministic
contents match the first post-fix receipt byte-for-byte. The main merge preserves
the separate worker's FastView code/research/state; no Gate-14 change is part
of the PR diff against main.

Validation: final corrected-environment full reconstruction run passed **1,513 tests
with 22 expected licensed-source skips**; post-reconciliation focused/integration
run passed **67 tests with 3 expected skips**. Exact licensed menu-font tests
also pass with the canonical English source inputs. Repository asset policy
passes. Full local validation used the existing private Capstone installation
and a writable temporary directory outside Git. Initial sandbox-only failures
were missing Capstone and temporary-file fallback into the repository, not code
regressions; both prerequisites were corrected before the successful full runs.

## Closure decision

Gate 13 remains **OPEN**. Presentation separation passes. Source resource reuse
and first-screen caption geometry are substantially verified; original timing
and broader normal management presentation are not established by schema 8.
Normal fixture-cell -> linked-context PMatchInfo is still not ordinary pointer
navigation. Surrounding management pixels, owner-local popup transforms and
post-transition Squad pixels remain fail-closed. The next local source task is
the application-owned management shell/resource draw path, followed by ordinary
fixture-cell hit-testing and its secondary-context owner bridge. Neither audio
nor modern scaling nor obscure secondary panels are added as Gate-13 blockers.
