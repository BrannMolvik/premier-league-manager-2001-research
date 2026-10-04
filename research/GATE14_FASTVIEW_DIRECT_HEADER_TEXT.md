# Gate 14 direct FastView header TextControls

_Status: independent source-backed Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Result

The two previously unnamed direct FastViewPanel TextControls at outer draw ranks
31 and 32 are now source-closed far enough to preserve their exact rendering
contract and runtime string shapes without inventing the remaining leading
second-line semantic.

They are created at:

- `0x520A16`: rectangle `(250,45)-(550,75)`;
- `0x520A69`: rectangle `(250,70)-(550,86)`.

Both use:

- generic TextControl constructor `0x527960`;
- style index **3**;
- native color `0xFFFF`;
- raw flags `0x24`, plus the generic forced render bit `0x08`;
- final flags `0x2C`, therefore horizontal and vertical centering.

Style selector `0x527BA0` maps index 3 to wrapper `0x87BE30`. Its initializer
binds font object global `0x8CAB80`, loaded by `0x657650` from the exact
embedded path:

`Fonts\Zurich_XCn_BT_18pixel.fnt`

That font is not yet provenance-staged in the repository, so this checkpoint
does not rasterize either control.

## Match-context ownership

FastViewPanel constructor `0x51F490` has one source callsite at `0x53321A`.
The caller passes its retained match object as constructor argument 3, and the
constructor stores that exact pointer at FastViewPanel `+0x2A8`.

The header producer later reads the match-type field at `+0xD20` and the
attendance integer at `+0xD84` from that retained object.

## First line

The source first builds a person display string at `0x6310B0` using exact
format:

`%s %s`

from two source-indexed strings. Helper `0x51F430` then preserves a one-word
name or abbreviates a multi-word value with:

`%c. %s`

The resulting display name is passed immediately after the exact localized
label **Referee**.

The source match-type branch is:

- match-context `+0xD20 < 0`: exact localized **Friendly**;
- otherwise: index `+0xD20` passes through the source lookup chain
  `0x4056D0 -> 0x4F3B10 -> 0x49AB40`.

The localized template global is exact **`%s MATCH`**. The constructor appends
literal suffix **`  -  %s %s`**, producing exact final format:

`%s MATCH  -  %s %s`

Thus the source-backed line shape is:

`<match-type> MATCH  -  Referee <abbreviated source person name>`

No referee identity is fabricated from modern match state in this checkpoint.

## Second line

The exact format at `0x8296F8` is:

`%s  -  %s %u`

The second string is exact localized **Attendance**, and the integer is read
from match-context `+0xD84`.

The first string is obtained by:

1. `0x62AC80` returning match-context nested object `+0xFE8`;
2. `0x514270` resolving that object's source display string through existing
   object/lookup state, including its original `N/A` / `NA` fallback logic.

The exact player-facing semantic name of this leading value is **not** yet
source-closed, so code deliberately keeps it neutral instead of calling it a
stadium, venue, city, or club from context.

## Localization proof

The already source-closed 2,714-entry English global table maps these exact
values:

| Global | English.idx entry | STR id | Text |
| --- | ---: | ---: | --- |
| `0x981EE4` | 2629 | 21783 | `%s MATCH` |
| `0x982354` | 2345 | 21542 | `Referee` |
| `0x982C40` | 1774 | 20308 | `Attendance` |
| `0x9830C8` | 1484 | 20885 | `Friendly` |

Automated tests replay these entries against the provenance-tracked canonical
`English.idx` / `English.str` pair.

## Fidelity boundary

This checkpoint closes the two controls' construction, geometry, style/font
identity, color/alignment, localization labels, exact format strings,
match-type branch, referee-name formatting path, and attendance source field.

It deliberately keeps false:

- semantic naming of the second line's leading `0x514270` result;
- provenance staging of `Zurich_XCn_BT_18pixel.fnt`;
- header pixel rasterization;
- complete FastView frame;
- Gate 14 completion.

## Next step

Source-close the nested `+0xFE8 -> 0x514270` object's concrete class/field
meaning. Independently, stage and checksum the exact style-3 font from the
authorized disc. Only after both are verified should these header strings be
bound to reconstructed match state and rasterized.
