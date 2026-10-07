# Gate 14 direct FastView header TextControls

_Status: independent source-backed Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Result

The two previously unnamed direct FastViewPanel TextControls at outer draw ranks
31 and 32 now have source-closed rendering contracts and runtime string
semantics. The second line's leading value is proven to be the match stadium
display name rather than a context-based guess. Pixel rasterization remains
fail-closed until the verified style-3 font bytes are provenance-staged.

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

The authorized source archive was recovered through
`research/ORIGINAL_SOURCE_LOCATOR.md` and independently verified before
extraction:

- source archive: **511,121,336 bytes**, SHA-256
  `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`;
- raw MODE1/2352 image: all **268,549** sectors validated;
- Joliet level-3 catalog: **2,456** files;
- exact `Fonts\Zurich_XCn_BT_18pixel.fnt`: **79,734 bytes**, SHA-256
  `968936a5f5e42c4dd321f0a1096a8668c8f9ca3bd0b86243b585190969c1b71a`.

Those exact bytes are now provenance-staged at
`original_assets/source/Fonts/Zurich_XCn_BT_18pixel.fnt`. The Git blob SHA
`a7286c680a13811f18c8f67ebcc3e17b381fd752` matches the Git-object SHA
computed independently from the recovered local source bytes before upload.

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

The first string is now source-closed as the **match stadium display name**.

The evidence chain is:

1. `0x62ABD0` stores its constructor argument at `+0xFE8`; its sole caller
   `0x5130A9` passes the current Match-family object.
2. MSVC RTTI proves that caller slot across the concrete source types
   `Match`, `LeagueMatch`, `CupMatch`, `FriendlyMatch`,
   `CupMatchReplay`, and `SecondLegMatch`.
3. `0x62AC80` is the bare accessor `mov eax,[ecx+0xFE8]`, so the returned
   object is that Match-family object, not a separately inferred venue object.
4. Match helper `0x514220` obtains the explicit club id at Match `+0x48`
   when present and otherwise falls back through the first club reference at
   Match `+0x14`.
5. `0x514270` resolves that id through global `0x874B9C`. The global is
   constructed at `0x40BBB0` with vtable `0x7BD718`; RTTI names it
   **`DBTClubs`**.
6. The returned DBRAccessClub record supplies its string at `+0x28`.
   DBRAccessClub loader `0x4022D0` reads that fourth string at callsite
   `0x402364`.
7. The canonical original English resource proves the record slot with real
   club data: Arsenal's fourth string is **Highbury** (STR id 919), Chelsea's
   is **Stamford Bridge** (975), Liverpool's is **Anfield** (1031), and
   Manchester United's is **Old Trafford** (1059).
8. Independently, localized entry 2538 / STR id 21705 is exact
   `%s MATCH TODAY AT %s`; source callsites pass the same `0x514270`
   result as that final location value.

`0x514270` retains the original `N/A` / `NA` fallback logic before
returning the stadium string. No modern stadium label is invented.

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
match-type branch, referee-name formatting path, stadium-display semantic, and
attendance source field. It also source-verifies the exact style-3 font bytes
and their authorized archive provenance.

It deliberately keeps false:

- header pixel rasterization;
- complete FastView frame;
- Gate 14 completion.

## Next step

Bind the now source-closed stadium/referee/attendance strings to reconstructed
match state and rasterize the two direct header controls with the exact staged
style-3 font.
Gate 13 remains the earlier active validation gate and is not changed here.


## Recovery 375 correction — style-3 font identity

Fresh first-hand tracing of the global font initializer supersedes the earlier
18px font association in this document.

The style selector still maps index 3 to wrapper `0x87BE30`, and that wrapper
still points at font object `0x8CAB80`. The corrected initializer dataflow is:

- path literal `0x839E30` is built at `0x6044AC`;
- `0x657650` loads that path into font object `0x8CAB80` at `0x6044F9`;
- `0x839E30` is exact `Fonts\\Zurich_XCn_BT_16pixel.fnt`.

The previously associated `0x839E10` / `Zurich_XCn_BT_18pixel.fnt` belongs
to the next font object `0x8BD970`, not to `0x8CAB80`.

The authorized source file for the corrected style-3 font is:

- size: 75,217 bytes;
- SHA-256: `e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18`;
- parsed atlas: 1261 x 17;
- native line height: 18.

Accordingly, the earlier 18px raster checkpoint is superseded. The clean-room
FastView direct-header contract and tests now use the 16px source font and must
pass exact-head CI before this correction is promoted to canonical `main`.

This correction also matters to PPreMatch: its fixture-header/date controls use
the same `0x87BE30` wrapper, so new pre-match text pixels must use the
corrected 16px source rather than copying the stale FastView label.
