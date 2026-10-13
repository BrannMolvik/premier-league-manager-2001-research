# Recovery580: first-human queue drain source ownership and CRT uncertainty

**13 October 2026 KST. Gate 13–17 OPEN.** Independent static source check of the original 4,714,541-byte `footballmanager.exe` with SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, using GNU `objdump -D -Mintel --section=.text`. **No original process launch, interactive Windows 11 test, or seed measurement.**

## First-human two queue-drain callsites

- `0x4258D0` user constructor begins the selected-user initialization, calls `0x42C400` at `0x4258F8`, then `0x42599E` sets **ECX = `0x947AA8`**, and `0x4259B5` calls native **`0x614080`**. Following this call, `0x4259C0` invokes `0x5CF830` with the current user +0x6B4 state.
- `0x412EF0` subsequent selected-user setup similarly sets **ECX = `0x947AA8`** at `0x412F0D`, and `0x412F1F` invokes the **same `0x614080`**. It first clears user+0x04 and sets user+0x9E4 to -1; these are *not* evidence that the global queue is empty.
- Native `0x614080` enters via **queue ECX**, checks queue+0x0C for reentrancy/busy (`0x614085`), defers by queue+0x10=1 if busy (`0x61408C`), otherwise traverses queue+0x04 linked nodes (`0x614097`). For each inner object it executes polymorphic **vft+0x04** (`0x6140A5`) and conditional **vft+0x18** (`0x6140B0/0x6140C7/0x6140D2`); when selected, native removal calls `0x4EA190` (`0x6140E0`). Thus this drain can invoke unknown child callbacks with possible other shared CRT reads; no direct rand in this *dispatcher* is insufficient to prove no RNG changes.
- **UNKNOWN:** queue head content before each first human drain, whether pending events are present, identity of each actual queued object, counts, callback branches, effects on shared CRT and their ordering relative to new-game seed.

## Correction to nearby XOR route

The two static `0x4AF7F0` calls `0x4AEA48/0x4AED01` belong under **PScouting2K** event ID31 (`0x7C2E6C` vtable RTTI `.?AVPScouting2K@@`), *not* a proven first TeamSelect manager selection. See `GATE13_MANAGER_EVENT31_XOR_RESEED_RECOVERY579.md` correction and `original_scouting_event31_reseed.py`. Do not append scouting reseeds to New Game shared CRT without a separate original input/caller proof.

## Verification and exact next action

Private original instruction checks passed for **12** drain/callback/queue sites and original PScouting2K RTTI/event table. New checks are appended to `audit_original_teamselect_continue_static.py` for reproducible re-run. This is SOURCE proof only, **not** an observable first-human seed/career simulation contract. **NEXT**: identify actual original producers that populate `0x947AA8` between game setup and first human selection, source-classify any queued object callbacks and their CRT effects, and collect real original player-process receipts when a separately approved safe source-valid Windows runtime is accessible. Do not guess queue emptiness or first-human draw count. The original 2–6 human, live PSupportStart editor, Inbox, R1 and all Gate13–17 Win11 release remain unfinished.
