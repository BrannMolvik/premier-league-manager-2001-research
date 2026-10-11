# Gate 13 — Recovery538: original PBg direct Inbox initial bitmap **rendered** (bounded state)

## Original source, not an inference from a modern widget

Canonical owner-authorized `footballmanager.exe`: 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Source art `FM2001_Art/Generic/Background_buttons/back_3.444`: 5,932 bytes, SHA256 `f369e73c2a7f9149661d66cf3c781ddc8eabf01f80ef924b423d46d57cf628e6`, original EA444 **40×380** pixels. Both verified from actual source bytes; original game executable has **not been executed**.

Static original PE disassembly, independently inspected this recovery:

- `0x5FA570` loads original source string `0x837A38`, original wrapper `0x943B30`; `0x5FA5C0` binds bitmap descriptor `0x943B10` via `0x64E500` using literal **x=0, y=0, width=40, height=95**, and bitmap mode `0x100`. Thus initial source crop is the **uppermost 40×95** strip, not an inferred stretch, a full 40×380 rendering or a random frame.
- Original PBg factory `0x43092B..0x430957` registers **child ID1** at parent-local x558,y0, passing to `0x431850`, which constructs a **40×95** region via original width/height wrapper values `0x943B24/+0x943B28`, with source descriptor `0x943B10` passed to rendering helper `0x5D6630`. The existing direct Inbox header click `0x4326D6→0x482BF0(0x65)` is already integrated from PR627.
- Generic original eCControl constructor `0x64F300` sets **control+0x18 = 0x183**. The original eCControl/default-button virtual slot `+0x90` at table `0x7BE530` is **`0x64FDB0`**. In the initial flag state `0x183`, function `0x64FDB0` returns frame index **0** regardless of image flag bits, because the intermediate pressed, disabled, hover branches do not match. Therefore original initial bitmap crop (0,0,40,95) is independently confirmed both by original descriptor setup and the actual frame selector. This is a deliberately bounded original **idle** proof.
- The same frame-selector source `0x64FDB0` returns generic indices 0–4 conditional on control bits and resource state. **back_3 contains only four 40×95 frames (0–3)**; generic frame4 must not be blindly sampled. No original pointer-event/state-producer proof has yet established all original hover/pressed/disabled flag transitions or the full end-to-end game visual behavior.

## Code and ordinary host integration

`reconstruction/original_pbg_mail_art.py` validates original source SHA+geometry, uses the existing original PE-verified EA444 quantization/table decoder, exposes exact native `0x64FDB0` frame-selector semantics for independent source tests, and accepts **only native initial control flags `0x183`** for a drawable idle crop. All non-initial states fail closed until source input mappings can be proven.

Normal `OriginalGameTkHost` loads this authenticated art in its existing fresh management Squad-family loader along with header/NEXT, retains it for later Inbox/Fixtures/Tables panels, and draws the actual 40×95 original bitmap at **(558,0)** in the normal management header before later input. This is player-visible initial original asset work, not a substitute placeholder; the direct header ID1 click path still routes to the actual registered-user delivered Inbox.

Tests cover byte-authentic source, original four-frame raster, native generic flag-precedence cases, initial-frame crop/pixel identity, rejection of unknown pointer states/corrupt geometry, and real normal host draw placement. Focused Gate13 and full reconstruction workflows include the tests. **This does not qualify header hover/press/focus animation, full Inbox, match/season, or genuine Windows 11 GUI acceptance.** No original EXE launch, Gates13–17 remain OPEN.

## Next original-data-critical work

Finish original eCText color/C/P/T rich parser `0x5D75B0`, `0x5D7500→0x6570F0` and native child flags/clip, then paint exact delivered Inbox ID2/3/0 text (source font masks merged PR629/630). Complete preview, PEAMMessage dialog actions/Escape/read/rebuild, header button native dynamic flags, filter/scroll; then original NEXT through all four PPreMatch modes/PResults/return, Squad/Save/Load, every shipped league/country and 2–6 users; Gate13–17 Win11 release audit.
