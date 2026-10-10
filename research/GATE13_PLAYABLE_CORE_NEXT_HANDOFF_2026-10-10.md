# Playable-core priority and NEXT integrity checkpoint — 10 October 2026 KST

Daniel's latest instruction supersedes the cosmetic-first queue. Work on
`codex/gate13-windows-playability-recovery`, not main. First deliver ordinary
New Game -> club -> Squad -> NEXT -> match -> result -> management -> continued
season -> save/reload. Then formation controls, real Inbox, essential PMenu
navigation and measured responsiveness. Preserve full original scope and the
audit-only worker. Gate13 remains OPEN; no main merge or runtime-owner change.

## Completed bounded implementation, not a playable milestone

Reconciled canonical main `fc857236c64b4a99feea10d9fc7e2eb5454f8944` into the
recovery branch, retaining both local verified work and all newer worker audits.
The only new behavior change is safe publication of the existing bounded NEXT
backend. `advance_original_management_turn` executes on an isolated controller
graph and publishes it only after the entire requested turn succeeds. Failure
leaves the original graph, including its date, RNGs, players, results, pending
state and transient transfer receipts, untouched. Successful publication keeps
the live controller identity; `ManagementSourceDataBridge.state` reads through
that controller. Immutable coefficient matrices are shared, not rebuilt.

Evidence and compatibility boundary:

- Recoveries457/460/465 establish the ordinary control/input ownership, existing
  due-wrapper rejection and multi-day partial-mutation risk. The original
  bounded day target and two-pass League processing are unchanged.
- This transaction is a reconstruction fail-closed safety mechanism, **not**
  evidence that the original executable implemented rollback this way.
- Unknown wrappers remain unknown. No date/score/header projection is promoted
  to an authoritative event, no simulation or report data is invented, and no
  original executable was launched.
- Controller consumers must obtain current state through the controller after
  successful publication. The existing management bridge does this; future
  live NEXT integration must reset transient drag/snapshot owners accordingly.
- Production calendar hooks are bound methods; the regression checks that their
  owners follow the staged/published GameState. Filesystem/resource loaders are
  read-only. This does not authorize arbitrary external side-effect callbacks.

Final verification:111 tests passed in8.697s across `test_original_management_turn`,
`test_original_management_advance`, `test_human_gameplay`, `test_internal_save`
including the published calendar-hook owner assertion; asset policy passed.
The two new refusal test methods deliberately reproduced three failed snapshot
comparisons with staging disabled: two independent single-manager club cases
and one later-day refusal after a real AI calculator result/RNG mutation. The
isolated successful-day test checks the live bridge/controller ownership.
Synthetic database/fault injection is explicit; these are not native runtime,
Windows pointer, canonical-world performance or playable acceptance receipts.

Private logs remain outside Git under the thread's `work` directory:
`next-atomic-red.log`, `next-atomic-focused-final.log`.

## Exact next vertical slice

1. Close and implement the source-qualified runtime NEXT event selector for the
   supported ordinary single-manager League path, separate from the display
   header. Reuse Recoveries447/448/462–465:payload mask0x61, original manager/Side
   reference identity, per-event wrapper state and local same/previous/next
   bucket resolution/recheck. Do not disable global invalidation without
   replacing the source producer lifecycle, or mark UNKNOWN as CLEAR.
2. Connect PBg childID3 at(700,0,100,95) using Recovery457's bit2/bit0x10 and
   owner/modal guards; preserve source roster eligibility/warnings and pending
   pre-match choice. Use the existing calculator, not prototype skip-to-fixture.
3. Integrate the recovered normal pre-match/results/return controls. Do not
   substitute a developer popup or assume any click dismisses PResults.
4. Test actual Windows mouse/keyboard across the full single-manager loop,
   including refusal snapshots, more than one real fixture, save/fresh reload,
   and staged-copy performance on canonical data. Only then deliver a playable
   original-look test build. No completed player action is claimed here.

Formation and EAMail independent source reports remain in private scratch.
They are next priorities after NEXT, not reasons to return to fonts/palettes.
The previous font snapshot0ae745d1 is only a presentation test. No new frozen
package or ordinary UI acceptance was performed in this checkpoint. The last
full-suite receipt remains NOT green due to the previously recorded disjoint
Gate17 package-lock failures; no waiver or release claim.
