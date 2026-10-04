# Ordinary Fixtures paging and PMenu visibility

5 October 2026 KST. Canonical executable SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Authorized ZIP independently rehashed:
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
No original execution, probe, registry change, report injection or Gate14 work.
Disassembly, complete private reports and the genuine save remain outside Git.

## Exact source controls (closed)

| Field | Left | Right |
| --- | --- | --- |
| Owner member | `PLeagueFixtures+D30` | `+D60` |
| Native event | 39 | 40 |
| Wrapper | `9474F0` | `9474B0` |
| Literal | `834B9C` | `834BDC` |
| Original basename | `toogle_arrow_left.444` | `toogle_arrow_right.444` |
| Local rectangle | `(351,213,27,18)` | `(721,213,27,18)` |
| Length / SHA-256 | 4,024 / `31c0b0c96c5e13c10c4f38f04a47456c178ad87e12eb3381bf9f07010ca86982` | 3,760 / `125a70a2e4ac36970e592068c8781d9109e9b0518575f97949c24c369d3c7173` |

Both exact files live under the original
`fm2001_art\generic\GenericButtonsAndBars` directory; the `toogle` spelling is
original. They are now controlled, provenance-imported assets. Each decoded
atlas is **108x18**, four horizontal **27x18** frames, not fifteen frames.
`64E500` stores the pushed `0xF` at descriptor `+4`: a capability mask.
Descriptor draw flags are `8000`, other field `100`.

`46D579..46D5A7` constructs the concrete bitmap controls, vtable `7BE3E8`,
initial flags `183`. `46B92A..46B9D0` supplies the exact events, origins,
wrappers and renderer `87BF00`. Vtable `+6C ->64F7A0` accepts enabled bit2,
rejects already-captured bit10, obtains true from parent `42DE00`, captures
and sends the parent action on **press**, not release. `+70 ->64F860` clears
capture; parent `428AE0` produces no second page action. Container `653480`
uses half-open bounds and subtracts the actual parent origin.

`+84 ->64FBE0` sets/clears hover bit8. `+90 ->64FDB0`, with descriptor F,
selects frame3 disabled, frame1 captured (`10/20`), frame2 hovered, otherwise
frame0. Disabled wins over capture/hover. Descriptor F does **not** enable
the selected-bit4 frame. `64E5D0` reads source x=frame*27; no scaling/recolor.

`46DCD0/46DD5B..46DD8B` enables left iff offset!=0 and right iff
offset<club_count-12. `46E040` dispatches to `46E489/46E4AB`, subtracts/adds12
and clamps at0 / club_count-12. Twenty clubs therefore page0↔8, not0↔12.
Factory `47C724/47C74E..47C75D`, with the EDI zero producer `47AEE1`, calls
`47F280 ->653320` with origin0/0 and extent799x599. This closes the screen
transform for both arrows; neither is at a clip edge.

## Required dependency: PMenu is a popup, not a permanent overlay

The initial Tk input proof succeeded but its visual-tail check found **486/486
right-arrow pixels** covered by the permanently drawn menu. That receipt is
rejected as a complete visible-navigation proof. Raising the arrow over PMenu
would invent native z-order and was not done.

`4C2FB0 ->5EC060` pushes the selected child onto the panel stack.
`532960` returns its current top; constructing PMenu does not make it top.
Application setup `43095F..43098D` registers compound `+4E0`, event2,
at `(599,0)`. `4313B0`, descriptors `943A90/943AD0`, and initializer
`5FA650/5FA6E0` establish width30+70 and height95: `(599,0,100,95)`.
Concrete vtable `7BEB2C+6C ->5D6270 ->5D4790 ->64F7A0` uses the accepted
enabled/capture press route; `5D48C0` propagates event2/parent to its children.
`432690/4326AE..4326CE ->5EBEA0` pushes PMenu only when not already top.

Application pointer callback `432970` dismisses at x<524 or (y<96 and x>700).
The second threshold comes from original user-selector `+524+8`, initialized
at x700 by `4309B4..4309C4 ->5D3900 ->651E30`, not the popup's right edge.
`4329F0 ->5EBAC0 ->532980` pops PMenu. Child transition
`47AD60 ->5ED2A0` removes and then re-pushes an already-open menu; title/child
selection is not synonymous with popup visibility.

The host now starts closed, opens from this source event2 rectangle, retains
an open popup through accepted child transitions, and honors the proven pointer
dismissal. Visible PMenu owns input; hidden underlying paging/report actions
are not accepted through it. Original draw ordering is unchanged. The header
compound's dynamic art/text remains unrendered, **not source-pixel complete**:
its now-known resources are `Background_buttons/back_4.444` (`837A6C`) and
`back_4_anim.444` (`837AA0`). This remains a recognizability audit item.

## Genuine ordinary away proof

Automatic non-zeroing Windows allocation produces native inputs; the real
calculator publishes a complete report for fixture2, Coventry5 hosting human
Middlesbrough11. Schema44 disk save SHA-256:
`4275d5a5be5374a2288faade60a845697eb6b2ff1a03801cccc5c77801154d61`.
No report, scalar, link or capacity values are injected.

A **fresh Tk process** reloads that save, opens/dismisses the menu through real
pointer bindings, verifies both arrow PhotoImages and zero menu occlusion,
clicks right→8 / left→0 / right→8, tests repeated press and release, then
ordinary right-clicks the real fixture cell. The explicit host paging seam is
patched to raise if called. The retained report owner/context matches exactly;
Attendance22,859, Ref.B Betsy, Mom.Colin Hendry, Coventry/Middlesbrough3–0 and
the nested original pitch render. This fixture has **zero script rows**;
nonempty script rendering is not asserted by this receipt.

Initial corrected ordinary-route receipt SHA-256:
`d22de98fa7b130df69331366073256e8e62a6ecaa67ea77f3a26004fbd159125`.
Earlier occlusion failure SHA-256:
`a7b65f52d8ab731c4b9bca5aa9c9937d9c4e3c7b5bb6e617797758c3920ff8e5`.

## Private source receipt identities

Resources: `a9d4a39332720290d6031ba00c667962761bad7801461cc000361dffc23bcdfc`.
Concrete controls/bounds: `67950af908a05eb28c1e2cae814ad0e23563869cfadc298e59198e2a9ebafeb9`.
Draw/frame/container: `04b42bc14f1da6d1ba9cf9440474c4849f34c65b5db81d7308bf00aef6397a3f`.
Wrapper semantics: `76b522392e9cb12c9bb8f801f2045f4d885b67b9626c4a1da56dd073ad559b42`.
Zero-origin producer: `11293b189eb54d0ad092293561ec569cc0fe99c158d9ba318098e6727f97fe20`.
Menu stack: `46958a4fde00989a567efa68d004fbc4f5b097ab2a2b2deaca148d84de01718a`.
Menu child transition: `a84910de5d9ed41fc02a8d67e0af6dbf8cb0db23de802cc3c216942d9039223c`.
Header vtable/literals: `96de182f33f1ece631bf9c39ca21bf16ee0f6d0049dea182ce46f093a80de74a`.

## Remaining Gate13 criterion boundary

Ordinary Fixtures paging/report navigation is closed for this genuine route.
Gate13 is **not** complete merely because that route and schema8 pass.
The live first-screen host still calls `build_original_debug_frame(view,0)`:
the recovered 11-step Button hover state model is not advanced by the live host,
and no original update cadence has been qualified. Do not invent a Tk timer.
The required next source-backed step is the existing Button update owner/
cadence and its actual live integration, then final recognizability review of
the recovered management header and ordinary data/text presentation. No
completed native capacity/report work needs to be repeated.
