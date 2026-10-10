# Original Squad name-drag cursor — bounded source contract

Canonical executable SHA256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Independent source audit and primary re-execution:27 canonical-byte comparisons
over three explicitly supplied mask layouts. No original process was launched.
Private source/emulation receipts remain outside Git.

## Contract before implementation

PSquadScreen owns cursor+38A0, constructor4BD330, final vft7C5D44. Setup
4B597F..59A6 registers it last (index6/7) in the Squad draw array, then allocates
a128x32/16-bit surface through4BD3F0/6555D0. Native source key87B680 is derived
from the observed runtime red/blue masks; it is not a fixed guessed magenta.
Descriptor64E460 is flags21h, bltflags0, source(0,0,128,32), mode100h.

Name press4B92CB..92EE resolves the retained roster player, calls4BD5F0 and
immediately4BD790. There is no movement threshold on this path. Null player
returns0 without changing existing cursor state. Shirt-number drag is separate.
Player+0C /42C6F0 supplies the original surname bytes, not the abbreviated row
name.4BD5F0 clears the surface to key, fills RECT
`(0,5,min(strlen(surname)*8+10,128),22)`, then draws black at(5,5), clip
(0,0,128,32), flags24h. Font9269F0 is literal839F24 ->
`Fonts/Zurich_BdXCn_BT_16pixel.fnt`, SHA256
`9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732`.
It is not the18px row font. Byte length controls the fill, not measured glyph
width or ellipsis. Native glyph casing/pair layout is a separate font dependency.

4BD790 places the full surface at parent-local pointer minus(20,20), without
clamping. Motion4B8D80 invalidates old then new rectangles when active. Actual
Squad origin is(0,79), size800x520; native parent traversal6533A0 intersects the
supplied clip before blit and shifts the source crop accordingly. Source-key
plus wait flags are1008000h. Example local pointer(5,5) with full parent clip:
screen destination(0,79,113,96), source(15,15,128,32). Local(799,520):
screen destination(779,579,800,599), source(0,0,21,20).

Accepted/rejected name release hides via4BD4A0, clears+CC and refreshes.
Hide clears source clip/offsets and active state but retains/invalidate the old
destination rect. Name-child right press also reaches4B6DA0 and hides, after a
separate player-detail boundary. Destruction releases the surface/descriptor.
WM_ACTIVATEAPP invokes ordinary release at retained pointer coordinates; it
is not proven unconditional cancel. Squad-local Escape is a no-op, but the
global saved key handler is unresolved. Do not invent threshold/focus/Escape
semantics or apply name behavior to shirt-number controls.

## Exact packing, deliberately no default format

Runtime metadata653090/6530D0/653120 supplies R-left/R-right at984828/2C,
G-left/G-right at984834/38 and B-right at984844.4BD64D..6AB executes:

    ((0xAC00 >> ((G_right+8)&31)) << (G_left&31))
    | (0x160000 >> ((R_right+16)&31))
    | ((0xBD >> (B_right&31)) << (R_left&31))

All shifts/ORs have x86 uint32 semantics. There is no red-left shift; the last
shift uses R-left, not B-left. Do not silently replace this with conventional
RGB(22,172,189). Original synthetic mask R/G/B inputs produce:

| Explicit fixture masks | Native fill DWORD |
| --- | --- |
| 001F/07E0/F800 | 0577 |
| F800/07E0/001F | BD62 |
| 7C00/03E0/001F | 5EA2 |

These are parameterized function proofs, not observed historical masks.
Native font antialias blending and modern expansion also require a qualified
transport. No suitable original-runtime mask receipt was found in the bounded
existing receipt check. The new helper may represent exact content/packing/
crop only with explicit inputs. It must not select a format, render guessed
RGBA, bind a live cursor, or claim visible acceptance until those dependencies
are qualified. Unaffected formation/Inbox/NEXT work can continue.

SOURCE-VERIFIED: this bounded content/packing/geometry contract with explicit
pixel metadata and the separately declared emulator/API fixtures.
INTEGRATION-VERIFIED: not yet; live original cursor transport remains absent.
VISIBLE-ACCEPTED: no. Daniel's exact multi-drag sequence remains unreplicated.

## Independent transport challenge

Source route530E87 ->653090 reads surface947594 via GetSurfaceDesc.6530D0/
653120 retain its actual RGB masks/shifts;656320 retains the font-blit masks.
615256 requests16bpp, but the returned surface comes from the external
_THRASH_setstate@8(DAC1) ->947AC4 ->614F40 ->947594. The EXE does not prove
one fixed565 format.6555D0(16) copies the observed masks. Its32-bit branch
is unrelated to this cursor. DirectDrawBlt is the qualified final boundary;
no native packed16-to-RGBA expansion is established there.

Independent reviewer cursor_transport_audit executed653090/6530D0/653120/
656320,6555D0 and658BC0 for3,072 packed-pixel cases over three explicit
format fixtures; primary agent reviewed/reran the private harness. Successful
GetSurfaceDesc/CreateSurface/Lock/Unlock leaves, alpha bytes, storage and
rectangles are explicit fixtures, not a live format receipt.

Critical counterexample: native black-font antialias replaces a source-key
destination with literal0 before intermediate blending. Any nonzero coverage
on a key pixel becomes black, not translucent RGBA. The native arithmetic is
integer /256; alpha255 has a separate direct-write branch; unused packed bits
survive intermediate blending.555 bit15 can remain8000 at alpha254 then become
0000 at alpha255. Expanded RGB8 /255 would diverge. Original443E00 quantization
is many-to-one (both248 and255 become5-bit31); inverting it cannot prove exact
modern channel expansion. Keep packed surface plus explicit format/key context
together, and qualify the output adapter independently before visible claims.
No guessed RGB, fixed synthetic mask or translucent cursor was bound.
