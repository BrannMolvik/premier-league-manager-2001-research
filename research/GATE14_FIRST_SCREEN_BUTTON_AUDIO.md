# Gate 14 first-screen Button numeric audio route

_Status: source-backed numeric route only; Gate 13 remains the earliest incomplete validation gate._

## Result

The original first-screen Button path can now be connected to the already
recovered AudioHooks numeric dispatcher without naming a sound by ear.

For an **accepted, enabled** press on any of the six verified PStartMenu or
TeamSelect action buttons, the source path sends:

`AudioHooks(event=10, state=0, arg3=0x40)`

The recovered AudioHooks switch maps numeric tuple `(10, 0)` to
`menus.bnk` sample slot **2**.

Neither event 10 nor slot 2 receives a human-readable meaning in this
checkpoint.

## Why event 10 is source-closed

### Constructor field

Button constructor `0x652FD0` forwards its eleven arguments unchanged to
`0x651E30`.

`0x651E30` stores its fourth argument at Button offset `+0x34`.

The Button AudioHooks selector `0x6528A0` uses that field:

- `+0x34 == 0` -> numeric event **2**;
- `+0x34 != 0` and native group 2 -> numeric event **2**;
- `+0x34 != 0` and native group 0/1 -> numeric event **10**.

### Verified first-screen constructors

The four already recovered PStartMenu action buttons are constructed at:

- `0x4C1C84`;
- `0x4C1CDF`;
- `0x4C1D3C`;
- `0x4C1D9A`.

In each case constructor argument 4 is the caption source pointer already used
by the verified original-text renderer.

TeamSelect Back at `0x4D88BA` passes the dereferenced caption global rooted at
`0x98211C`.

TeamSelect Start at `0x4D8921` calls `0x4D9270`, which returns the
dereferenced caption global rooted at `0x982124`, and passes that value as
constructor argument 4.

The reconstruction already requires these caption sources for the verified
first-screen visual path. They are therefore the same non-null source class
used by the native Button selector rather than an inferred replacement field.

## Owner acceptance

The pre-audio owner gate in `0x64F7A0` dispatches virtual slot `+0x0C`
when the Button has an owner/callback context.

For the two first-screen owners this gate is source-closed:

- PStartMenu vtable `0x7C64E0`, slot `+0x0C` -> `0x42DE00`;
- TeamSelect vtable `0x7C7650`, slot `+0x0C` -> `0x5CFA50`.

Both targets are exactly `mov eax,1; ret 8`. Therefore these owner methods
accept the press at this pre-audio gate. This does not bypass the Button's own
enabled/capture checks, and it does not claim that every later gameplay/session
operation succeeds.

## Press ordering

Generic Button press handler `0x64F7A0` first rejects controls whose enabled
bit is clear or whose capture gate rejects the press.

For an accepted enabled press it then:

1. loads the global AudioHooks object;
2. pushes arg3 `0x40`;
3. pushes state `0`;
4. calls Button vtable slot 0 to obtain the numeric event;
5. sends that event through AudioHooks at callsite `0x64F7FE`;
6. only afterward calls the Button state-changing virtual at `+0x1C`.

Thus the audio selector sees the **pre-press** native animation group.

The already recovered enabled groups 0 and 1 both select event 10 when
`+0x34` is present. Disabled group 2 cannot reach this AudioHooks send through
`0x64F7A0` because the handler rejects it earlier.

## Reconstruction contract

`reconstruction/gate14_first_screen_button_audio.py` records the exact numeric
route and provides a fail-closed playback adapter that feeds event 10/state 0
into the existing verified menus-bank PCM path.

The adapter deliberately does **not** claim that it is already bound to the live
PStartMenu/TeamSelect input host. That final binding must preserve the native
owner-acceptance boundary and event ordering rather than simply playing audio
for every rectangle hit.

The checkpoint therefore keeps all of these false:

- human-readable event semantics;
- sample meaning;
- live front-end audio binding;
- real-Windows audibility verification;
- login/menu audio integration;
- Gate 14 completion.

## Next step

The native first-screen owner acceptance gate is now source-closed. The next
integration step is to wrap the existing verified first-screen Button press
boundary without editing Gate-13-owned presentation code, preserve the Button
enabled/capture checks, and route the accepted numeric tuple through the
existing menu PCM backend. Then rerun the strict Windows audible receipt.

Do not use later modern backend rejection (for example an unavailable gameplay
continuation) as a substitute for the earlier native Button acceptance order.
