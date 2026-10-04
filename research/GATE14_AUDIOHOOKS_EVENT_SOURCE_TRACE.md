# Gate 14 AudioHooks sender source trace

_Status: source-backed numeric sender structure only. Gate 13 remains Codex-owned._

## Result

Recovery 278 closes the original AudioHooks object/dispatch path far enough to
replace the earlier direct-CALL-only hypothesis.

The canonical executable proves:

- RTTI-backed AudioHooks vtable: `0x7D73EC`;
- vtable slot 0 target: `AudioHooks::0x5DBFC0`;
- vtable installation at `0x5DC2B6`;
- global AudioHooks object pointer store at `0x5DC2BC -> 0x984810`;
- ordinary senders load the object through global `0x984810`, load slot 0
  from its vtable, and call that slot indirectly.

The earlier direct `CALL 0x5DBFC0` scanner is therefore retained only as an
auxiliary/negative trace path. It is not the main native sender mechanism.

No human-readable event or sample meanings are assigned.

## Dispatcher calling convention

`AudioHooks::0x5DBFC0` source-closes a three-dword callee-clean stack
contract:

- arg1 / numeric event ID: `[esp+4]`;
- arg2 / numeric state value: `[esp+8]`;
- arg3: `[esp+12]`;
- every dispatcher return uses `ret 0x0C`.

The dispatcher reads arg1 and arg2, but no path in the recovered function reads
arg3. Therefore arg3 is source-closed as part of the call convention but
**unused by this dispatcher implementation**. It must not be assigned a
meaning from neighboring callers.

## Literal virtual sender tuples

The following callsites have all three AudioHooks arguments as immediate
literals immediately before the slot-0 virtual call.

Tuple format:

`(callsite, event arg1, state arg2, third arg3)`

| Callsite | Event | State | Arg3 |
| ---: | ---: | ---: | ---: |
| `0x468720` | 1 | 1 | 0 |
| `0x468781` | 1 | 1 | 0 |
| `0x47AD13` | 13 | 0 | 0 |
| `0x4B6822` | 1 | 1 | 0 |
| `0x4B6868` | 1 | 1 | 0 |
| `0x4B9297` | 1 | 2 | 0 |
| `0x4B994F` | 1 | 1 | 0 |
| `0x4B9AC0` | 1 | 1 | 0 |
| `0x4D707F` | 19 | 0 | 0 |
| `0x5EC1BC` | 11 | 0 | 0 |

These are numeric source facts only. Event 1, 11, 13, or 19 is not named.

## Dynamic control-sender family

A second exact family appears in generic control code. These sites first call a
virtual method on the control object, retain the returned `EAX` as AudioHooks
arg1, and reuse two already-pushed numeric values for the AudioHooks call:

- state arg2 is the literal control-state index;
- arg3 is literal `0x40`;
- event arg1 is the prior control-method return value and is **not** guessed.

Source-closed sites:

| AudioHooks callsite | State arg2 | Arg3 |
| ---: | ---: | ---: |
| `0x64F7FE` | 0 | `0x40` |
| `0x64F88B` | 1 | `0x40` |
| `0x64F923` | 2 | `0x40` |
| `0x64F9BE` | 3 | `0x40` |
| `0x64FA4B` | 4 | `0x40` |
| `0x64FAE3` | 5 | `0x40` |
| `0x64FC31` | 6 | `0x40` |
| `0x64FC91` | 7 | `0x40` |
| `0x64FD1B` | 8 | `0x40` |
| `0x64FD8B` | 8 | `0x40` |

This closes the sender shape without equating the dynamic return value to any
specific AudioHooks event ID.

## Tracer update

`reconstruction/gate14_audiohooks_event_source_trace.py` now has two source
paths:

1. the older direct-target scan for `CALL 0x5DBFC0`;
2. a global-object virtual sender scan that recognizes:
   - `MOV reg,[0x984810]`;
   - a vtable load from that object;
   - an indirect slot-0 call through that vtable register.

For each virtual candidate the private report retains:

- global-load VA;
- indirect callsite VA;
- slot byte offset 0;
- bounded linear instruction context;
- nearby push operands as neutral candidates.

The automated scanner still labels raw decoded sites
`...not_cfg_or_semantic_proof`. The source-closed literal/dynamic tuples above
come from manual canonical-executable adjudication of those exact call
contexts.

## Fidelity boundary

This checkpoint may promote:

- AudioHooks RTTI/vtable/global-object path recovery;
- three-stack-argument calling convention;
- event/state/third argument positions;
- proof that the third argument is unused by `0x5DBFC0`;
- the exact numeric literal sender tuples above;
- the exact dynamic-control sender shape above.

It does **not** promote:

- human-readable event names;
- UI action meanings;
- match-event meanings;
- sample meanings;
- equality between AudioHooks numeric IDs and unrelated reconstructed enums.

Decoded audio remains non-evidence for naming events.

## Next source step

Continue from the sender side rather than the dispatcher:

1. source-close the remaining non-literal virtual sender candidates where event
   or state is derived from registers/data flow;
2. tie only directly proven sender contexts to higher-level native classes or
   event constructors;
3. add semantic names only when that source path itself establishes the meaning;
4. keep BNK sample interpretation separate from sender semantics.

No proprietary executable bytes, generated disassembly, BNK bytes, or decoded
PCM belong in Git.
