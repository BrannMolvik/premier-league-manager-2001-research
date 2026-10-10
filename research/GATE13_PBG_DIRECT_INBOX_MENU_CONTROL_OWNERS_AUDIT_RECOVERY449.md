# Recovery 449 — source-verified direct EAMail/PMenu header child IDs and coordinates

_9 October 2026 KST. Continued independent AUDIT ONLY P0 original-functionality sweep after source-confirming derived LeagueMatch clone/scheduling. Codex exclusively owns reconstructed gameplay implementation and Windows11 tests._

## Proof owner, source, reproduction

Current main began at `337d03bba66462916c4d206fb8832fdb2abe2084` and advanced through two research/ledger evidence commits during this recovery. Codex current head `0ae745d1b56f45cade460f03cd893849a2f53b45` changed original header/Squad font ownership, not menu/NEXT/EAMail integration. Canonical original privately held `footballmanager.exe` size 4,714,541; SHA256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** independently rechecked this recovery.

Reproduce original instruction chain using `objdump -d -M intel` with ranges `0x430928..0x4309C9`, `0x431850..0x43188E`, `0x4313B0..0x431416`, `0x432690..0x432707`. Original raw executable/disassembly remains private outside the repo.

## Exact original shared PBg direct-header controller contract

The original **`PBg`** management background creates a *three-control* root action collection. These are not PMenu child-list IDs. Each event/control child is registered through its original vtable +0x08, receives the owning `PBg` object, and is associated with the native `PBg::0x432690` parent callback (`PBg` vft 0x7BEE8C +0x10). Original root controls:

| Original owner field | Setup / instruction | ID and original action | Screen origin from native push arguments | Original dimensions/uncertainty |
| --- | --- | --- | --- | --- |
| **`PBg+0x49C`** | `0x43092B..0x430957`, `0x431850` | **ID1** → `PBg::0x432690` case `0x4326D6` → direct EAMail PMenu factory `0x482BF0(0x65)` (only if inbox not already top/active) | **x=558, y=0** | **40×95** native input rectangle: `back_3.444` width40×380 (4×95 frames); wrapper `0x943B10` +0x14/+0x18 feeds `0x943B24/0x943B28` to helper `0x431850` |
| **`PBg+0x4E0`** | `0x43095F..0x43098D`, `0x4313B0` | **ID2** → `PBg::0x432690` case `0x4326AE` → popup PMenu stack management, subject to original active-panel guard | **x=599, y=0** | **100×95 composite input rectangle**: `0x4313B0` width is `0x943AA4 + 0x943AE4 = 30+70`; `back_4_anim.444` width30×4845 (51×95 frames) plus `back_4.444` width70×380 (4×95 frames). Height wrapper `0x943AA8=95` |
| **`PBg+0x524`** | `0x430992..0x4309C9`, `0x5D3900` | **ID3** → `PBg::0x432690` case `0x4326A4` → native NEXT/MATCH progression `0x432190(0)` | **x=`0x2BC=700`, y=0** | Source-verified original `back_5.444` bitmap control (100×95 original crop), already tracked in `reconstruction/original_management_next.py` |

### Exact original art ownership closes all three static control hit rectangles

The executable's original resource path literals are **`0x837A38` `FM2001_Art/Generic/Background_buttons/back_3.444`**, **`0x837A6C` `back_4.444`**, **`0x837AA0` `back_4_anim.444`**, and **`0x837AD8` `back_5.444`**. The loader/wrapper constructor code maps:

- `back_3.444`: loader `0x5FA570`, wrapper `0x5FA5C0` = **40×95 per native frame**; disc Joliet LBA105245, 5,932 bytes, SHA-256 `f369e73c2a7f9149661d66cf3c781ddc8eabf01f80ef924b423d46d57cf628e6`.
- `back_4.444`: loader `0x5FA600`, wrapper `0x5FA650` = **70×95 per frame**; LBA105248, 5,476 bytes, SHA-256 `710016aa4f9c2d5a04580ba48e2449882040482d231b875726203836b8cb42bb`.
- `back_4_anim.444`: loader `0x5FA690`, wrapper `0x5FA6E0` = **30×95 per frame**, separately animating at the left of the fixed 70px PMenu art; LBA105251, 99,968 bytes, **30×4845 = 51 frames**, SHA-256 `867abd21e89b21c878d20777547524e8ea4a00fcc9b49524f8356b631a665f69`.
- `back_5.444`: loader `0x5FA720`, wrapper `0x5FA770` = **100×95**; LBA105300, 10,940 bytes, SHA-256 `171257f958b9fa15115476814a31de2d86bbdd2beb4767e42b3181d83e7ba605`.

Original `0x431850` reads the `back_3` crop dimensions at wrapper`0x943B10+0x14/+0x18`, so EAMail native rect is **(558,0,40,95)**. `0x4313B0` adds **`back_4_anim` wrapper+0x14 width30 and `back_4` wrapper+0x14 width70**, while using the animated wrapper's 95px height, so PMenu native rect is **(599,0,100,95)**. The NEXT rect is **(700,0,100,95)**. These rectangles are now **EXACT original-resource + executable setup facts**, though enabled/pressed/hover transitions, input acceptance and actual panel presentation remain distinct from static rectangles.

**Important correction of this recovery's interim geometry:** the 70px `back_4.444` sprite by itself is **not** the whole PMenu control; its 30px `back_4_anim.444` partner enlarges the owner to 100px. Original common `0x64F380` receives initial flag0x8018, which is not by itself a proven enabled native press state; do not infer any accepted-click behavior merely from geometry.



The native EAMail action1 is a **separate direct management-background route** to PMenu child ID0x65's PEAMail class from the nine-root/twenty-eight-child PMenu popup system. Thus a faithful user-visible game must offer the direct header inbox entry *and* the list action, not merely a partially populated PMenu panel.

## Current main/Codex source comparison and actionable missing route

Read the latest Codex `reconstruction/original_game_host.py::on_click` method at **`2287..2542`**: it has `pmenu_open_press`, Squad-row and League-Fixtures input handlers, PMenu rows; **no accepted direct header mail hit-test or PEAMail/inbox dispatch, and no native NEXT press dispatch**. Its isolated `original_management_next.py` draws source art/hover/caption without actual PBg action3. This report does **not** assert its current menu press art is wrong or that EAMail would work if only a hit box were added.

**Codex-exclusive implementation handoff:** use the now-proven original ID1/ID2 resource wrappers and exact rectangles, then source-qualify status flags and ownership before editing the original-look host. Connect source-qualified action1 through genuine PEAMail list/detail and existing selected club/messages, respecting original active-panel guard; preserve action2 existing source menu popup acceptance, and separately action3 native NEXT progression. Test all three in **ordinary mouse path** with PMenu visible/hidden, EAMail empty/populated across at least 2 managers/clubs and full Windows11 timing/return receipts.

**Bounded status: CONFIRMED control object and action IDs, x/y origins, concrete setup helpers, target factories and current missing header-mail click implementation; EXACT ID1/2 original composite hit-rectangle geometry/raster identity; UNKNOWN physical acceptance/hover and original live mailbox contents.** No asset/code/Windows process changes, tests/CI, merge or gates. Gate13 remains OPEN; Gates14–17 and verified full original-game Windows11 release remain incomplete.
