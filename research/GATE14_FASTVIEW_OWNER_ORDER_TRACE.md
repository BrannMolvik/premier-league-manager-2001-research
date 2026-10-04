# Gate 14 FastView owner-order candidate trace

_Status: private evidence tooling only; Gate 13 remains Codex-owned._

## Purpose

The resolved-only FastView compositor now classifies every ambiguous
cross-component overlap by whether its pairwise draw order is already
source-closed. Only one current relation is fully proved:

`possession_diagram -> possession_figures_text`.

The largest remaining raster blocker is therefore not another guessed
compositing rule. It is source evidence for how the other FastView component
families enter the native child-render hierarchy.

`reconstruction/gate14_fastview_owner_order_source_trace.py` narrows that
next private pass.

## Bounded owner neighborhood

The tracer linearly decodes only the source-qualified FastViewPanel neighborhood
`0x51F490 <= VA < 0x520900`.

That interval deliberately spans the already persisted direct owner callsites:

- top-bar PictureControl: `0x51FDA3 -> 0x527730`;
- ticker PictureControl: `0x51FE31 -> 0x527730`;
- PossessionDiagram: `0x5206CD -> 0x5227D0`;
- PossessionFigures: `0x520802 -> 0x51E7E0`.

The interval is **not** asserted to be one exact function boundary.

Within it, the tracer retains only decoded direct CALL candidates whose target
is already source-qualified:

- generic PictureControl `0x527730`;
- PossessionDiagram `0x5227D0`;
- PossessionFigures `0x51E7E0`;
- FastViewTeam constructor `0x524920`.

This makes a future private report materially smaller than broad disassembly and
gives it four persisted callsites as decoder calibration.

## Evidence boundary

A matching direct CALL candidate still does not prove:

- the bounded interval is one reachable FastViewPanel CFG;
- the receiver passed to the constructor;
- that the created object joins FastViewPanel's `+0x1C/+0x38` draw array;
- ordering across nested component-owned child arrays;
- a new pairwise draw-order relation;
- global FastView z-order;
- cross-component alpha/blend behavior; or
- a complete FastView frame.

The report therefore keeps every one of those promotions false.

## Exact private follow-up

On the next healthy canonical-executable path:

1. run this tracer against the verified original executable;
2. locate and manually adjudicate the FastViewTeam constructor candidate(s);
3. recover the receiver/parent data flow for the candidate;
4. prove whether the resulting component joins the same forward-traversed
   FastViewPanel child array used by the direct controls;
5. only then add source-closed pairwise relations to
   `gate14_fastview_draw_order.py`;
6. rerun the overlap-readiness audit to see which exact unresolved pixel groups
   move from draw-order-unresolved to blend-only-unresolved.

No proprietary executable bytes or generated private disassembly belong in Git.
