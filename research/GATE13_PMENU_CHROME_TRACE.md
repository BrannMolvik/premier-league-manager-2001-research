# Gate 13 PMenu chrome and static menu trace

_Date: 2 October 2026 KST_

This note records the first source-bound management-shell chrome after the
fresh-game route recovered in `GATE13_MANAGEMENT_SHELL_ROUTE.md`.

Trace source: canonical `footballmanager.exe` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Original resources were read from the authorized source image outside Git.
Raw disassembly and unselected proprietary bytes remain private.

## PMenu row-class family

MSVC RTTI and vtables identify the management menu classes:

| Class | Vtable | Source-bound setup/use |
| --- | ---: | --- |
| `CMenuList` | `0x7C3E34` | embedded by `PMenu` |
| `PBaseMenuRow` | `0x7C3C50` | common row base |
| `PTitleMenuRow` | `0x7C3A80` | setup `0x47A7E0` |
| `PChildMenuRow` | `0x7C3A20` | setup `0x47A990` |
| `MenuTitleArrow` | `0x7C3B98` | title-row child |
| `MenuBackgroundToggle` | `0x7C3AE0` | menu background state |
| `PTitleMenuRow::SelectBmp` | `0x7C3CB0` | title selection bitmap |
| `PChildMenuRow::SelectBmp` | `0x7C3D4C` | child selection bitmap |

The row builder at `0x482300` advances visible rows in **29-pixel**
increments. The same height is encoded by every correlated row resource below.

`CMenuList` also constructs six `eCText` objects (vtable `0x7BE340`) at
vertical origins `0,24,48,72,96,120`, each with a 160x24 presentation
rectangle, plus bitmap/background objects. Those text controls all reference the
runtime font object at `0x87BEA0`.

The exact source font file, native text colors, clipping and all row-state
meanings are still open. The reconstruction must not substitute a modern font
or name atlas frames from appearance alone.

## Exact original row resources

Four original files are now bound end-to-end from literal path -> resource
loader -> wrapper -> concrete PMenu row class.

### Child-row arrow/status strip

`FM2001_Art/Generic/menu_popup/menu_anim.444`

- literal VA: `0x837C20`;
- loader: `0x5FAB10 -> 0x64D750`;
- raw handle: `0x9438B0`;
- wrapper setup: `0x5FAB60 -> 0x64E500`;
- wrapper: `0x943890`;
- consumer: `PChildMenuRow::0x47A990` at `0x47AA06`;
- exact file bytes: 22,768;
- source geometry: 30x667 = **23 x 29-pixel rows**;
- SHA-256:
  `de53b9ed410bf0456e79c03b305cfb7a1ccaae4c10fb77a50fefd7106c2d4e22`.

### Title-row arrow/status strip

`FM2001_Art/Generic/menu_popup/menu_arrow_anim.444`

- literal VA: `0x837C4C`;
- loader: `0x5FABA0 -> 0x64D750`;
- raw handle: `0x943870`;
- wrapper setup: `0x5FABF0 -> 0x64E500`;
- wrapper: `0x943850`;
- consumer: `PTitleMenuRow::0x47A7E0` at `0x47A856`;
- exact file bytes: 26,248;
- source geometry: 30x638 = **22 x 29-pixel rows**;
- SHA-256:
  `45d34aea3d4ae3f85a171fe3e6eb1b28ea960f5f500f123d98bcbbab52d22006`.

### Title-row background strip

`FM2001_Art/Generic/menu_popup/submenu_main_box.444`

- literal VA: `0x837C80`;
- loader: `0x5FAC30 -> 0x64D750`;
- raw handle: `0x943830`;
- wrapper setup: `0x5FAC80 -> 0x64E500`;
- wrapper: `0x943810`;
- consumer: `PTitleMenuRow::0x47A7E0` at `0x47A907`;
- exact file bytes: 5,700;
- source geometry: 168x87 = **3 x 29-pixel rows**;
- SHA-256:
  `37bc920cb734cde0ac8891d240341f06319c4d1827cdd03a9c4ef8137e30791c`.

### Child-row background strip

`FM2001_Art/Generic/menu_popup/menu_main_box.444`

- literal VA: `0x837CB4`;
- loader: `0x5FACC0 -> 0x64D750`;
- raw handle: `0x9437F0`;
- wrapper setup: `0x5FAD10 -> 0x64E500`;
- wrapper: `0x9437D0`;
- consumer: `PChildMenuRow::0x47A990` at `0x47AAB7`;
- exact file bytes: 6,864;
- source geometry: 168x116 = **4 x 29-pixel rows**;
- SHA-256:
  `4cc1becee669f1f55749a58051eca8833ed582b1f45754c18485366dd6715007`.

A separate `menu_anim_disabled.444` file and
`GenericButtonsAndBars/menu_arrow.444` were also found and hash-checked
privately, but their PMenu-row ownership/state meaning is **not** yet proven.
They are intentionally excluded from the guarded PMenu resource set.

## Static menu-node representation

`0x60C9C0` constructs one 24-byte menu node:

```text
+0x00 = zero/runtime state
+0x04 = label object/global
+0x08 = auxiliary resource/string object
+0x0C = menu/panel ID
+0x10 = child-array pointer
+0x14 = zero/runtime flags
```

`0x60C9F0` writes the terminating node. `0x60CB60` recursively searches by
the `+0x0C` ID. `0x60CA20` and `0x60CA30` resolve the label and auxiliary
members respectively.

The main root array is `0x947638`, in exact construction order:

| Root ID | Label global | Child array | Exact caption status |
| ---: | ---: | ---: | --- |
| 2 | `0x98475C` | `0x9479C8` | English.idx 39 = **Team** |
| 3 | `0x982298` | `0x947968` | unresolved label global |
| `0x259` | `0x982B1C` | `0x947728` | unresolved label global |
| 6 | `0x982098` | `0x947830` | unresolved label global |
| 7 | `0x98474C` | `0x9477D0` | English.idx 43 = **Analysis** |
| 4 | `0x982094` | `0x9478D8` | unresolved label global |
| 5 | `0x98209C` | `0x947878` | unresolved label global |
| 1 | `0x984748` | `0x947A70` | English.idx 44 = **EAMail** |
| 8 | `0x9820A0` | `0x947770` | unresolved label global |

The main English loader maps entry N to
`0x9847F8 - 4*N`. Only labels satisfying that exact loader/global relation
are promoted as captions.

### Team children, array 0x9479C8

IDs in order:
`0xCE, 0xCA, 0xCB, 0xCC, 0xCD, 0xCF`.

Exact correlated child captions currently include:

- `0xCA`: English.idx 48 = **Stats**;
- `0xCC`: English.idx 53 = **Team Orders**;
- `0xCD`: English.idx 54 = **Training**;
- `0xCF`: English.idx 59 = **Youth Team**.

The fresh PMenu route independently maps `0xCE` to `PSquadScreen`, but its
row caption global `0x982918` is not yet language-correlated.

### Transfer-family children, array 0x947968

IDs: `0x12D, 0x12E, 0x12F`.

Their row-label globals remain unresolved. The panel factory independently uses
the exact main-English **Transfer** heading for this family, and `0x12E`
constructs `PScouting2K`; neither fact licenses guessing the three row
captions.

### Direct 0x259 family, array 0x947728

IDs: `0x259, 0x25C`.

Both row-label globals remain unresolved.

### Tables children, array 0x947830

- `0x25A`: English.idx 71 = **League Tables**;
- `0x25B`: English.idx 72 = **Cup Tables**.

`0x25A` is independently proven to construct `PLeagueTables` in the
management-shell route trace. The root ID 6 caption global itself is not yet
language-correlated and is therefore not forced to the nearby word "Tables".

### Analysis children, array 0x9477D0

IDs: `0x2BD, 0x2BE, 0x2BF`.

The root caption is exactly **Analysis**, but these child-label globals are not
members of the main-English global sequence and remain unresolved. Nearby
English strings such as Ratings/Trophy Room/Match Archive are not accepted as
bindings without the missing initializer/use correlation.

### ID-4 family, array 0x9478D8

IDs: `0x191..0x195`.

Exact language-correlated rows:

- `0x193`: English.idx 67 = **Stadium**;
- `0x194`: English.idx 68 = **Development**;
- `0x195`: English.idx 69 = **Maintenance**.

The corresponding factory family uses the exact **Admin** panel heading, but
the root ID-4 row label global `0x982094` remains unresolved.

### ID-5 family, array 0x947878

- `0x1F5`: English.idx 60 = **Cash Flow**;
- `0x1F6`: English.idx 62 = **Tickets**;
- `0x1F7`: English.idx 63 = **Contracts**.

The root caption remains unresolved.

### EAMail child, array 0x947A70

One child:

- `0x65`: English.idx 44 = **EAMail**.

### ID-8 family, array 0x947770

IDs: `0x321, 0x322, 0x323`.

All three row captions remain unresolved. `0x323` is independently the proven
`PStartMenu` screen ID, but that does not identify its PMenu row caption.

## Separate source-proven team-order array

Array `0x9475A0` exists outside the proven main root tree ownership:

- `0x3E9`: English.idx 47 = Formation;
- `0x3EA`: English.idx 48 = Stats;
- `0x3EB`: English.idx 51 = Ind Orders;
- `0x3EC`: English.idx 52 = Specific Roles;
- `0x3ED`: English.idx 53 = Team Orders.

Its exact owning navigation edge remains open, so it is retained separately
rather than inserted into the main PMenu hierarchy by assumption.

## Reconstruction consequence

`reconstruction/original_pmenu_chrome.py` now guards:

- the concrete PMenu row-class identities and setup addresses;
- the 29-pixel native row geometry;
- the four exact source-correlated row resources and hashes;
- the nine-root static menu order and child arrays;
- only the English captions that have exact loader/global correlation.

This is enough to build a faithful resource-backed PMenu hierarchy skeleton
without inventing category names.

It is **not** enough to claim finished management presentation. Remaining PMenu
work includes:

1. recover the unresolved non-main-English label globals;
2. identify the exact source font behind runtime handle `0x87BEA0`;
3. recover text origin/color/clipping and row selection/hover/disabled state-to-
   frame transforms;
4. trace the exact PMenu shell background/chrome around the row list;
5. provenance-import only the four already-correlated source assets (and later
   assets only after their ownership is proven);
6. execute integrated Windows graphical validation after the corrected first-
   screen audit.

No original resource bytes are added by this checkpoint itself.

## Recovery 145 private source validation

Before this checkpoint was proposed for merge, the four selected files were
re-read from the freshly staged authorized source outside Git. All four matched
the byte lengths, SHA-256 values, source dimensions and original
`64 ff 00 ff` EA444 descriptor recorded above. Their heights divided exactly
into the expected 29-pixel row stacks (22, 3, 23 and 4 respectively).

This private validation proves the selected bytes match the source contract; it
does not replace hosted regressions or authorize any uncorrelated neighboring
asset.
