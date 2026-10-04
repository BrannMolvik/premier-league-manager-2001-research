# Gate 14 ScoreComposite phase receiver order

_Status: independent Gate-14 source result while Gate 13 Fixtures paging remains the earliest incomplete validation gate._

## Result

The original ScoreComposite phase receiver order across the visible
FastViewLeagueScores rows is now source-closed for one event broadcast.

For each typed phase sender, ScoreComposite receivers are:

1. registered in LeagueScores source-row construction order;
2. appended to the sender list tail;
3. dispatched head-to-tail.

Therefore one phase broadcast reaches visible rows in source-index order:

`0, 1, 2, ...`

Within each row callback, the previously closed phase helper appends:

`icon(row) -> text(row)`

So one broadcast over three rows has the exact control-append shape:

`icon0, text0, icon1, text1, icon2, text2`

This is stronger than the previous unknown cross-row callback boundary.

It still does **not** establish a timeless aggregate relation
`all runtime icons -> all runtime text` or the reverse.

## Row construction and typed registration

FastViewLeagueScores builds visible ScoreCompositeNormal rows in the loop rooted
at `0x522E3A`; the virtual score-composite factory call is at `0x522E6C`.

For every new row, the same loop registers these receiver subobjects:

| Event | Receiver offset | Sender offset | Registration callsite |
| --- | ---: | ---: | ---: |
| EventHalfTime | `+0x94` | `+0x40` | `0x522F5C` |
| EventExtraTime | `+0x98` | `+0x60` | `0x522FAF` |
| EventPenalties | `+0x9C` | `+0x70` | `0x523002` |
| EventFullTime | `+0xA0` | `+0x50` | `0x523055` |

The loop's row index is the same source-row progression used for placement.

## Tail insertion

All four registrations use shared list helper `0x5302C0`.

The sender subobject stores:

- sentinel/list anchor at `+0x08`;
- receiver count at `+0x0C`.

The registration path supplies the sentinel and its existing tail. The new node
receives:

- `next = sentinel`;
- `prev = old_tail`;

then the caller updates:

- `sentinel.prev = new_node`;
- `old_tail.next = new_node`.

Receiver data is installed through `0x530330` at node `+0x08`.

This is append-at-tail behavior. It preserves the row construction order.

## Forward dispatch

Typed sender broadcasts start from `sentinel->next`, invoke the receiver
virtual callback at slot `+0x04`, then follow each node's `next` pointer
until the sentinel is reached.

Representative exact forward loops include:

- HalfTime: `0x519A75..0x519AAE`;
- ExtraTime: `0x519B00..0x519B1A`;
- Penalties: `0x519B5A..0x519B74`.

Combined with tail registration, one typed broadcast therefore dispatches
ScoreComposite rows in the same source order in which LeagueScores created
them.

## Why aggregate icon/text order remains unresolved

The phase-display helper's per-callback order is already exact:

- phase PictureControl callsite: `0x51BB05`;
- phase TextControl callsite: `0x51BB9A`.

Thus each callback appends icon before text.

But the controls persist and may be replaced by later phase events. Separate
broadcasts occur at different times. A later broadcast can append a new
icon/text pair after controls created by an earlier broadcast.

Accordingly, the source supports chronological sequences of per-row pairs, not
one universal family partition. The reconstruction must keep:

`league_scores_runtime_phase_icons`

and:

`league_scores_runtime_phase_text`

at the same aggregate unresolved order level.

The 14/15 pairwise overlap result introduced by PR #375 therefore remains the
correct aggregate model.

## Reconstruction contract

`reconstruction/gate14_fastview_phase_receiver_order.py` records:

- exact receiver and sender offsets;
- exact registration callsites;
- tail-insertion list semantics;
- representative forward-dispatch loop anchors;
- source-row registration order;
- source-row callback order for one broadcast;
- per-row icon-before-text control append order.

It deliberately keeps false:

- aggregate runtime icon/text family order;
- flattened runtime phase planes;
- global FastView z-order;
- complete FastView frame;
- Gate 14 completion.

## Next step

The next visual-fidelity task should move away from this now-bounded aggregate
phase-order question. Either close the remaining runtime packed-16 to modern
display/output boundary needed to flatten known overlaps, or source-bind another
omitted FastView child/resource family. Do not introduce an aggregate icon/text
edge unless a stronger chronological invariant is recovered.
