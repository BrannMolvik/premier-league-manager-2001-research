# Recovery589: original FastView remaining 22 native row rects and text owners

13 October 2026 KST. Gate13 active; Gates13–17 OPEN. Source is owner-approved original footballmanager.exe, 4,714,541 bytes, SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3, retrieved privately from Drive original ID 1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q. Static native PE read only. NO original process was launched and NO private bytes were added to Git.

Builds upon verified and merged PR664 and research/GATE13_R1_FASTVIEW_NATIVE_POINTER_DISPATCH_RECOVERY589.md; that milestone established six native eleven-row event families (66), parent callback gates, and coordinates of previously missing 22 controls.

## Native source geometry: first 11 native text controls

The eleven native x80,y=278+17*row controls with exact event IDs 0x23D65A+row use source constructor 0x6503F0 → 0x64F380. Their original constructor arguments give explicit WIDTH 0x28=40 and HEIGHT 0x10=16; 11/11 exact PE width/height/y/x source checks passed. Unlike four arrow sprite families, each of these eleven controls receives a distinct original screen-local text-buffer pointer screen+0x374+0x20*row and shared original source owner 0x87BEA0. At each original call address 0x527FBE,0x5283AC,0x5287BA,0x528BE3,0x52900C,0x52943B,0x529879,0x529CC3,0x52A116,0x52A56C,0x52A9C2, preceding machine code at call-0x1B computes that screen pointer and call-18 pushes the owner immediate. All 11+11 source byte sites independently matched SHA-verified private PE. This proves owner and pointer, NOT actual rendered text, glyph content, or editor side effects.

## Native source geometry: second 11 dynamic resource controls

Eleven separate x133,y=278+17*row controls with exact event IDs 0x8877AE+row use source 0x5D71A0 → 0x651A50 → 0x64F380. The source constructor passes original owner 0x877820, and 0x651A50 obtains a LIVE width DWORD from owner+0x14 and height DWORD from owner+0x18. Original owner initialization at 0x52CFF0..0x52D01A calls 0x64E460 with explicit width 0x9C=156 and height 0x10=16. Original 0x64E4E0 stores the width and 0x64E4F0 the height at these respective offsets. Thus first original source-initial bounds are x133,y278+17*row, width156, height16. The source still looks up mutable owner fields; no claim is made that dimensions can never change. Exact native bytes for 0x52CFF0,0x52D000,0x52D015,0x64E464,0x64E471,0x64E4E0,0x64E4F0 and 0x651A57 plus earlier owner/dispatch sites were directly verified in private original executable.

Original 0x52F690 (the parent first callback special row response) uses mapped source row BYTE screen+0xB46+selectedRow, conditional source lookup structures 0xA14BCC / 0xA14C0C, text buffer screen+0x4768 with 0x20 stride, row index cache screen+0x4848 and child array screen+0x263C. It invokes eleven source child vtable+0x3C callbacks in a guarded case and an indexed one in another case. This is an original event-related *read and redraw/format path*, NOT a license to simulate player-record mutations or assume callback equals mouse release; remaining path semantics require further investigation.

## Bounded code, verification and next source task

Current feature branch worker/gate13-r1-fastview-native-hit-and-rect-source-589 contains:
- reconstruction/original_fastview_tactics_control_layout.py: fixed first-family 40x16, initial second-family 156x16, live dynamic resource owner 0x877820, source text-buffer per-row offsets and owner, strict refuse-to-guess runtime sizes;
- reconstruction/test_original_fastview_tactics_control_layout.py: pure 22-row geometry and fail-closed validation; opt-in original PE bytes for fixed geometry, text producers and dynamic original owner initializer.

These are source-only checks, NOT live player-visible tactics, original startup, match calculation, post-result, or Windows11 GUI proof. No new PR/CI at this scratch stage.

Next: source-qualify native 0x6503F0 and 0x5D71A0 actual input/size/vtable callback sequence; recover 0x52F690 row read/redraw effects and 0x633020 guarded mutations/0x6C2170, then reconcile actual synchronous mode2 0x5331C0 modal and post-modal two-sided player writes with true R1 simulation, PResults and management return. Continue all remaining Gates13–17 and complete actual Windows11 acceptance before any release-complete status.
