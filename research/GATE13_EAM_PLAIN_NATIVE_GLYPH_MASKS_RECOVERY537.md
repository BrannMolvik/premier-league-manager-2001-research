# Recovery537 — original Inbox eCText font masks for native plain columns

## Source-proven bounds, not a full rendered game screen

Original private shipped executable `footballmanager.exe`, 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; no original EXE launched. Native `PMessageRow::0x46E680` constructs eCText ID2/3/0 through `0x5D68D0`, at row-local (38,0,215,16), (256,0,215,16), (474,0,71,16). Original text rendering `0x5D75B0` initializes default font object `0x9269F0`; separately authenticated loader/font identity is `Fonts/Zurich_BdXCn_BT_16pixel.fnt` (79,722 bytes, SHA256 `9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732`, 1526×17 atlas) already used for faithful League Tables row text. Native delivered initial EAM transfer request producer builds ID3 subject `Transfer List` and ID0 date via original English file; both source-confirmed; ID2 contains `<T+P>...<T->` or `<T+P>...<T-> @ <T+C>...<T->` and is NOT plain text.

## New bounded tested implementation

`original_eamail_plain_glyph_masks.py` uses exactly this **authenticated original font atlas** to pre-render *alpha-only* native-font glyph masks for real delivered ID3 title and ID0 date within their validated native child rectangles. Does NOT draw them to normal game screen yet: original row alignment, control visibility/bit4 behavior, color, glyph positioning, clipping and native modified-buffer rich markup remain incompletely traced. It intentionally skips ID2 even when original rich-tagged text is available; never strips angle brackets, guesses colors or paints text in an unqualified layer. Emitting a prepared mask is NOT original GUI acceptance.

The source-derived tests exercise the real New Game/selected human/delivered PEAMail presentation, exact child geometry, original text/CP1252 glyph alpha pixels, empty registered-user mailbox, corrupted NUL/tag handling and no player markup pretending to be literal text. Both focused Gate13 and full reconstruction CI are wired to run these tests on the exact branch head.

## Native parser follow-on

The original native eCText render path `0x5D75B0` parses tags through selector `0x5D7A4C`; `<T+P>/<T+C>/<T->` are not interchangeable with Python string replacements. Function `0x5D7500` renders font glyphs via `0x6570A0/0x6570F0`, with original glyph palette/clip/caret potentially dependent on other eCText and downstream render state. The original +0x98 and +0x9C virtual functions at `0x650650/0x6506A0` mutate the text buffer/caret and are called from parser. Until native positional and color semantics and text visibility state are established, do not paint a visually plausible fallback.

Next: source-trace original PMessageRow eCText draw callback caller state, default glyph color & layout, T+ markup state and selected/normal bit4; then convert alpha masks into exact native-colored/clipped visible glyphs in ordinary Inbox. Also resolve PBg back_3 sprite frame state/hover input, message preview/modal/actions/Escape and full game. Gates13–17 remain OPEN, Windows 11 GUI untested.
