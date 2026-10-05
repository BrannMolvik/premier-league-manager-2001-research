# Gate13 fixed closure slice — 5 October 2026

Daniel limits remaining implementation to (1) live source-qualified first-screen
Button animation and (2) the already-identified required management header and
ordinary data/text rendering. No new unrestricted fidelity sweep. Non-blocking
pixels, secondary states and obscure contexts belong in Gate15/FIDELITY_GAPS;
completed paging/capacity/report/save/PMatchInfo work is not reopened.

## Button update owner and cadence

Canonical executable SHA256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Bounded source windows corroborate this complete ordinary owner chain:

- WinMain `531398..5313A0` enters `531AF0`.
- `531B1E` calls `531B40` each ordinary loop iteration. While `877A48` is
  clear, `531B53 -> 6597F0` tests/takes available semaphore `877A34` with
  WaitForSingleObject timeout0; `531B65 -> 5329D0` runs one UI pass, then
  `531B6F -> 6597E0` releases it. `531C5C..531C66 -> 531AE0` identifies
  this same semaphore as the nested event-handler serialization owner.
- `5329DD` samples GetCursorPos (IAT7BD2D4). The pass sends pointer transitions
  before `532A62 -> 6541E0`, which updates panels in order.
- `6541F3 -> 6538F0` skips paused panel byte+60. `653910..653927` visits
  update children in original order, skips visibility bit1 clear, dispatches
  vtable+68. Button vtable7BF4CC+68 contains6527F0.
- The existing source-qualified model advances/retreats one subframe per
  eligible update, saturating0..10; group/disabled semantics are unchanged.

This ordinary path has **no fixed hover millisecond timer**. Do not substitute
16ms/33ms or infer a rate from unrelated audio/multimedia timers. Native elapsed
duration depends on loop/presentation execution; no hardware-independent wall
clock duration has been established. The Tk compatibility adapter serializes
one update per idle pass and redraws changed source frames only, retaining
inactive screen state. Stopping stable redraws is an optimization, not a change
to the saturated state machine. No original executable is launched or patched.

Private window receipts (raw disassembly stays outside Git):
ordinary entry/gate: `763ea18fd2d7eed86d58ba8c787caa3bc3acff7162b019d49e2630e5bb954e5b`;
ordinary loop/manager traversal: `f4b239509ee2b02f83d18b759dec5933d31ecdf956ad499348ae840a268535bb`;
event semaphore producer: `906861a5ec8297264d0103eb90d0da434ae2a23d3b6bce93db8a4775be850e4d`;
Button slots: `9d2e76ef83ee45f4039d39d58da813057012eb5b12b80e0d07cdd63abfc595f8`.
Candidate byte hits alone were not used as semantic proof.

Implementation checkpoint: `857a1806`. Focused regression:38 tests,1 expected
licensed-source skip PASS. Real Windows/Tk8.6.12 qualification verifies all
eleven forward source frames0..10 and leave retreat9..0 through the bound
Motion/Leave callbacks and real Tk idle/PhotoImage machinery; other buttons
remain0 and stable redraws stop. Private receipt SHA256:
`e5171f265e8584c354f48ee7cd937efc7ded59e51c0516e5cdbf23e7e38ff817`.
This withdrawn test is executable Windows evidence, not human visual acceptance
or a claim of hardware-independent original wall-clock duration.
Fresh real Windows11/Tk schema8 also PASS at the same implementation checkpoint;
receipt SHA256 `131866c416673c306c932a11899dc4bfe3810c60ee683fd87e82aa7aae2e8cc9`.
Full-suite and Windows-package CI are left to the clean PR; their results must
be checked before merge. This is not the final Gate13 closure audit.

## Bounded header handoff (not integrated)

The authorized archive was rehashed to canonical SHA256
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
Existing source-inventory tooling privately extracted only these exact paths:

| Resource | Source SHA256 | Original image |
| --- | --- | --- |
| `Background_buttons/back_4.444` | `710016aa4f9c2d5a04580ba48e2449882040482d231b875726203836b8cb42bb` |70x380|
| `Background_buttons/back_4_anim.444` | `867abd21e89b21c878d20777547524e8ea4a00fcc9b49524f8356b631a665f69` |30x4845|

These image dimensions alone do NOT establish state/frame semantics. No assets
or raw reports from this investigation have been imported into Git.
`4313B0..431411` constructs the100x95 compound at the already-proven application
origin599,0: its+38 child uses descriptor943A90 at local0,0 (30x95), and+3C uses
943AD0 at local30,0 (70x95), both setup652940. `4314C3 ->652980` sets the
separate+40 caption at local32,62,70x30, style10, font8B0760, English global9820F4.
`604554..6045A5` source-binds that font to `Fonts/Zurich_XCn_BT_24pixel.fnt`.
The exact English loader index, live child state ownership/selector and font
alias initialization for ordinary management rows still need qualification;
do not guess them from nearby literals or image height.

Private bounded header receipts:
`8763c7f33e6d851ae4c251b7fa9c5e5f32ead44ac789d91a1757d123ba247b73`;
`d08c2d9df743fe535a11833f1730cb8633cbbf5d6a2ab6208d88f8659368b7db`;
font/setup continuation:
`cccae3fb8f0732057270b68997b9285167eae4a6bc1a4fc663adf3b3982ef128`.
Private extraction directory `work/gate13-fixed-header-stage` and selection
receipt `work/gate13-fixed-header-inventory.json` are reusable after identity
verification; neither is a tracked game resource or runtime substitute.

## Remaining accepted item

Required management `back_4/back_4_anim` dynamic header art/text and ordinary
management data/text rendering remain the only implementation item after live
animation qualification. Gate13 stays open until that item and the four ROADMAP
criteria pass. Do not create new blockers for optional fidelity refinements.
