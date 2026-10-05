# Gate 14 TeamTable base-control private source boundary

_Status: cloud-safe trace preparation; no new private executable adjudication._

## Why this exists

The canonical nested-order contract already proves that each TeamTable owns
exactly six visible base controls before its parameterized PlayerRow children.
The retained PlayerRows raster now covers the row subtree, but those six
table-level controls remain outside the current pixel model.

The repository does **not** yet source-close which constructor calls correspond
to those six controls, their roles, arguments, geometry, resources, text or
pixels.

## Trace anchors

The private tracer narrows the next source pass to the canonical TeamTable
constructor at `0x524EC0` and records decoded direct calls only to already-known
constructor targets:

- generic Panel: `0x527350`;
- generic PictureControl: `0x527730`;
- generic TextControl: `0x527960`;
- PlayerRow: `0x525DB0`.

The inspection window is bounded source evidence, not a claimed exact function
extent. A decoded direct call is only a candidate. It does not prove that the
call constructs one of the six base controls, nor does nearby linear
disassembly prove arguments or registration order.

## Fail-closed contract

Already canonical:

- TeamTable constructor identity;
- exactly six TeamTable base controls;
- nine controls per PlayerRow;
- parameterized PlayerRow count.

Still false after this checkpoint:

- identities of the six base controls;
- adjudicated constructor callsites for those controls;
- base-control registration order;
- geometry;
- resource identity;
- text semantics;
- raster pixels;
- complete TeamTable;
- complete FastView frame;
- Gate 14 completion.

## Private next step

When a functioning private process/disassembly surface is available, run the
tracer against the checksum-gated original executable and manually adjudicate
the candidate calls around `0x524EC0`. Only then may the six controls be mapped
to roles/geometry/resources or used to promote
`team_subpanel_complete_pixels_recovered`.

Raw executable bytes and disassembly must remain outside Git.
