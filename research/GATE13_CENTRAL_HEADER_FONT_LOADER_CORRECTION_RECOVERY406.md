# Recovery 406 original management header font-object source correction

**Date:** 8 October 2026 KST. **Gate:** 13, original behavior reconstruction. No external Windows visual acceptance claimed.

The prior `research/GATE13_MANAGEMENT_CENTRAL_HEADER_SOURCE_TRACE.md` correctly recovered original controls, rects, club/date text producers and font-object addresses, but associated the font object with the *next* path literal following a loader call rather than the path constructed immediately **before** that call. This is a reproducible source-trace attribution error, not an intentional visual modernization.

The authorized Joliet root `footballmanager.exe` is SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Disassembly of the complete recurring font loader sequence proves that a literal `Fonts\\Zurich_...fnt` is passed to `0x5317D0`, then through string assembly at `0x40E8A0`, finally to `0x657650` with the actual font destination in ECX. The exact preceding path literal, not the following one, identifies that object:

| Native original font object | Preceding source path construction | Original loader call | Correct file |
| --- | --- | --- | --- |
| `0x8F21B0` primary Club.name line | `0x6043AA` pushes path `0x839E94` | `0x6043F2 -> 0x657650` | **Fonts/Zurich_BdXCn_BT_32pixel.fnt** |
| `0x8E4FA0` other original font | `0x604400` pushes path `0x839E70` | `0x604448 -> 0x657650` | Fonts/Zurich_BdXCn_BT_36pixel.fnt |
| `0x8CAB80` y34/y51/y68 header controls | `0x6044AC` pushes path `0x839E30` | `0x6044F4 -> 0x657650` | **Fonts/Zurich_XCn_BT_16pixel.fnt** |
| `0x8BD970` other original font | `0x604502` pushes path `0x839E10` | `0x60454A -> 0x657650` | Fonts/Zurich_XCn_BT_18pixel.fnt |

Reproduce privately with `objdump -D -M intel --start-address=0x604380 --stop-address=0x60455a footballmanager.exe`. The embedded path strings can be checked with `objdump -s --start-address=0x839e00 --stop-address=0x839f30 footballmanager.exe`. Do not commit original executable or source disassembly dumps.

Authorized original disc Joliet:
- Bold32 `Fonts/Zurich_BdXCn_BT_32pixel.fnt`: logical extent 170829, 136128 bytes, SHA-256 `27b5e4c42518bef0e000a5878939f859c2c1b1e635e4fd200752e23c468c3e36`, atlas **2422x34**, Git blob `41a200f65908ede882bce0675eae9787b94299cd`.
- Normal16 `Fonts/Zurich_XCn_BT_16pixel.fnt`: logical extent 171122, 75217 bytes, SHA-256 `e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18`, atlas **1261x17**, already present and source SHA-identical in Git.
- Bold36 and Normal18 previously imported were genuine authorized originals, but were misbound to these two particular controls; do not delete or misrepresent their provenance.

The corrected compatibility renderer still uses native `Club.name`, exact control rect `(172,1,378,32)`, two conditional match lines at y34/y51 and date at y68, raw style `0x2102` and native white color `0xFFFF`. No guessed layout/content/colors. Both the corrected source bytes and release-package identity are SHA-gated, and the generic Southport/Arsenal tests run through the same path.

**Exit boundary:** This fixes proven source font selection and does not prove the actual Windows 11 UI's size, responsiveness, startup FMV content, or overall original equivalence. Gate 13 is still open pending original Windows transport evidence and external visual/latency acceptance. Retrospective post-#482 audit needs the previous font association superseded explicitly after verified merge; no Gate-14 or Gate-17 closure.
