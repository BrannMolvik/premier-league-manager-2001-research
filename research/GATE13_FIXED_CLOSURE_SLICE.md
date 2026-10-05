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

## Remaining accepted item

Required management `back_4/back_4_anim` dynamic header art/text and ordinary
management data/text rendering remain the only implementation item after live
animation validation. Gate13 stays open until that item and the four ROADMAP
criteria pass. Do not create new blockers for optional fidelity refinements.
