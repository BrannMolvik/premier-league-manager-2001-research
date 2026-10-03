# Application-owned management shell: bounded owner trace

3 October 2026 KST; canonical executable SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Raw disassembly stays private. These findings extend, rather than replace,
the earlier negative **PMenu-specific** background-ownership result.

## CONFIRMED: management entry refreshes application-owned art

Management entry `0x4C2FB0` first calls application method `0x432BA0`
through global object `0x87567C`, before constructing PMenu. That method calls
`0x432A20`, then loads handle `0x943BB0` through `0x64DB90` from:

`fm2001_art/generic/background_buttons/back_2_<variant>.444`.

The exact switch input is the dword at `+0x10` of the object returned through
`0x4139D0 -> +0x5B4`. Its domain must not be renamed “country ID” merely from
the resource labels: runtime club country is recorded elsewhere at `+0x14`.
The jump table at `0x432CD8` and byte selector table at `0x432CE8` prove:

| Selector input | Variant |
| --- | --- |
| 0 | `Premiership` |
| 21, 22 | `Bundesliga` |
| 50, 51 | `Lnf` |
| other values | `generic` |

Inputs above unsigned `0x33` take generic directly. A failed first resource
load retries `back_2_generic`. Case-insensitive disc catalog paths exist for
all four variants (sizes 18376, 22728, 17444, 11984 bytes respectively).

Static wrapper setup `0x5FA4A0` binds handle `0x943BB0` to wrapper
`0x943B90` with source rectangle `(0,0,385,95)`. Application setup
`0x430602..0x430628` binds that wrapper to embedded control `+0x270`,
at local position **(171,0)** through `0x651BA0`. The refresh method invokes
that control's slot `+0x30` after changing the resource.

This source-closes one application header fragment's owner, variant selection
and local placement. It does **not** close the complete 800x600 shell.

## CONFIRMED: base image is dynamically replaced

Application setup `0x4304EC..0x430559` initially binds a full **800x600**
wrapper `+0x17C` to handle `0x941310`, then assigns it to control `+0x19C`
at `(0,0)`. Static initializer `0x6001C0` binds that handle to the literal
`FM2001_art/generic/bground.444` at `0x82A054`.

However, management refresh `0x432A20` obtains a cached/generated image through
`0x5D3490 -> 0x5D3560`, takes its `+0x14` result via `0x5D3510`, stores that
at application `+0x174`, then replaces wrapper `+0x17C` at `0x432B38..0x432B3E`.
The cache key includes the selected object and option-derived value.

Therefore using the front-end `bground.444` as the **live** management base
would still be unsupported. The previous default-only provenance warning is
now narrowed: initial binding is confirmed, but the normal refreshed image
requires the generator/cache path. No background rendering change or new asset
import is made on the strength of this incomplete trace.

## Exact next native task

Trace image creation/cache method `0x5D3560` and the option value selected by
`0x64CCD0` from `0x9847FC` / table `0x83339C`; identify the final image's
resource inputs/composition and verify the application parent's origin and
draw order. Only then integrate the management base plus the confirmed header
fragment and refresh the Windows receipt. Ordinary fixture-cell hit-testing
and linked-context PMatchInfo remain a separate subsequent task.
