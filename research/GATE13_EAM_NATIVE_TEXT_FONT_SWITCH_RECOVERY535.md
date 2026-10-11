# Gate 13 original Inbox eCText font and tag dispatcher source recovery (Recovery 535)

## Source identity and exact control draw owners

Static x86 instruction and PE-raw-byte mapping from privately authorized original `footballmanager.exe` (4,714,541 bytes; SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; `.text` original VA `0x401000` to file offset `0x1000`). No running-original observation or graphical acceptance.

Original `PMessageRow::0x46E680` initializes its three `eCText` children via `0x5D68D0`:
- child ID2 / native row+0x174: local rect (38,0,215,16); call `0x46E73D..0x46E752`;
- child ID3 / native row+0x74: local rect (256,0,215,16); call `0x46E774..0x46E78F`;
- child ID0 / native row+0x274: local rect (474,0,71,16); call `0x46E7A5..0x46E7C0`.
Native text renderer `0x5D68D0` calls `0x5D7350` (stores supplied text pointer to object+0x2C); text drawing eventually uses `0x5D75B0`, which initializes default font object pointer `0x9269F0` at `0x5D75C6`. This default is **already independently linked** to `Fonts/Zurich_BdXCn_BT_16pixel.fnt`, 79,722 bytes, SHA256 `9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732`, 1526×17 atlas, through `reconstruction/original_pmenu_chrome.py` and `reconstruction/original_management_text.py`. This proves *font identity* for default render stage, NOT the row's final colors/clip/truncation.

## Verified static rich-tag switch (do not strip tag text blindly)

At `0x5D7642` the renderer checks byte `0x3C` before reading the next tag letter; `0x5D7666..0x5D7689` uppercases the next character via `0x66A98C`, normalizes by subtracting `0x43` (ASCII C), and indexes the original 18-byte selector array at VA `0x5D7A4C` with an eight-target DWORD jump table at `0x5D7A2C`. Independently decoded original PE bytes yield:

| Tag byte | Table index | Native target |
| --- | ---: | --- |
| C | 0 | `0x5D771C` |
| D | 1 | `0x5D788A` |
| F | 2 | `0x5D7690` |
| I | 3 | `0x5D7767` |
| L | 4 | `0x5D76D8` |
| P | 5 | `0x5D76D1` |
| T | 6 | `0x5D7855` |
| E/G/H/J/K/M/N/O/Q/R/S | 7 | `0x5D78D4` fallback |

`F` branch `0x5D7690..0x5D76CF` decodes a following selector digit 0/1/2: selector 0 chooses default `0x9269F0`; 1 or 2 use native font object `0x9197E0` (previously source-linked to `Fonts/Zurich_BdXCn_BT_18pixel.fnt` through `reconstruction/original_squad_row_style.py`). This is NOT sufficient to call every markup tag's final visual style known. In particular `<T+P>...` is first handled by **T**, not by the top-level P case, and nested control/state logic must be traced before splitting or painting color runs.

## Control-state clarification

`0x470B40` and `0x470B90` invoke each eCText child's virtual+0x14; the independently read `eCText` vft `0x7BE340` entry+0x14 is `0x64F430`, which passes mask `0x4` to `0x64F710/0x64F750` and toggles **object+0x18 state bit4**. This independently proves bit-state mutation, not a complete per-pixel text-visibility contract. The preceding Recovery534/535 descriptions of “visible state” must not be read as independently verified glyph visibility until the draw gate consuming bit4 is mapped.

## Required next implementation/evidence

Trace `0x5D75B0` nested T/P/C markup parser, stage-specific colors, text layout/clipping and bit4 rendering gate. Use verified shipped font and current delivered ID2/3/0 text from original language; **do not invent default white, strip angle-bracket codes as plain text, or draw absent label data**. Write original-derived glyph placement/markup regression against actual font and normal host, then continue native preview/modal and header direct mail acceptance. **PARTIAL SOURCE / NOT VISIBLE-ACCEPTED. Gate13–17 OPEN.**
