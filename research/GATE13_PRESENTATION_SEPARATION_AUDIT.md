# Gate 13 Presentation / Simulation Separation Audit

_Date: 1 October 2026 KST_

## Criterion

Gate 13 completion criterion:

> Simulation logic remains separated from presentation code.

This criterion is now independently audited as **satisfied**. This does **not**
mean Gate 13 itself is complete. Original resources, layouts, navigation,
animation timing and recognizable FM2001 presentation remain open.

## Evidence

### Original first-screen path

`front_end_state.py` owns only recovered presentation/navigation state and
imports no simulation modules.

`front_end_session.py` is the application seam. Its module-level imports are
presentation/navigation types only. The canonical `HumanGameplayController`
adapter is imported lazily inside `make_gameplay()`; presentation import does
not initialize or own simulation.

`original_first_screen_presenter.py` composes verified original-source
resources and dispatches recovered pointer/navigation events through the
session. It imports no GameState, MatchCalculator, transfer, finance or player
runtime implementation.

### Management screens

`gate13_management_source_data.py` is a read-only, backend-type-agnostic
projection. At module load it imports only dataclasses/date support. It does not
import simulation packages and does not invoke simulation-mutating actions.

The bridge exposes only already recovered data required by future presentation:

- controlled-club source identity/date;
- source-order squad and fixture projections;
- persisted lineup/tactics/Team Orders;
- native-comparator-aware league table output;
- recovered player profile state;
- finance and transfer runtime data;
- mapped manager-mail queues;
- training state;
- mapped scouting result data.

Where native screen sorting, visual labels, control IDs or geometry remain
unknown, the bridge preserves neutral numeric/runtime identity or fails closed
rather than embedding guessed game rules in presentation.

### Temporary development UI

`app.py` remains explicitly a temporary Tk development surface, not the
FM2001 fidelity target. Its Play tab routes presentation reads through
`ManagementSourceDataBridge`. Commands such as select club, set lineup,
set tactics, advance and play remain controller actions.

`test_app_presentation_boundary.py` rejects direct Play-surface reads through
`controller.state`, `controller.human`, `self.gameplay.state` or
`self.gameplay.human`.

## Durable regression enforcement

`test_gate13_presentation_separation.py` additionally verifies:

1. `front_end_state.py` stays independent of simulation modules;
2. `front_end_session.py` does not import simulation at module load and keeps
   the canonical gameplay import nested in the lazy factory;
3. `original_first_screen_presenter.py` has no direct imports from the
   reconstructed simulation/runtime families;
4. `gate13_management_source_data.py` remains simulation-import-free and does
   not call the known mutating gameplay/finance/transfer actions.

The focused Gate13 workflow includes both this architecture audit and the
temporary-UI AST boundary test.

## Full integration baseline

Immediately before this audit, PR #33 updated the full-suite PR filter for the
Gate13 presentation seam and run `36760160986` passed **1,050 tests with 21
expected original-source-gated skips and zero failures** on
`818e91033ba0cb7f2c912c67badf58f06f38f098`.

This full hosted result proves code integration only. It does not execute the
licensed original-resource opt-in tests or a Windows 11 graphical build.

## Why the other Gate 13 criteria remain open

This audit intentionally closes only architecture separation.

Still open:

- actual private original-executable Button/Zurich trace;
- physical ten-resource source-byte/pixel audit;
- provenance import of verified original UI resources;
- exact original first-screen/control states and typography;
- original manager-screen layouts/navigation/timing;
- recognizable FM2001 normal-play presentation;
- native Windows 11 graphical/integration smoke testing.

Accordingly Gate 13 remains **ACTIVE**. Do not use this criterion's completion
to advance to Gate 14 until the remaining Gate 13 criteria are independently
audited.
