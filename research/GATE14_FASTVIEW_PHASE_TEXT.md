# Gate 14 ScoreComposite phase-label source trace

_Status: independent Gate-14 source result while Gate 13 Fixtures paging remains Codex-owned._

## Result

The paired text created by `ScoreCompositeNormal::0x51BA30` is now
source-closed for the four phase events that already own exact icon resources:

| Event receiver | Label global | English.idx entry | STR id | Exact English text |
| --- | ---: | ---: | ---: | --- |
| `EventHalfTime` | `0x982380` | 2334 | 21533 | `HT` |
| `EventFullTime` | `0x98237C` | 2335 | 21534 | `FT` |
| `EventExtraTime` | `0x982378` | 2336 | 21535 | `ET` |
| `EventPenalties` | `0x982374` | 2337 | 21536 | `PEN` |

These labels are derived from the exact executable localization loader and the
provenance-tracked original `English.idx` / `English.str` pair. They are
not inferred from event names, icon filenames, or nearby language strings.

## Exact localization mapping

The canonical executable contains one uninterrupted **2,714-entry** loader,
which exactly matches the 2,714 uint16 entries in `English.idx`.

For each entry it:

1. reads one two-byte value through `0x667E90`;
2. supplies the active language string-table object and that uint16 index to
   `0x64E320`;
3. `0x64E320` resolves the string pointer as
   `table_base + (index & 0xFFFF) * 4`;
4. stores the resulting pointer in a destination-global table.

The read-call sequence begins at `0x635F56` and ends at `0x64C7AC`.
Destination globals descend by four bytes from `0x9847F8` to `0x981D94`.

Therefore one destination global has the exact language-index entry:

`entry = (0x9847F8 - global_va) / 4`

The four ScoreComposite label globals map to entries 2334..2337. Replaying
those entries against the canonical English resource gives `HT`, `FT`,
`ET`, and `PEN` respectively.

The checked-in source identities are:

- `English.idx`: 5,428 bytes, SHA-256
  `98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1`;
- `English.str`: 369,644 bytes, SHA-256
  `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`.

## Text-control render contract

The phase helper creates its text control through generic constructor
`0x527960` with:

- local rectangle `(311,0)-(339,16)`;
- raw flags `0x24`;
- style index **1**;
- native color endpoint **0xFFFF**.

The generic constructor adds its mandatory render bit `0x08`, yielding
render flags **0x2C**.

Generic text draw `0x64F090` interprets:

- bit `0x04` as horizontal centering;
- bit `0x20` as vertical centering.

Thus the exact phase label is centered both horizontally and vertically in the
28x16 local control. Style 1 is the already source-backed wrapper
`0x87BE90` / font object `0x9197E0`, the same Zurich 18-pixel source font
family already used by FastView text reconstruction.

## Runtime ordering boundary

Within one `0x51BA30` callback:

1. the phase PictureControl is created at callsite `0x51BB05`;
2. the phase TextControl is created later at `0x51BB9A`.

So **one callback's icon precedes its own text**.

However, runtime phase callbacks for multiple ScoreComposite rows append their
controls at the parent array's current tail. The resulting global sequence can
therefore be interleaved per row:

`icon(row A), text(row A), icon(row B), text(row B), ...`

It is not source-correct to replace that with one global
`all icons -> all labels` relation.

For the same reason, this checkpoint does not flatten the label pixels into the
current aggregate runtime-icon plane. Antialiased label pixels can overlap the
18x16 icon, and exact native packed-16 blending/output conversion remains a
separate fidelity boundary.

## Reconstruction contract

`reconstruction/gate14_fastview_phase_text.py` makes the exact global/index/
text mapping and generic text parameters machine-checkable. Its tests replay
the four mappings against the actual provenance-tracked English language
resources already in the repository.

This checkpoint promotes:

- exact phase-label text identity;
- exact localization-global mapping;
- exact phase text rectangle/style/color/alignment;
- per-callback icon-before-text order.

It deliberately keeps false:

- paired phase text rasterized;
- global all-icons-before-all-text order;
- runtime icon/text interleaving flattened;
- global FastView z-order;
- complete FastView frame;
- Gate 14 completion.

## Next step

Represent runtime phase icon/text pairs at a granularity that preserves native
per-row append order, or close the remaining native packed-16-to-modern output
boundary before any overlapping pair is flattened. Do not regress to an
aggregate icon-only z-position as a complete representation.
