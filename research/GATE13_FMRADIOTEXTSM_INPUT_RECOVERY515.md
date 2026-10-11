# Recovery 515: original fmRadioTextSm input dispatch and selected Premier0 Fixtures integration

**11 October 2026 KST. Gate 13 remains OPEN.** Original executable identity: authorized private root `footballmanager.exe` size 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Re-read from canonical private disc in this recovery, not executed. No private executable/disc bytes are stored in Git. This is a **static source trace**, NOT observed-original GUI interaction or Windows 11 visual acceptance.

## Bounded source results

- `PLeagueFixtures` constructor `0x46B022..0x46B20B` registers the six candidate League `fmRadioTextSm` children, native event IDs 9–14; previous Recovery506 documents their 182x18 rectangles at x27, y445+20*i and country event IDs 1–8.
- `fmRadioTextSm` vtable at `0x7D6AB8`; its slot `+0x6C` points to handler `0x5D4AC0`. Original `0x5D4790..0x5D47FB` iterates the parent's `+0x2C` child vector (count `+0x34`, 8-byte entries), requires per-entry mask bit `0x4`, consults `0x64F570`, then calls the child's vtable `+0x6C` at `0x5D47E8`. This proves *child dispatch structure*, not which on-screen mouse points are accepted.
- Original handler `0x5D4AC0..0x5D4B43` requires child `+0x18` flag bit1; distinguishes `+0x38` state, `+0x20` callback availability, and `+0x40` selection; for the callback branch calls interface at child `+0x24` vtable `+0x0C` (predicate) and `+0x10` (effect), then selected-control virtual `+0x98`. Neither callback identity nor complete coordinate/parent clipping ownership was closed.
- Current normal host `reconstruction/original_game_host.py:on_click` accepts PMenu/Squad/fixture paging/grid but has no source-verified native League country/choice radio pointer dispatch. Existing presenter method `source_accepted_league_fixtures_radio_event` is intentionally non-pointer. **Do not wire raw candidate geometry as accepted clicks** until original callback/hit ownership is traced.

## PR581 reviewed integration checkpoint

PR #581 source-selected Premier0 Fixtures was corrected after exact-head full reconstruction run 38096489409 failed seven cases solely from synthetic `comp()` definitions lacking `scheduled_matchday_count`. Commit `602abe2498ee18f649a885cfe50580b9d82b7224` adds the known 38 matchdays to the synthetic setup without weakening production validation. Exact-head CI: Gate13 run **38098272215 success**, reconstruction run **38098272357 success**, asset run **38098272311 success**. Independently checked merged branch against main, no active review concerns or Codex R1 overlap; merged PR581 with SHA guard as **`b8ab50fb657d4b466107847e5d143b2c2f4c9c59`**.

It supports source-qualified read-only alternate Premier0 fixture grid, 20 real members/380 fixtures, original primary bucket order, CP1252 ranking, strict status/membership/date/result; **not** native mouse controls, native match-detail links, actual Windows11 click test, other missing management/multi-manager pathways or release. Gate 13 and Gates 14–17 remain open.

## Exact next action

Trace `fmRadioTextSm` child callback `+0x24` predicate `vtable+0x0C` from the source-valid original registration and `0x5D4790` parent to screen-origin transform / hit / routing through `PLeagueFixtures::0x46E040`. Identify enabled/hidden controls, caption and art ownership. Once fully source-proven, add the smallest actual normal-host GUI radio press dispatcher on a disjoint worker branch with event/selection/visible integration tests; do not edit Codex R1 NEXT/PPreMatch/PResults files. Keep broader original Squad, Inbox, Save/Load, 2–6 human managers, all Leagues and full Windows11 playtest on the critical-path inventory.

## Recovery 516: callback destination confirmed, actual native click still NOT established

Additional disassembly of the same verified private original executable corrects and narrows the missing callback identity, **without asserting real mouse acceptance**:

- `PLeagueFixtures::0x46AA70` initializes `ebp=0` at `0x46AA75`. In the child constructor at `0x46B02F..0x46B048` it passes `esi` (the panel instance) and `ebp` (initially null) into child vtable `+0x08`. The child's vtable `0x7D6AB8` resolves `+0x08` to `0x5D48C0`, which calls base `0x64F3C0`; that writes child `+0x20 = ebp` and `+0x24 = esi`. Thus the original panel is the nominal callback target, **but the initial callback enable argument is zero**. Do not treat a nominal vtable link as proof it fires on ordinary clicks.
- Original `PLeagueFixtures` vtable `0x7C24B8` confirms `+0x0C → 0x42DE00` (returns 1) and `+0x10 → 0x46E040` (the panel event switch). Inside `fmRadioTextSm::0x5D4AC0`, `+0x20` must be nonzero to enter the `+0x24` callback branch. Whether and when the real UI supplies that enabling value is still UNKNOWN.
- Base `0x64F3C0` writes both callback fields and source `0x64F380` places the original 182x18 child rect. Child vector entry masks and `0x64F570` bit0 gate at `0x5D4790` confirm dispatch plumbing, but **no closed mouse button → screen-local hit-tested control → radio state transition → PLeagueFixtures event trace yet exists**.
- `PLeagueFixtures::0x46E040` is positively identified as the original panel event switch; it branches on original event ID from event `+0x20` (native country events1–8, League9–14). This proves effect dispatch only, not the original GUI mouse event producer.

**Narrowed exact next step:** disassemble/trace root mouse-message processing, original control rectangle hit-test and any later assignment of `fmRadioTextSm+0x20` enabling callback before any host pointer integration. Specifically distinguish virtual child `+0x6C` routed by parent from ordinary WM_LBUTTON actions and confirm source input path to panel `0x46E040`; preserve fail-closed native GUI until positively verified. No code/CI/GUI claims from this addendum.
