# Gate 14 AudioHooks numeric menu-sample dispatch

_Status: source-backed numeric routing only. Gate 13 remains Codex-owned._

## Result

The canonical original executable source-closes the numeric switch in
`AudioHooks::0x5DBFC0` that conditionally routes original event IDs to
literal sample slots in `menus.bnk` through helper `0x6CFF10`.

This checkpoint deliberately preserves the original numeric IDs rather than
inventing names for them. The repository does not yet prove that AudioHooks
event ID 17, for example, is the same semantic event as any reconstructed
FastView or MatchCalculator enum value.

## Switch boundary

The dispatcher covers original numeric event IDs 2 through 35. Its direct
menus-bank sample calls reach every nonzero slot 1 through 22. Slot 0 is not
passed by this dispatcher.

Unconditional routes:

| Event ID | menus.bnk slot |
| ---: | ---: |
| 17 | 6 |
| 18 | 7 |
| 19 | 1 |
| 23 | 16 |
| 24 | 17 |
| 25 | 16 |
| 26 | 17 |
| 31 | 20 |
| 32 | 20 |

Routes requiring the second dispatcher argument to equal zero:

| Event ID | menus.bnk slot |
| ---: | ---: |
| 5 | 11 |
| 6 | 12 |
| 20 | 13 |
| 21 | 15 |
| 22 | 14 |
| 27 | 8 |
| 28 | 9 |
| 29 | 4 |
| 30 | 5 |
| 33 | 22 |
| 34 | 21 |

Special predicates:

- event IDs 2, 3 and 4: slot 2 when state is 0 or 3;
- event ID 8: slot 10 when state is 8;
- event ID 10: slot 2 for state 0/3, slot 3 for state 6;
- event ID 35: slot 18 for state 0, slot 19 for state 1.

Switch entries 7, 9 and 11 through 16 do not call the menus playback helper.

## Fidelity boundary

`gate14_audiohooks_menu_dispatch.py` records only:

- the exact numeric switch range;
- literal menus-bank sample slot selection;
- the exact second-argument predicates.

It keeps these false:

- semantic event binding;
- human-readable sample meaning.

The fact that decoded audio is now available does not justify naming sounds by
ear or equating numeric AudioHooks IDs with unrelated reconstructed enum values.
A later source trace must identify the senders/callers that construct those
numeric event IDs before Gate-14 `audio_event_binding_recovered` can become
true.

No proprietary audio or executable bytes are committed.
