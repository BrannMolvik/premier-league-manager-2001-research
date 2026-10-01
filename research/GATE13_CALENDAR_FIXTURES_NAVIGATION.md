# Gate 13 Calendar, Tables and League Fixtures navigation identity

_Date: 2 October 2026 KST_

This checkpoint correlates four exact PMenu IDs to concrete original
presentation panels through the canonical executable's management panel factory
at `0x47AEC0`.

Trace source: canonical `footballmanager.exe` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

No original executable bytes or raw disassembly are stored in Git.

## Factory dispatch

For IDs `0x195..0x25B`, the factory computes `id - 0x195`, reads a dispatch
byte from `0x47CB14`, then jumps through the target table at `0x47CAF4`.
`0x25C` has a direct branch to its factory case.

The source-exact results are:

| PMenu ID | Original caption | Factory case | Constructor | RTTI class | TypeDescriptor | Vtable |
| ---: | --- | ---: | ---: | --- | ---: | ---: |
| `0x259` | Calendar | `0x47C62B` | `0x47CCB0` | `PCalendar2k` | `0x81CA18` | `0x7C2F04` |
| `0x25A` | League Tables | `0x47C6D1` | `0x448640` | `PLeagueTables` | `0x81B458` | `0x7C00C8` |
| `0x25B` | Cup Tables | `0x47C67E` | `0x44EC80` | `PCupTable2000` | `0x81BA30` | `0x7C0A78` |
| `0x25C` | League Fixtures | direct `0x47C724` | `0x46D470` | `PLeagueFixtures` | `0x81C550` | `0x7C24B8` |

The captions are independently exact from the Recovery-146 full
`English.idx` loader correlation, so the menu-node identity and the factory
panel identity agree without filename inference.

## Calendar

PMenu root ID `0x259` is the exact **Calendar** root and also the first child
of its own two-entry child array. The factory dispatch byte for index
`0x259 - 0x195 = 0xC4` resolves to case `0x47C62B`.

That case allocates 0x2CDC bytes and calls `0x47CCB0`.
The constructor ultimately installs vtable `0x7C2F04`; MSVC RTTI identifies
`.?AVPCalendar2k@@`.

This establishes a concrete original Calendar panel rather than a generic
calendar backend surface.

## League Tables and Cup Tables

PMenu TABLES children are exact IDs `0x25A` and `0x25B`.

- `0x25A` dispatches to `0x47C6D1`, constructs `PLeagueTables` through
  `0x448640`, vtable `0x7C00C8`.
- `0x25B` dispatches to `0x47C67E`, constructs `PCupTable2000` through
  `0x44EC80`, vtable `0x7C0A78`.

The League Tables identity was already known from the fresh PMenu route; this
trace places both table screens in the same exact factory/menu family and adds
the concrete Cup Tables panel identity.

## League Fixtures

PMenu Calendar-family child ID `0x25C` is exact **League Fixtures**.
The factory compares directly against `0x25C` and branches to
`0x47C724`.

That case allocates 0x126A8 bytes and calls constructor `0x46D470`.
The constructor installs vtable `0x7C24B8`; RTTI identifies
`.?AVPLeagueFixtures@@`.

This closes the previous Gate-13 **fixtures/results panel identity** gap for the
League Fixtures screen. It does not yet close row ordering, resource ownership,
exact geometry, controls, result-display behavior or navigation beyond the
source-proven PMenu edge.

## Reconstruction consequence

`reconstruction/original_management_navigation.py` now exposes only these four
source-proven identities and fails closed for IDs outside this recovered family.

The next source task should continue inside these concrete panels, prioritizing:

1. `PLeagueFixtures` original resource paths, row/list geometry, result/date
   bindings and sorting/navigation;
2. `PCalendar2k` source resource/layout bindings;
3. `PLeagueTables` / `PCupTable2000` visible row/header resources and
   geometry;
4. integrated PMenu navigation once the required source resources are
   intentionally imported.

This identity checkpoint alone does not claim those screens are visually
reconstructed.
