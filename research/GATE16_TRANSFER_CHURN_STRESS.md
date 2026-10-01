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


## First full-suite finding: month-end contract overflow

Reconstruction run `36837615509` did not validate this stress. It ran 1,129
tests with 22 expected source-gated skips and stopped with three errors, one in
each new transfer-churn test.

All three reached an existing long-duration defect in
`contract_expiry_from_month_span`: the recovered autonomous transfer path can
start a contract on day 29, 30 or 31 and later target a shorter month. The
clean-room helper preserved the day unconditionally, so Python raised
`ValueError: day is out of range for month`.

The source evidence already proves the contract-length unit and calendar-month
advance, but the exact original helper's normalization of an unavailable target
day is not yet instruction-locked. The private authorized source archive was
successfully recovered for this audit, but the current execution allocation
could not launch the process required to re-disassemble `FOOTBAL.EXE`.

The runtime therefore uses a deliberately bounded compatibility rule rather
than inventing original semantics: preserve the source day whenever it exists
in the final target month; otherwise clamp to that month's final valid day.
Focused tests cover ordinary, leap-February and multi-month boundaries.
`research/FIDELITY_GAPS.md` records the unresolved original normalization.

This section records the failed finding and the repair boundary only. A later
CI pass is required before the five-year transfer stress is treated as
verified.


## Verification

The bounded month-end repair and the original five-year stress were re-run
together in reconstruction workflow `36840977540`.

Result:

- **1,130 tests passed**;
- **22 expected original-source-gated skips**;
- **0 failures / 0 errors**;
- runtime: **278.116 seconds**;
- repository asset-policy run `36840977536`: **passed**.

PR #57 merged to canonical `main` as
`71676cb9a5b5b89b60b037c8f4426dc72a58e682`.

This verifies the synthetic transfer-churn/state-growth regression and the
month-end crash repair. It does not resolve the separately documented original
end-of-month normalization semantics, transfer-window dates, or autonomous
buy-counter lifecycle, and it does not close Gate 16.
