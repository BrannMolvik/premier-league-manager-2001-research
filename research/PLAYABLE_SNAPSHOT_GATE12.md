# Gate 12 playable snapshot

This branch is an isolated play-test surface created while the main FM2001
reverse-engineering worker continues on `main`.

## Branch boundary

- Branch: `playable-snapshot-gate12`
- Base main commit: `3c73b3b059c5c5957e6eac87e834c4d6f86322f3`
- Do not treat this branch as the canonical reconstruction state.
- Do not merge presentation changes into `main` while the active worker is
  changing backend behavior unless they are deliberately reconciled first.

The snapshot uses existing reconstructed APIs rather than reimplementing match,
competition, transfer, training, finance, youth, scouting, or save logic.

## Launch

From the repository's `reconstruction` directory on Windows:

```text
RUN_CURRENT_PLAYABLE.cmd
```

The launcher defaults to `C:\Games\FM2001`. If the canonical files are not
there, a folder picker asks for the FM2001 installation directory.

The runtime expects the canonical local files already required by the project,
including:

- `Master.dat`
- `Static.dat`
- `Core.str`
- `English.str`
- `FOOTBAL.EXE`

## Current exposed gameplay

The temporary shell exposes:

- choose a Premier League club and start a human-manager game;
- automatic legal 11+5 selection plus manual XI/substitute changes;
- formation and tactical controls;
- the shared Gate-12 Premier League/domestic-Cup human match path;
- league table and match-result log;
- internal `.fm2k` save/load;
- per-player training-method assignment;
- scouting search;
- ordinary cash bids and player contract offers;
- scheduled-transfer processing;
- live controlled-club Balance/ledger state;
- chairman financial-objective selection;
- youth-list initialization, promotion and release;
- reconstructed contract-renewal and player-transfer-request queues.

## Intentional limitations

This is not Gate 13 and does not claim original UI fidelity. It is meant to
answer the practical question: "What does the reconstructed game feel like if
we put a usable shell around the backend we have today?"

Known open backend fidelity remains governed by
`research/CURRENT_STATE.md` on `main`. In particular, the active worker is
still extending Gate 12 beyond the domestic-Cup slice and closing post-match
fidelity boundaries.

Original front-end presentation, audio, FastView/3D, packaging, and final
Windows release work remain later roadmap gates.
