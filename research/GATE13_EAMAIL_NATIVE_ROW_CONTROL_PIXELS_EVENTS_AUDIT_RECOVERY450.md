# Recovery 450 — original EAMail row controls, text grids, status indicators and auxiliary actions

_10 October 2026 KST. Independent original-file fidelity audit only, continuing the source-first inbox work after Recovery449. **Codex owns reconstruction implementation and Windows 11 acceptance.** No original executable/art committed, game code/asset/save changes, CI, merge, original game process execution or gate closure._

## Checkpoint and original source provenance

Rechecked GitHub main at `e5128af2df9c7f69ece88e7cc51ffa783c74dfcd`, `research/CURRENT_STATE.md` prioritizing **original PMenu/EAMail/Squad/NEXT usability**, and `agent-runtime` (`worker_role=audit_only`, `implementation_allowed=false`). Latest Codex branch `0ae745d1b56f45cade460f03cd893849a2f53b45` is separate and remains untouched.

The authorized private original executable at `/mnt/data/fm2001_private/footballmanager.exe` (4,714,541 bytes) was SHA-256 reverified to **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. GNU `objdump -d -M intel` ranges for reproduction: **`0x46E680..0x46E884`** (row child-control registration and positioning), **`0x471B80..0x471D11`** (row select/detail/auxiliary events), **`0x470B40..0x470C3D`** (row highlight state), **`0x471780..0x4717F8`**, **`0x471FC0..0x471FEA`** (message status indicator states), **`0x471D20..0x471F63`** (real row producer), and source graphic loader **`0x5F5580..0x5F5740`**. Native object RTTI remains original `PMessageRow` vft **`0x7C266C`**, `CMessageList` vft **`0x7C2A50`**.

## A. The actual native row control IDs and pixel-space layout

`PMessageRow::0x46E680` is the **real row child-control setup** invoked by virtual `+0x04` from the `CMessageList::0x471D20` allocator at `0x471F65..0x471F74`. Its source list/control allocation records and exact child owner assignments distinguish clickable text controls from decorative/status graphics:

| PMessageRow field | Native child ID | Native original local x/y/width/height and data owner | Verified source |
| --- | --- | --- | --- |
| **`+0x348`** | **1** | **532 × 18**, row background original grid at local (0,0); registered to parent row by child vtable+0x08, ordinary resource `0x945E30` | `0x46E6B7..0x46E717`, background setup `0x651BA0` and original crop `0x5F55D0` |
| **`+0x37C`** | **2** | local **(38,0,215,16)**. Text source is record string at **`PMessageRow+0x174`**, obtained from message `+0x1C` | `0x46E717..0x46E752`; text setup `0x5D68D0` |
| **`+0x4AC`** | **3** | local **(256,0,215,16)**. Text source at **`PMessageRow+0x74`**, obtained from message virtual **`+0x18`** | `0x46E752..0x46E78F` |
| **`+0x5DC`** | **0** | local **(474,0,71,16)**. Formatted numeric/date-like field is **`PMessageRow+0x274`**, source message `+0x04` via `0x64CCD0` and `0x471FA0` | `0x46E78F..0x46E7C0` |
| `+0x70C` | **0** | icon/control with original setup (15,3), size read from original wrapper `0x945C30`, mutually managed with `+0x73C` | `0x46E7C0..0x46E7FC` |
| `+0x73C` | **0** | icon/control with original setup (15,3), size from wrapper `0x945BF0` | `0x46E7FC..0x46E838` |
| `+0x76C` | **0** | icon/control original setup (2,4), size from wrapper `0x945AF0` | `0x46E838..0x46E874` |

**Exact row-local dimensions and IDs** follow the original instruction arguments in `0x5D68D0`, `0x64F380`, `0x651BA0`; the row **532×18** also matches the original 532×18 grid-asset headers. **NOT YET PROVEN:** absolute screen x/y of `PEAMail+0xF58` list parent, row font names/actual pixel raster, labels for the text columns, and whether the row background's ID1 click always produces the same neutral row-event argument. Avoid guessing a global screen rectangle from these row-local values.

## A2. Source-verified CMessageList list rect and eight visible row-slot stride

A follow-on direct source trace identifies the previously unresolved **panel-local list control geometry**, but **not yet the whole PEAMail panel's absolute screen origin**:

1. The real `PEAMail` child setup **`0x46F511..0x46F557`** obtains `PEAMail+0xF58` (final `CMessageList` vtable `0x7C2A50`), assigns parent/control ownership with **ID `0x11` (17)**, and calls the list's virtual **`+0x98 → 0x6510F0`** with exact nine original arguments:
   ```text
   0x6510F0(x=0xE9=233, y=0x1E=30,
            width=0x221=545, height=0xA0=160,
            visible_slots=8, row_stride=0x14=20,
            extra_arg=2, initial_scroll=0, flags=0)
   ```
2. **`0x6510F0`** forwards the first four arguments to `0x64F380` as the source local control rectangle, writes `CMessageList+0x30 = 8`, **`+0x34 = 20`**, **`+0x38 = 2`**, **`+0x3C = 0`** and allocates eight 0x30-byte list-entry descriptors (`0x65113E..0x65117B`).
3. The source loop **`0x651194..0x651209`** invokes the CMessageList virtual **`+0x9C → 0x471D20`** once per visible slot, links each actual concrete `PMessageRow` as list child, and positions it using list row geometry virtuals **`+0xA0`** / **`+0xA4`**. The source initial viewport starts at scroll offset zero.
4. Thus the native inbox has a **545×160 panel-local list region at (233,30)** with eight **20-pixel-spaced row slots** holding **532×18** source grid rows. This corroborates the earlier source `max(0,filtered_count−8)` scroll limit rather than replacing it with an arbitrary table pagination rule.

**Classification: EXACT original `PEAMail`-local list position, 8-row count, 20-pixel row pitch, embedded row dimensions, constructor ownership and original list factory.** **UNKNOWN:** original PEAMail panel's absolute screen offset, scroll widget visible pixels/click events, whether the enclosing panel placement changes the final coordinates, and the specific native row-boundary hit-test action sequence. Do not render it at screen (233,30) before establishing parent offset.

## B. Four real original EAMail grid resources — no guessed modern row background

The original executable paths at `0x836024/0x836050/0x83607C/0x8360AC` and static resource loaders bind:

| Native grid art | Loaded wrapper / source code | Verified original ISO data |
| --- | --- | --- |
| `fm2001_art/generic/eamail/text_grid_nor.444` | `0x5F5580→0x5F55D0`, **`0x945E30`** | LBA **105652**, **8,124 bytes**, SHA-256 **`74676dce75532b781551cab6e8598f805fa4698b2e1b828c9f4ef15b3ff0816d`** |
| `text_grid_sel.444` | `0x5F5620→0x5F5670`, **`0x945DF0`** | LBA **105656**, **7,504 bytes**, SHA-256 **`6b6ff7ce36b3c507df2d590ba7ad48b9253409757844acf4ec93204807bad556`** |
| `text_grid_high.444` | `0x5F56C0→0x5F5710`, **`0x945DB0`** | LBA **105648**, **6,856 bytes**, SHA-256 **`a13b413d13b5fa9c5f6a7b36f632c60342898de72bcff2ee73025bc92fdb68c8`** |
| `text_grid_des.444` | `0x5F5760→...`, original loader for wrapper based at `0x945D70` (**exact wrapper allocation/end cropping needs follow-on**) | LBA **105644**, **7,184 bytes**, SHA-256 **`cb1fb08a99dfe204ea9b485f5102e808ab758f80aec96f69e17e9537d8eb2f70`** |

The 444 file headers begin with `0x0214=532,0x0012=18`; do not treat all three text columns as independently modern table widgets when the original uses layered selection-state bitmaps. All source assets remain private; only original paths/hashes/call addresses are persisted.

The **source state transition** is confirmed directly:
- `PMessageRow::0x470B40` calls `0x651BA0` with **selected `0x945DF0`** on child background `+0x348` and enables the three native row text controls by their vtable `+0x14` with argument1.
- `PMessageRow::0x470B90` instead installs **normal `0x945E30`** and supplies argument0 to those native text controls.
- `PMessageRow` virtual **`+0x2C -> 0x470BE0`** uses the global selected-row pointer **`0x87675C`** and pointer-state parameter to switch between **highlight `0x945DB0`** and normal `0x945E30` for *nonselected* rows, queuing source redraw only on pointer change. Source `+0x2C` state-argument identity as 'hover' is **plausible**, not a proven named physical event/gesture until original GUI receipt.

## C. Original row activation is not just an 'open message' callback

Row final vtable `0x7C266C`:
- **`+0x10 → 0x471B80`** handles the argument **zero** action. First activation of a *different* row sets selected pointer `0x87675C`, selected flag `0x876754=1`, stores message virtual `+0x1C` as preview content `0x876750`, calls selected drawing `0x470B40` and inbox preview `0x471620`. Reactivation of the already-selected row sends original message to `0x471270`, creating the `PEAMMessage` detail view and then refreshing selection/counters. Original physical click-count sequence remains unproven — **do NOT label this necessarily double-click**.
- **`+0x20 → 0x471C60`** has a *separate* native event callback for child action IDs **2 and 3** (source event object `+0x20`). Event **2** uses the underlying record's embedded field `+0x1C` and row byte `+0x490` through helper **`0x5CF7B0`**; event **3** calls **message-object virtual `+0x34`** using a row byte at **`+0x5C0`**. Their returned identifier values are processed through original `0x604900` or `0x605DC0` depending on the associated context pointer. The native precise action labels, resulting panel type and keyboard shortcut are **NOT source-closed**. This proves there are row-specific actions beyond preview/details, and they must not be silently dropped or automatically mapped to 'delete' or 'reply'.
- **`+0x08 → 0x471FC0`** checks original message status **`message+0x08 bit0x01`** and, if clear, invokes the native control's virtual `+0x34` on row icon `+0x76C`, then recomputes row graphic/status effects. The physical semantic label of bit0x01 is not yet independently proven.
- **`0x471780`** checks original message **`+0x08 bit0x02`** and mutually toggles icon controls `+0x70C/+0x73C`. Their vtable `+0x30=0x64F510` sends argument1 to underlying `+0x0C`, and `+0x34=0x64F520` sends argument0; the branch chooses opposite on/off states depending on status bit0x02. Detail `0x471270` independently **clears the same bit0x02** when opening the message, so source visibly relates this status bit to the row's two icon states. It is *plausible* this is read/unread, but **unproven as a semantic caption**; do not invent persistence rules before tracing original save/restore.
- Previously proven `PEAMail` message count/filtered `+0x68/+0x6C`, eight-row scroll calculation `max(0,count−8)`, and post-detail scroll restoration remain binding.

## D. Comparison to current runtime and immediate Codex handoff

At latest Codex head `0ae745d1b56f45cade460f03cd893849a2f53b45`, `reconstruction/original_game_host.py::on_click` has no live PEAMail route. Both main and Codex still lack the actual **PBg direct EAMail header click**, original **CMessageList/PMessageRow**, and native **PEAMMessage** detail. PMenu 0x65 identity does not imply a working inbox; header source geometry from Recovery449 is exact **(558,0,40,95)**, with original PMenu (599,0,100,95) and NEXT (700,0,100,95).

**Codex implementation (NOT this audit worker):** recover original PEAMail list-parent screen origin / font and owner, then restore the verified 532×18 row UI, left/middle/right text bindings, four row graphic states and the *source accepted* selection/reactivation and auxiliary event2/3 pathways, with message bit0x01/0x02 icon toggles. Integrate genuine data/filter/sorting source, an empty and populated mailbox and context-qualified Escape/detail return; test through **normal native-look mouse/keyboard** across two different managers/clubs and source font/resource validation. Do not create a generic ttk inbox table just because row local coordinates are known; source visual/gesture control owners matter.

**Status:** row controls/size/content/resource identities/state-callback code are **EXACT** original-file evidence. Absolute inbox list x/y, original semantic labels, keyboard/mouse precise acceptance, message category/actions and source persistence remain **UNKNOWN/PARTIAL**. **Gate13 remains OPEN**, Gates14–17 and original full-scope Windows11 release INCOMPLETE.
