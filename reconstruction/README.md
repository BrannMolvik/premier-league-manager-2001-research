# FM2001 clean-room reconstruction prototype

This directory contains clean-room code only. It does **not** include EA game data or executable code.

The parser reads a user's existing FM2001 files:

- `Master.dat`
- `Core.str`
- `English.str`
- `Static.dat`

Current reconstruction support also includes a tested implementation of the verified player development/training core in `player_development.py`.

Current parser support includes:

- corrected Master.dat club/player/manager boundaries;
- 1,246 clubs, 30,064 players and 1,612 managers;
- club names, stadiums and manager links;
- player names, current club links, dates, height/weight and positions;
- both verified 17-byte player skill arrays;
- complete 17-skill ordering;
- exact FM2001 raw-byte -> 0..30 display conversion;
- manager names, DOB, joined-club dates and club links;
- Static.dat position names.

Run:

```
python verify.py C:\Games\FM2001
```

to validate the exact analyzed release, or run `RUN_PROTOTYPE.cmd` on Windows to open the small Tkinter data browser.

The reconstruction code is intentionally data-free. Research evidence, addresses and confidence levels live under `research/`; this code should only be updated when those semantics are verified.

## Current gameplay status

This is still a data/reconstruction prototype, not a complete playable replacement.

Implemented and unit-tested reconstruction mechanics:

- monthly 17-skill age/development curve;
- exact peak-age grouping and shipped peak-range behavior;
- post-age monthly training modifier behavior;
- exact seven training profile vectors;
- Youth Team Coach / Assistant Manager / Training Centre quality multiplier;
- active-training success threshold and strict +8/-8 raw-skill steps.

Not yet implemented as gameplay:

- season simulation and AI;
- full transfer/finance behavior;
- save-game compatibility;
- match engine;
- FastView / 3D match presentation.
