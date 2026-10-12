# Original Inbox list: source contract and connected milestone

## Evidence before implementation

Authorized local `C:\Games\FM2001\FOOTBAL.EXE` was rehashed: 4,714,541
bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Static Capstone/PE inspection only; no original execution or interactive Windows
test is authorized for this assignment. Private bounded disassembly stays outside
Git. Main baseline is `29e7f2e108edaaebf478d1e204e6ac3d0035c569`.

**Source:** row construction `0x46E680`, final child-vtable assignments
`0x471E09/43/7D`, raw vtable `0x7BFAC8`, renderer `0x5D7360 -> 0x5D75B0`,
glyph/advance `0x5D7500`, word measurement `0x6574E0`, parent clipping
`0x6533A0`, selected-state setters `0x470B40/90`, status producer `0x471780`,
icon loaders `0x5F5A40/AD0`, and scroll dispatch `0x650020 -> 0x64FF30/90 ->
0x4721C0`. Original STR/IDX, font and art use existing hash-gated loaders.

**Hypothesis tested:** row text was blocked partly by an incorrect virtual
dispatch interpretation, not missing glyph data. Raw final-vtable reads and
independent constructor assignments establish this; reconstruction tests alone
do not establish native behavior.

**Unknown:** complete preview RNG ownership (blocked PR #638), mutable message
status/actions, complete message subclasses, >16-pointer hybrid sorting,
descriptor sorting, physical filter/header controls, thumb drag and held-repeat
cadence. No inferred bodies, links, read transitions or RNG advancement.

**Smallest implementation:** paint the three qualified text columns and initial
unread icon; connect source arrow press/release and one-row clamped scrolling;
retain recipient/data ownership and existing fail-closed sort/class limits.

## Correction to earlier native notes

Recovery536/537/541 incorrectly attributed generic eCText virtual slots to the
actual Inbox row children. Final vtable **`0x7BFAC8+0x98=0x43B680` and
`+0x9C=0x43B6A0`**, not `0x650650/0x6506A0`. The latter belong to generic
`0x7BE340` and edit text; the actual Inbox slots are **color getters**. Selected
mask4 chooses `+0x124/+0x12C`, otherwise `+0x120/+0x128`. Rendering this bounded
Inbox label does not mutate its raw text buffer. Opt-in licensed-source tests
must guard these exact final dispatch slots against regression.

## Qualified rendering

* Child IDs2/3/0 are row-local `(38,0,215,16)`, `(256,0,215,16)`,
  `(474,0,71,16)`; the last extends beyond the 532px background, within the
  545px list. Parent panel `(0,148)` plus list `(233,30)` gives `(233,178)`.
  Rows have 20px pitch, eight visible slots. Clip each child to its rectangle
  and list; no invented centering, inset or ellipsis.
* Font object `0x9269F0` is the verified Zurich BdXCn 16px font. Constructor
  `0x5D68D0` gives untagged white/selected black and tagged RGB
  `(120,238,130)`/selected `(11,37,13)`. `0x471780` retains those inputs.
  These are source RGB inputs to the existing RGBA presentation pipeline, not
  a claim of bit-exact legacy display-format blending.
* Only the two already-qualified `<T+P>...<T->` / club-label templates are
  accepted. T+ uses the tagged getter; T- resets the untagged getter. No
  heuristic tag stripping or synthetic player/club actions.
* `0x5D7500` draws before advancing; advance uses **current glyph's pair with
  the previous raw byte**, including `>` after a tag. This differs from the
  generic single-line mask helper. Space advances but is not drawn. After a
  space/tag, `0x6574E0` measures until space/`<`, starting with space width;
  overflow wraps by truncating atlas-height times **1.5** (`0x7D738C=0x3FC00000`).
  The 16px control clips wrapped lines; do not shrink or substitute the text.
* Row `+0x70C` / wrapper `0x945C30` is read_mail_icon; `+0x73C` / wrapper
  `0x945BF0` is unread_mail_icon, both 18x12 at `(15,3)`. Status bit2 selects
  unread. Only immutable initial transfer flags6 are currently qualified.
  First selection does **not** mark read; repeated activation remains blocked.

## Qualified scroll slice

PEAMail up/down IDs19/21 at panel-local `(212,30,18,25)` and
`(212,163,18,25)` use wrappers `0x9470B0/0x947090`, the verified generic
72x50 arrow atlas. Static frames are idle0, pressed1, disabled3. Press
`0x650020` invokes `0x64FF30`: step1 clamped to `0..max(count-8,0)`;
`0x64FF90` disables bounds. Release clears pressed state without another step.
Dispatcher `0x47223C` clears row-pointer selection when rebuilding, even if
the message remains visible. It does not establish a new body/read state.
No fake wheel, drag or repeat timer is added.

## Verification / remaining work

At baseline `29e7f2e1`, 91 Inbox-focused tests passed, including the two new
opt-in licensed-source checks; 142 host/menu/presenter integration tests passed.
New coverage distinguishes post-draw reverse-pair advance, raw `>` kerning,
native word-wrap/clip, normal/selected colors, unknown tags/names, source icon
placement, eight-row bounds, scroll/release selection semantics, no RNG/data
mutation, and delivered rows/text across the real save codec.

Full local Windows suite: 3,424 tests / 28 expected skips, **4 failures and 1
error**, all the same pre-existing Gate17 FFmpeg fixture/path failures reproduced
on the untouched pre-menu baseline in the prior audit. No Inbox/host regression
failed. Asset policy passed. This is noninteractive Python testing on Windows,
not interactive GUI acceptance or original runtime evidence.

Inbox remains PARTIAL: readable list and bounded navigation are not complete
preview/detail/action acceptance. Physical filter/sort controls, thumb/held
repeat, >16 hybrid sorting and descriptor sorting remain fail-closed. No
SupportStart, simulation/RNG ownership, save schema or agent-runtime changes.
Final reconciled-head verification is recorded in the PR; no automatic merge.
