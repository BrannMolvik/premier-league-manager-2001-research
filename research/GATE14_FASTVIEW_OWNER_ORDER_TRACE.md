# Gate 14 FastView owner-order candidate trace

_Status: canonical private replay completed for the owner-call layer; Gate 13 remains Codex-owned._

## Purpose

The resolved-only FastView compositor classifies ambiguous cross-component
overlap by whether pairwise draw order is source-closed. Before this checkpoint,
only one current relation was fully proved:

`possession_diagram -> possession_figures_text`.

Recovery 274 restored a healthy private execution path and replayed the owner
trace against the authorized original disc instead of stopping at synthetic
tooling.

## Revalidated canonical source

The source chain was revalidated from the user-owned Library artifact:

- disc-image ZIP: **511,121,336 bytes**;
- ZIP SHA-256:
  `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`;
- raw MODE1/2352 image: **631,627,248 bytes** / **268,549 sectors**;
- Joliet inventory: **2,456 files** and **211 directories**;
- both root and `crack/` copies of `footballmanager.exe`: **4,714,541 bytes**;
- canonical executable SHA-256:
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

No proprietary executable bytes or generated disassembly were placed in Git.

## Corrected bounded setup region

The first #344 trace bound ended at `0x520900`. A canonical private pass
reproduced all four calibration calls inside that range but correctly found no
FastViewTeam constructor there.

A full direct-call check then located exactly:

`0x520E67 -> FastViewTeam::0x524920`.

The repository tracer now covers the bounded setup region

`0x51FA70 <= VA < 0x5211F9`

and uses five persisted source callsites as calibration:

- top-bar PictureControl: `0x51FDA3 -> 0x527730`;
- ticker PictureControl: `0x51FE31 -> 0x527730`;
- PossessionDiagram: `0x5206CD -> 0x5227D0`;
- PossessionFigures: `0x520802 -> 0x51E7E0`;
- FastViewTeam: `0x520E67 -> 0x524920`.

The widened range is still treated as a bounded source region by the automated
tool rather than as automatic proof of one fully recovered CFG.

## FastViewTeam parent dataflow adjudication

The private source context materially narrows the remaining order problem:

1. the owner allocates the FastViewTeam object;
2. immediately before `0x520E67`, it pushes the current FastViewPanel object
   as the constructor argument;
3. `FastViewTeam::0x524920` calls generic Panel constructor `0x527350`;
4. the FastViewTeam constructor then stores its incoming owner pointer at
   object offset `+0x78`;
5. the owner stores the constructed FastViewTeam pointer at FastViewPanel
   offset `+0x94`.

That proves the owner call and parent-pointer relationship. It does **not**
prove that FastViewTeam itself enters the same forward-traversed
FastViewPanel `+0x1C/+0x38` child array used by direct PictureControl/TextControl
children.

The constructor/setup region `0x524920..` contains no direct
`0x5274C0` append-registration call for the FastViewTeam object. Therefore
this checkpoint deliberately does not add any new pairwise relation to
`gate14_fastview_draw_order.py`.

## Evidence boundary

The canonical replay now source-closes the FastViewTeam owner callsite and
parent-pointer relationship. It still does not establish:

- FastViewTeam registration into the parent's forward draw array;
- how FastViewPanel invokes FastViewTeam rendering if it is not a normal child;
- ordering across FastViewTeam's nested TeamTable/Row controls and direct
  FastViewPanel children;
- a new pairwise draw-order relation;
- global FastView z-order;
- cross-component alpha/blend behavior; or
- a complete FastView frame.

Accordingly, `fastview_team_owner_callsite_recovered` may become true when the
exact recovered call is decoded, while
`same_parent_registration_recovered_for_new_pairs`,
`additional_pairwise_draw_order_recovered`,
`global_fastview_z_order_recovered`,
`cross_component_blend_rule_recovered`, and
`complete_fastview_frame_recovered` remain false.

## Exact next source task

The next private FastView order task is no longer to locate FastViewTeam.
Instead:

1. trace FastViewPanel's render/visibility path to the object stored at
   `+0x94` / later copied into its runtime presentation state;
2. identify whether that path calls FastViewTeam before, during, or after the
   generic `0x6533A0` forward child-array traversal;
3. separately prove the TeamTable/Row nested traversal boundary;
4. only then add source-closed relations to
   `gate14_fastview_draw_order.py`;
5. rerun the overlap-readiness audit and promote only exact contributor groups
   whose order is actually proven.

No geometry, callsite proximity, class naming, or allocation order is used as a
draw-order substitute.
