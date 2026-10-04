# Gate 14 source-closed possession draw order

_Status: independent Gate-14 source result while Gate 13 remains Codex-owned._

## Result

Private tracing of the canonical executable now closes one cross-component
FastView ordering relation:

`possession_diagram -> possession_figures_text`

The PossessionFigures percentage text is registered later and painted later than
the PossessionDiagram PictureControls. Where those two components overlap, the
text control is therefore the later native draw operation.

This is a pairwise result only. It is not a global FastView z-order.

## Source chain

The result does not rely on filenames or screen geometry.

### 1. Both control types join the same parent draw array

Generic PictureControl constructor `0x527730` registers itself with its parent
through call `0x52782A -> 0x5274C0`.

Generic text-control constructor `0x527960` registers itself through
`0x527A15 -> 0x5274C0`.

Wrapper `0x5274C0` supplies the parent draw-array storage to append helper
`0x5275C0`:

- pointer array: parent `+0x1C`;
- count: parent `+0x38`.

### 2. Registration preserves construction order

Append helper `0x5275C0` allocates one extra pointer slot, copies all existing
entries in forward index order, writes the new child at the old count index, and
then increments the count.

New controls therefore append to the end of this draw array.

### 3. The renderer traverses that array forward

Generic traversal `0x6533A0` reads the same parent fields:

- draw-array pointer from `+0x1C`;
- draw-array count from `+0x38`.

Its loop starts at index 0, increments the index by one, and continues while
`index < count`. For each visible/clipped child it dispatches virtual offset
`+0x64`.

For the relevant generic PictureControl and text-control vtables, that render
slot targets `0x64F6D0`, which forwards to the contained visual renderer.
Thus the array traversal is the actual visible child-render path rather than an
ownership-only/destructor list.

### 4. FastView constructs the diagram controls first

FastViewPanel calls the PossessionDiagram constructor at
`0x5206CD -> 0x5227D0`. That constructor creates its pitch/overlay
PictureControls through `0x527730`, so they append to the parent draw array
during this call.

Only later does FastViewPanel call PossessionFigures at
`0x520802 -> 0x51E7E0`. That constructor creates its three percentage text
controls through `0x527960`, which append to the same parent draw array.

Forward traversal therefore paints the diagram controls first and percentage
text afterward.

## Reconstruction boundary

`gate14_fastview_draw_order.py` records this one pairwise relation and the
source addresses that establish it.

It deliberately keeps these unresolved:

- the global order among all FastView component families;
- direct chrome versus TeamTable/score/table components;
- source blend/alpha behavior across component boundaries;
- generic PictureControl crop-versus-stretch behavior for resized energy bars;
- unbound background ownership;
- audio and 3D choreography.

The resolved-only compositor should not flatten this overlap merely from the
ordering fact until the relevant cross-component pixel/blend behavior is also
source-safe. The current transparency mask remains the conservative pixel
boundary.

## Provenance

The private run used the authorized Library source archive:

`The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`

The recovered raw MODE1/2352 disc again enumerated 2,456 files. Both root and
`crack/footballmanager.exe` copies were byte-identical and matched canonical
SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

No proprietary executable bytes or private disassembly are committed.
