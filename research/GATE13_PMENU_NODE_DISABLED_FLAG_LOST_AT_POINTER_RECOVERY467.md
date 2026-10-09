# Recovery 467 — PMenu native disabled-node guard lost in ordinary mouse-path snapshot

_10 October 2026 KST. Strict audit-only cross-branch source/code inspection. No runtime modification or native executable launch._

## Canonical refs and evidentiary scope

- GitHub `main` `b7f2c58b2f1d6dc59b5f1102f188f159976105f1`, `reconstruction/original_game_host.py` blob `76820796c9bbf4a51b6972fd9f88099b734c1a91`.
- Codex branch `codex/gate13-windows-playability-recovery` `0ae745d1b56f45cade460f03cd893849a2f53b45`, `reconstruction/original_game_host.py` blob `14c4436d600aa2a397779d6fe22cdc74b742bf26`.
- Both use identical `reconstruction/original_pmenu_activation.py` blob `d5f546f5d82f554afc014443a874ad174a985280`; snapshot presenter on `main` blob `aa96fbe386a4be18480e27ffe3e58b3ef9ef3cdf`.
- Native proof relied upon: `research/GATE13_PMENU_ALL_28_NATIVE_DISPATCH_AUDIT_2026-10-09.md`, which reports a separately verified, SHA256-gated original `footballmanager.exe` `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` and `PMenu::0x47AD60` source node `+0x14` bit-0 and bit-1 selection gates. **This recovery did not rematerialize or rehash the original**, did not re-run original Windows GUI and does not independently prove when original nodes become disabled.

## CONFIRMED present-code disconnect (PARTIAL source equivalence)

1. `original_pmenu_activation.py:141–205` accepts full integer `source_flags`; bit 0 blocks selected children, and `PMENU_SOURCE_GUARD_BIT_1 = 0x2` blocks a child before native factory dispatch. This is unit-tested in `test_original_pmenu_activation.py:98–111` using a direct `resolve_pmenu_row_action("child", 0xCA, 0x2)` call.
2. `original_pmenu_presenter.py:35–59, 138–177` projects visible menu rows with `selected` and `expanded` booleans but **no per-node source disabled/guard flag**. It invokes `pmenu_static_row_state(kind, selected=...)` with no `disabled` argument. The function `original_pmenu_chrome.py:153–180` does support a `disabled` input and explicitly maps inverse source bit1 into enabled draw state, but the visible-row producer leaves its default `disabled=False`.
3. The ordinary management `on_click` path on `main` at `original_game_host.py:2074–2093`, and on Codex at `original_game_host.py:2385–2404`, computes `source_flags = 1 if candidate.selected else 0`, then passes the fabricated value to `resolve_pmenu_pointer_press` and `source_accepted_pmenu_action`. Its bit1 can **never be set**. The recovered resolver's bit1 gate therefore cannot be exercised through those user-visible pointer routes, even though the isolated helper test passes.
4. This is a representation/integration gap, **not a verified report of a particular disabled button misfiring**. The original runtime producer/conditions for +0x14 bit1 per concrete menu row, any frame-by-frame disabled transitions, and Windows11 effects require source/live evidence. Do not set all nodes disabled, assume all enabled, or use the isolated guard-test result to certify the host.

## Codex-only minimum correction recommendation

Preserve source node `+0x14` flags (or a source-proven derived equivalent) through menu model → row snapshot → visual disabled styling → actual pointer callback. Verify title versus child guard order, selected/expanded behavior, and dynamically guarded child refusals against original node-state producers. Add **ordinary on_click path** regression for a child whose source bit1 is set and a source-qualified enabled counterpart; assert gated child cannot open a panel or mutate selection. Recheck multi-club/state behavior and interaction frames on Windows before claiming original-fidelity.

This is lower priority than currently broken ordinary NEXT/MATCH, EAMail, formation, Save/Return and 2–6 manager paths unless the missing bit gates directly affect those routes. No test/CI, code implementation, original process, Codex branch edit, merge, or gate close was performed. Gate13 OPEN; Gates14–17 and original-scope release INCOMPLETE.

**Next independent audit target:** trace a source-backed P0-A menu node bit1 **producer and lifecycle**, not just its known consumer, preferably on an interactive menu whose outcome is otherwise implemented. If original binary access is unavailable, continue source-backed P0-B/P0-C actionable navigation audits without inventing the node state.
