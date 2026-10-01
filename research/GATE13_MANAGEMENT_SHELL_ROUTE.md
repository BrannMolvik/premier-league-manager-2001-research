# Gate 13 management shell and fresh-game landing route

_Date: 2 October 2026 KST_

This checkpoint corrects the roadmap-era assumption that a distinct generic
"Manager Home" content panel must exist between TeamSelect and normal
management play.

The trace was performed against the reverified canonical
`footballmanager.exe`, SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Raw disassembly and proprietary bytes remain outside Git.

## TeamSelect Start enters the management shell

The completed new-game path ends at:

```text
0x4C48D3 push 0
0x4C48D5 push 0
0x4C48D7 push 1
0x4C48D9 call 0x4C2FB0
```

`0x4C2FB0` allocates a 0xB8-byte object and calls constructor
`0x482830`. MSVC RTTI identifies its vtable `0x7C3DE8` as
`.?AVPMenu@@` (TypeDescriptor `0x81CE80`).

Therefore **PMenu is the source-proven management shell created after
TeamSelect Start**.

## PMenu chooses a real content panel

`PMenu::0x482960` reads the current user through `0x4139D0`, then reads a
neutral dword at user `+0x10E8` through getter `0x42C6A0`.

The route is:

| user +0x10E8 | PMenu panel code | companion menu node | factory target | concrete panel |
| --- | ---: | ---: | --- | --- |
| 0 | `0xCE` | 2 | `0x47AF2D` | `PSquadScreen` |
| 1 | `0x25A` | 6 | `0x47C6D1` | `PLeagueTables` |
| other | `0xCE` | 2 | `0x47AF2D` | `PSquadScreen` |

For state 1 and other nonzero values, `0x482A40..0x482A50` writes zero back
through setter `0x42C6B0`; state zero is already the steady default.

At `0x482B8A`, PMenu passes the selected node's `+0x0C` panel code to
factory `0x47AEC0`.

## Panel identities

### Code 0xCE

The factory's low-range jump table uses index
`0xCE - 0x65 = 0x69`. Byte table entry `0x47CA6D` selects factory case
`0x47AF2D`.

That case allocates 0x38F8 bytes and calls constructor `0x4B8240`.
The constructor installs vtable `0x7C5CA4`; RTTI identifies
`.?AVPSquadScreen@@` (TypeDescriptor `0x819D48`).

This independently joins the existing Squad resource/layout trace to the
actual management-shell navigation path.

### Code 0x25A

The high-range jump table uses index
`0x25A - 0x195 = 0xC5`. Byte table entry selects factory case
`0x47C6D1`.

That case allocates 0xA0C bytes and calls constructor `0x448640`.
The constructor installs vtable `0x7C00C8`; RTTI identifies
`.?AVPLeagueTables@@` (TypeDescriptor `0x81B458`).

The neutral +0x10E8 value therefore acts as a one-shot/steady routing state,
not as evidence of a generic home panel.

## Fresh users prove the initial route

TeamSelect club selection creates each user through `0x413BB0`:

```text
0x413BF0 allocate 0x10F0
0x413C0E call 0x424CA0   ; user construction
...
0x413C54 call 0x4258D0  ; bind clicked club / initialize user
```

Inside `0x424CA0`, the constructor uses zero in EBX and at
`0x424F36..0x424F45` pushes that zero and calls
`0x42C6B0`, storing **0 at user +0x10E8**.

Consequently, a newly created user reaches PMenu with route state zero and the
first source-proven management content panel is:

```text
TeamSelect Start
  -> 0x4C2FB0
  -> PMenu
  -> panel code 0xCE
  -> PSquadScreen
```

## Reconstruction consequence

"Manager Home" was a planning placeholder, not a source-proven standalone
fresh-game screen. It must not be invented merely to satisfy the old suggested
roadmap order.

The correct Gate-13 structure is:

1. PStartMenu;
2. TeamSelect;
3. PMenu management shell;
4. fresh-game content = PSquadScreen;
5. other source-proven PMenu routes, including the state-1 PLeagueTables route,
   are recovered as actual menu/panel navigation.

This does **not** claim that PMenu chrome, complete Squad composition, or the
League Table screen is visually finished. It closes only the panel identity and
fresh-game navigation boundary and removes an unsupported Manager Home target.
