# Gate 16 autonomous transfer churn stress

_Date: 1 October 2026 KST_

## Scope

This is cloud-safe Gate-16 work-ahead while Gate 13 remains the earliest
incomplete validation gate. It targets a different long-duration risk from the
multi-season fixture stress: repeated autonomous club acquisitions and the
persistent runtime state they mutate.

`reconstruction/test_gate16_transfer_churn_stress.py` builds a synthetic
20-club world with 26 players per club and exercises the recovered Saturday
`0x40DD70` AI acquisition pass for **260 consecutive weeks (five years)**.

The fixture deliberately supplies only the source-backed dependencies needed by
that path: manager ownership, country transfer gate, fan-base seller floor,
position coverage, player valuation/wage rows, transfer runtime state and the
shared MSVC CRT RNG.

## Long-duration invariants

Across every weekly pass the stress requires:

- all 520 players remain owned by exactly one club roster;
- every runtime player's `club_id` agrees with its roster owner;
- no seller roster falls below the recovered 16-player synthetic floor;
- no club roster exceeds a generous 40-player corruption guard;
- direct autonomous acquisitions leave no pending proposal, deal, bid-log or
  scheduled-transfer objects behind;
- completed movement history grows exactly once per successful acquisition;
- every completed movement changes clubs and has positive consideration;
- movement dates stay ordered and occur on Saturday;
- the recovered >26-week current-club residency rule prevents any player from
  moving more than ten times in the 260-week window;
- a repeated run with the same CRT seed produces the same full movement,
  roster, counter and RNG signature;
- an independent second seed also survives the complete five-year run.

This makes completed movement history an **explained event-proportional growth
surface** while fail-closing on transient-container leaks or roster corruption.

## Evidence boundary

This test is intentionally synthetic and does **not** claim authentic
five-season FM2001 transfer frequency.

Two already-recorded fidelity gaps remain relevant:

1. later dated country transfer-window toggles are not yet fully reconstructed;
2. the exact update/reset lifecycle of the club `+0x1ED` autonomous buy
   counter remains unresolved.

The synthetic fixture therefore keeps the country gate open and allows the
currently persisted neutral buy counter to behave exactly as implemented. The
test checks safety, ownership, determinism and state-growth behavior without
using its transfer count as evidence for the original market cadence.

A pass strengthens Gate 16 but does not close it. Canonical real-data
multi-season evidence, broader competitions, additional unusual-state
combinations and remaining long-duration fidelity gaps are still required.
