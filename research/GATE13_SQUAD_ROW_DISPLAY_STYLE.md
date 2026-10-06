# Gate 13 ordinary Squad row display-style trace

_Last verified: 6 October 2026 KST._

## Scope

This note source-closes only the visible ordinary `PSquadPlayerRow` name
format, player-name status color hierarchy, and assigned-role compatibility
color. It does not infer the unresolved status icon, first/reserve filtering,
scrolling, post-event formation pixels, or the exact font file behind runtime
font slot `0x94758C`.

Canonical executable:

`footballmanager.exe` / disc `FOOTBAL.EXE`

SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

No executable bytes are committed.

## 1. Assigned-role compatibility predicate

The ordinary row constructor `0x489530` calls helper `0x4EA3F0` before
building the assigned-role text control.

`0x4EA3C0` returns the low five bits of the compact player-position object's
fourth byte. Existing source work binds that value to the player's current
assigned role.

`0x4EA410` compares an input role against the compact object's first three
bytes. Existing source work binds those three bytes to the player's preferred
role tuple.

`0x4EA3F0` composes those helpers, so its exact boolean is:

```text
current assigned role is one of preferred_positions[0:3]
```

The `PSquadPlayerRow` constructor branches on that result before constructing
the role text color:

- preferred/current role match: logical RGB `(255, 255, 255)`;
- current role absent from all three preferred roles: logical RGB
  `(125, 1, 0)`.

The original then packs those source components into the active display pixel
format. The modern presenter records the logical source RGB values rather than
hard-coding one packed 16-bit word.

## 2. Ordinary Squad display name is not the full first name

The row constructor calls `0x5D6C50` with:

- x = 76
- y = 1
- width = 144
- height = 14
- runtime font slot = `0x94758C`
- text flags = `0x21`
- player pointer
- name-format flag = 0

`0x5D6C50` refreshes the control through `0x5D7080`, which reaches shared
player-name helpers `0x417A90` and `0x417AE0`.

The executable contains two relevant format literals:

- `0x81858C`: `%s %s`
- `0x818EB0`: `%c. %s`

The row passes format flag zero, selecting `%c. %s`. Therefore a normal
ordinary Squad row displays:

```text
<first-name initial>. <surname>
```

Example: `David Beckham` -> `D. Beckham`.

The shared formatter contains one explicit exception: when the first-name
source string begins with `-`, it emits surname only.

The previous modern row presenter used `full_name` and was therefore not
source-faithful.

## 3. Name-status color priority

`0x5D6C50` evaluates four player predicates in a fixed priority order using
the row's own player identity.

The already reconstructed runtime meanings are:

1. `0x417EE0`: DBRPlayer `+0x14 bit 4` = match active
2. `0x417F00`: DBRPlayer `+0x14 bit 5` = substitute available
3. `0x417EA0`: DBRPlayer `+0x174 bit 0` = injured
4. `0x417EC0`: DBRPlayer `+0x174 bit 1` = suspended

The first true predicate wins. The logical source RGB components are:

| Branch | RGB |
| --- | --- |
| match active | `(255, 255, 255)` |
| substitute available | `(232, 191, 94)` |
| injured | `(176, 176, 176)` |
| suspended | `(185, 167, 131)` |
| default | `(217, 210, 62)` |

So a player who is both injured and suspended uses the injured branch, while a
selected substitute with injury/suspension bits present uses the substitute
branch because that predicate is tested first.

## 4. Runtime bindings already exist

The clean-room runtime already source-binds the four status inputs:

- `RuntimePlayer.match_active`, setter mirroring `0x4182F0`;
- `RuntimePlayer.match_substitute_available`, setter mirroring `0x4182C0`;
- `RuntimePlayer.injured`;
- `RuntimePlayer.suspended`.

It also already carries the exact current role and three preferred roles.

Recovery 330 therefore needs no invented simulation state. The management
source bridge can expose the existing immutable values and the read-only Squad
presenter can reproduce the exact formatter/status choice.

## 5. Fidelity boundary still open

The name control uses runtime font slot `0x94758C`. The executable's font
startup path establishes that this slot points at a concrete runtime font
object, but this recovery has not yet independently bound that object to one
specific imported original font file.

Accordingly this checkpoint closes:

- displayed name string semantics;
- role-compatibility color choice;
- name-status color choice and priority;
- control geometry/flags already recovered with the row.

It does **not** yet authorize guessed Squad glyph pixels. Host-side row
rasterization must wait for the exact font-resource binding or reuse a separately
proven binding if found elsewhere in canonical research.

## Modern representation

`reconstruction/original_squad_presenter.py` stores the source-qualified
results as:

- `display_name`;
- `display_name_status`;
- `display_name_rgb`;
- `assigned_role_is_preferred`;
- `assigned_role_rgb`.

The unresolved `club_relative_assignment` and `native_status_icon` columns
remain fail-closed.
