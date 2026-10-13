# Recovery583: authentic Inbox ten-filter label font and source draw ownership

**13 October 2026 KST.** Canonical original private 4,714,541-byte footballmanager.exe SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, static disassembly only, **NOT original runtime execution**. This WIP begins AFTER source-filter PR662 merge `c687981ea74b72f2e2b07b80e7f54fc8a97fff22` and main resume checkpoint `ea1695eb7b1c3e44996eac25c52c6a792de38976`. Gates13–17 OPEN.

## Exact font and ten labels, new original-source verification

- Native PEAMail owner calls `0x5D4F00` with row positions `(x=22,y=30+30*i)`, ten native rows i0..9 (source ID2..11), labels from global English ordinal177..186. Original source strings are `New`, `All`, `Finance`, `Building`, `Events`, `Player/Team`, `Transfer Market`, `Youth Team`, `Contracts`, `FA`. These are original English STR/IDX, NOT handwritten localization defaults.
- Native `0x5D4F50` increments **EBP** by0x1E, EBP being the source x anchor22, so text's caller-supplied local x becomes **52**, while EDI remains the original row y30+30*i. Do not misinterpret `add ebp,30` as a y increment to the next row; that would cause overlapping labels.
- Original `0x5D4FD1` pushes actual font object VA **0x9197E0** and `0x5D4FD7` pushes text bitmap wrapper **0x945BB0**, control flags from `0x5D4FCC` **0x2001**, then calls native text setter `0x6528D0`. Original `0x6042F0` calls `0x657650` on font object0x9197E0 after its **previous** source filename literal; actual string VA **0x839F00** is `Fonts\Zurich_BdXCn_BT_18pixel.fnt`. Do not confuse the **next** literal `0x839EDC` (Zurich BdXCn 20px font) prepared after `0x6042F0` for another font object. Independent native source memory parse confirms all three adjacent filenames: at0x839EB8 25pixel, at0x839EDC 20pixel, at0x839F00 18pixel.
- Owner's private uploaded extracted `FM2001/Fonts/Zurich_BdXCn_BT_18pixel.fnt` individually materialized: **83,174 bytes**, SHA256 **`4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd`**. Exactly named file also exists in current Git source package `original_assets/source/Fonts/Zurich_BdXCn_BT_18pixel.fnt` with recorded size83,174. This is a positive authentic ORIGINAL asset receipt, unlike still-unverified `boost_type_11.444` radio bitmap.
- Native `0x6528D0` forwards twelve stack arguments into `0x651E30`, invokes text control virtual+0xB0 and initializes +0x48/+0x4A selection bytes. Its broad delegated `0x651BA0` source clip/position/color, text glyph raster and 0x2001 alignment behavior still require separate exact proof. The x52,y30+30*i are **text child constructor input coordinates**, NOT completed glyph bounding-box/center/clip proof.

## WIP implementation and strict limitation

New `reconstruction/original_eamail_filter_labels.py`: hash-verified source 18px font loader + original English STR/IDX locale resolution for ten exactly named labels, source font VA, wrapper VA, native flag and panel-local constructor anchor, no fake art. Test `test_original_eamail_filter_labels.py` checks real shipped font hash/10 labels/native coordinate owner, rejects missing/mutated font and optional private original executable source bytes (no executable launch). None is yet a visible live row, selected radio, full mouse handler, or source-exact glyph clipping. **NO PR/CI on this new WIP branch**; bundle with a cohesive actual display milestone after completing native text+radio provider ownership and source-backed interaction. The fully merged previous PR662 remains source/controller work only; physical original ten radio filters are still missing.

**NEXT:** trace source `0x651BA0` text layout, 0x2001 flags and original filter text child final vtable colors to render genuine font alpha masks. Trace native `0x657820` filesystem/provider and old `boost_type_11.444` radio art filename; NEVER substitute `button_type_11.444` without source proof. If source missing beyond available static evidence, record exact original-runtime observation needed and advance a different player-visible Gate13 original art workflow. No original process or Win11 GUI acceptance; do not close gates.

Reproduce authorized read-only source:

    objdump -D -Mintel --start-address=0x5d4f00 --stop-address=0x5d5000 footballmanager.exe
    objdump -D -Mintel --start-address=0x651ba0 --stop-address=0x651e90 footballmanager.exe
    objdump -D -Mintel --start-address=0x6528d0 --stop-address=0x652940 footballmanager.exe
    objdump -D -Mintel --start-address=0x6042b0 --stop-address=0x604350 footballmanager.exe
    sha256sum Fonts/Zurich_BdXCn_BT_18pixel.fnt
