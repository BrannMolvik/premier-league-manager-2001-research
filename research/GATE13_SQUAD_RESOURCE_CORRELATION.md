# Gate 13 Squad Resource Correlation

_Date: 1 October 2026 KST_

## Evidence boundary

This report records the canonical-executable owner correlation for the four
exact files returned by the whole-disc Squad catalog query. The authorized ZIP
matched SHA-256
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4` and
the private `footballmanager.exe` matched
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
before the trace. Private exhaustive disassembly reports remain outside Git.

Filename and directory similarity were not treated as ownership. Each result
below requires the exact path literal, the loader/wrapper chain, a code
consumer, and an RTTI-backed owner where applicable.

## Exact catalog and loader bindings

| Exact source path | SHA-256 | Native size | Path literal / load thunk | Raw handle -> wrapper |
| --- | --- | --- | --- | --- |
| `FM2001_Art/Coaching/squad/blue_toggle.444` | `3fe515f5a4a2d798a8f62917a45047b274e08bd3e68147a4fe0e25dfbd1d3343` | 22x17 | `0x83827C` / `0x5FBDD4` | `0x943070` -> `0x943050` |
| `FM2001_Art/Generic/GenericButtonsAndBars/squad_bars.444` | `c0ba37cc991e5449830af3e550f14dc7d9444cc545e91fa7936dc38508c6110b` | 81x64 | `0x8394B8` / `0x5FF7F4` | `0x941750` -> `0x941730` |
| `FM2001_Art/Generic/GenericButtonsAndBars/squad_but_anim.444` | `6a5180d9212fe50418537fa181c44ba075bc0317c5bb55aed8b9c6a9e0fc0632` | 73x575 | `0x83943C` / `0x5FF6D4` | `0x9417D0` -> `0x9417B0` |
| `FM2001_Art/Generic/GenericButtonsAndBars/squad_form_anim.444` | `e4bcc6981cc99fde44b093696791a05f91100752559b0b2f12dc0c0177392828` | 23x368 | `0x839478` / `0x5FF764` | `0x941790` -> `0x941770` |

All four load thunks call the established resource loader `0x64D750`. Their
wrapper initializers call `0x64E500`. The four files are now provenance-
imported individually under `original_assets/source/`; no archive, executable
or raw report entered Git.

## General Squad panel identity recovered

`squad_but_anim.444` supplies the decisive general-Squad binding:

- setup method `0x4B5720` is vtable slot 1 at `0x7C5CA8`;
- the vtable begins at `0x7C5CA4`, COL `0x7E5F00`;
- TypeDescriptor `0x819D48` names `.?AVPSquadScreen@@`;
- setup calls `0x652C50` with wrapper `0x9417B0` at exact origins
  `(37,92)`, `(113,92)` and `(189,92)`.

This is the first persisted proof of the distinct native `PSquadScreen` class.
The 73x575 atlas is retained intact. Its internal frame boundaries or user-
facing frame meanings are not inferred from height alone.

## Exact top-control bindings and captions

The same setup method registers the three adjacent controls through vtable
slot `+0x08` (`0x64F3C0`), which stores the supplied numeric control ID and
owner pointer. Their complete source bindings are:

| Control ID | Object offset | Origin | Label global | English.idx | Exact English text |
| ---: | ---: | ---: | ---: | ---: | --- |
| 3 | `+0x37A4` | `(37,92)` | `0x982110` | 2490 | `1ST & RES` |
| 4 | `+0x37F8` | `(113,92)` | `0x98210C` | 2491 | `1ST FORM` |
| 5 | `+0x384C` | `(189,92)` | `0x982108` | 2492 | `RES. FORM` |

The caption mapping is not inferred from visual order. Language loader
`0x635F30` begins its sequential two-byte `English.idx` reads at `0x635F56`.
Calls `0x64AA0E`, `0x64AA30` and `0x64AA52` are zero-based entries 2490,
2491 and 2492 and install those values into the three globals above. The
committed original `English.idx` / `English.str` pair resolves them to the
exact text shown.

The first control receives one distinct setup flag while the other two receive
zero. Its semantic name is not claimed, and no atlas row is labelled as a
normal, hover, pressed or selected state without a separate state transition
trace.

## Formation resources

`squad_bars.444` is consumed by `FormationText::0x4B6B60`; the method forwards
caller-provided geometry into `0x652C50` with wrapper `0x941730`.
`squad_form_anim.444` is consumed by `FormationText::0x4B6C30`, which forwards
caller-provided geometry into `0x652CB0` with wrapper `0x941770`.

`FormationText` is independently identified by TypeDescriptor `0x81DBC0`, COL
`0x7E5BB8`, and vtable `0x7C5700`. `PSquadPitch` (TypeDescriptor `0x81DB30`,
vtable `0x7C54A8`) constructs a 22-element embedded `FormationText` array at
`0x4B5B18`. These two resources therefore belong to the formation/pitch
presentation family, not automatically to the general roster panel.

## `blue_toggle.444` is shared, not `PSquadScreen` proof

The wrapper `0x943050` is consumed by four RTTI-owned setup methods:

| Setup | Vtable / TypeDescriptor | Owner |
| --- | --- | --- |
| `0x464400` | `0x7C1AB4` / `0x81C1C0` | `PFormation2k` |
| `0x48A590` | `0x7C47C8` / `0x81D380` | `PSCFTitle` |
| `0x4DB370` | `0x7C783C` / `0x81D270` | `PTraining` |
| `0x4E5F90` | `0x7C8650` / `0x81F378` | `PYouthTeam` |

No `PSquadScreen` setup reference to this wrapper was found. Its `Coaching/
squad` directory is therefore a shared-control provenance clue, not evidence
that the general Squad panel draws it.

## Durable implementation boundary

`reconstruction/original_squad_resources.py` fail-closes on the four hashes and
native `.444` header sizes, records the exact owner boundary, locks the three
recovered `PSquadScreen` controls, and resolves their captions from the
committed original language pair. It deliberately does not split either
vertical atlas, name native frame states, invent formation coordinates, or
claim the shared blue toggle for the general Squad screen.

## Next action

Use the now-proven `PSquadScreen` setup method as the anchor for the surrounding
general-Squad roster layout, state transitions and navigation. Separately trace
the callers that supply `FormationText` geometry before composing the formation
fragment.
The real Windows PStartMenu/TeamSelect graphical audit remains required before
Gate 13 can close.
