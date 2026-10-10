# Recovery 443 — PResults shared bottom graphic: original source resource and negative return-action audit

_9 October 2026 KST. Source-first P0-D functionality audit; review of previous Recovery442 PResults callback. This is **audit only**. Neither original executable/resource binaries nor code/assets/saves are committed. No Codex branch changes, CI or Windows 11 acceptance._

## Verified canonical original provenance

Reverified the authorized disc-root `footballmanager.exe` at 4,714,541 bytes, SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. The authorized original MODE1/2352 Joliet disc image was read locally, without executing the original game.

**Exact original graphic:** `FM2001_Art/Generic/Waiting/waiting_back_2.444`. Original disc Joliet entry physical LBA **152281**, **46,448 bytes**, header width/height **800 × 87**, SHA-256 **`289b692919b3048bbe932eaf83083c622089fe4367d8124cd26a8bbf566899e5`**. Executable literal string VA **`0x835950`**, source loader **`0x5F4330`** -> raw resource **`0x946650`**, native wrapper initializer **`0x5F4380`** installs picture wrapper **`0x946630`** cropping (0,0,800,87). Resource name, identity, atlas geometry and crop dimensions are source-proven, not inferred from the visible appearance.

## Cross-owner original control provenance: PBg and PResults

The **same** original wrapper `0x946630` is passed into `0x651BA0` in both:

- Shared management **`PBg::0x430A0C..0x430A2F`** — child at **`PBg+0x5BC`**, owner PBg, original control ID **0**, native setup arguments include `(x=0,y=0x201=513)`, native graphic derives 800×87 from the wrapper;
- **`PResults::0x4A6E6B..0x4A6EA6`** — child at **`PResults+0x16C`**, owner PResults, original control ID **0**, identical setup call with source wrapper and origin `(x=0,y=513)`.

`0x651BA0` recovers width/height from wrapper `+0x14/+0x18` when wrapper is present and calls `0x64F380` to set control local rect. Source code in `0x64F380` places `(x,y,x+width,y+height)` in control `+0x08/+0x0C/+0x10/+0x14`. Since verified PResults original panel rect is 800×600 at (0,0), the **shown resource region** is the bottom `x∈[0,800), y∈[513,600)`.

Its control concrete vtable **`0x7BE530`** has `+0x08 -> 0x64F3C0` (registers ID into child `+0x20` and owner into child `+0x24`), and **`+0x6C -> 0x64F7A0`** (original bitmap-control input method).

## Critical correction: a visible graphic is NOT sufficient to establish a return button

Recovery442 independently proved native `PResults` final vtable `0x7C4B84`, callback **`+0x10 -> 0x4A87E0`** which, **when invoked with a non-null argument**, calls `0x4C2FB0(1,0,1)` to reconstruct PMenu. **That callback itself remains correct.**

However, this recovery verifies the **control-to-callback missing gate**. The first PResults graphic child above is registered with **ID zero** because `0x4A6E8D..0x4A6E95` passes `push ebp`, with **EBP explicitly zeroed at `0x4A6E54`**, into virtual `+0x08=0x64F3C0`. In original `0x64F7A0`:

- source flags at control `+0x18`: bit **0x02** required, **0x10** blocks input;
- at **`0x64F7C0..0x64F7E1`**, it tests **control `+0x20` (ID)** and only asks parent `+0x0C` permission if **ID ≠ 0** and there is an event/context object;
- after control-local pressed state, at **`0x64F80A..0x64F81F`** it again checks that **control ID ≠ 0** and callback context before invoking **parent virtual `+0x10`**. When ID is 0, the parent call is skipped.

Consequently, **even if** the graphic's native input control receives an accepted pointer event, its original zero ID means `0x64F7A0` does **not** dispatch that event to `PResults::0x4A87E0`. The prior provisional suggestion that this bottom strip is the return button has been **falsified** by the actual native input source. It would be a functional fidelity bug to wire a clean-room click anywhere in `(0,513,800,87)` to PMenu solely because the graphic and a panel return virtual both exist.

The `PResults::0x4A6E50` initial setup registers its other embedded control children at `+0x1A0,+0x1E0,+0x220,+0x270` with the **same ID zero**, making these static initial registration calls insufficient to identify the actual trigger. **Do not assume** they can never receive dynamically assigned IDs or other owner events later: that requires live/native caller evidence.

**Fidelity classification:** Original resource/rect/initial ID/input gate **EXACT**, original `PResults` callback **EXACT**, actual user input or state event causing a nonnull argument to that callback **UNKNOWN**. Modern reconstruction currently has no original results owner integrated into the default three-panel management host and lacks the normal NEXT click activation; this remains a **CONFIRMED P0 gameplay/navigation gap**, not fixed by the return-callback identity.

## Correct next source questions and Codex handoff

1. Source-trace **which native event producer actually invokes `PResults` virtual `+0x10`** with nonzero argument. Search child ID assignments/state transitions after `0x4A6E50` and parent callbacks via original event dispatcher; inspect `PResults` window state and keyboard behavior rather than guessing an image click.
2. Recover source conditionals and result payload/caption semantics for original NEXT `0x432190` and `PResults` `0x431F70`, including club/fixture state tests beyond Southport and original result-screen lifecycle/timing.
3. If the original route closes automatically or through an entirely different control, implement **that** minimal source-equivalent behavior. Do NOT invent a 800×87 button or a generic click-anywhere return. Preserve `waiting_back_2.444` as source-qualified shared art, not a navigation semantic.
4. Only Codex, as implementation owner, may modify reconstructed game/runtime or perform Windows-local acceptance. Our worker remains `audit_only` and source research/fidelity-ledger only.

No original runtime Windows measurement, tests/CI or gate closure here. Gate 13 is OPEN; Gates 14–17 and full shipped-scope Windows 11 release are incomplete.
