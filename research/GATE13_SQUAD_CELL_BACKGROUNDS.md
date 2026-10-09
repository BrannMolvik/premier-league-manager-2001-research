# Original populated Squad cell backgrounds — 9 October 2026

Canonical executable SHA256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Read-only bounded analysis; no original process launch. Raw executable,
disassembly, emulator and receipt remain private/outside Git.

## Original contract before implementation

Final populated row vft7C57BC inherits setup489530. Its three pictures use
descriptor wrappers +9C/+BC/+DC and drawing context +70, not stats_grid.444.
Setup443E70/64F380 binds role `(28,1,38,14)`, shirt `(1,1,22,14)` and
name `(71,1,154,14)`. Name *text* starts at76; using that as the background
origin would omit five native pixels. All rectangles fit the226x17 row owner.
Empty slots have no populated-row cells and retain the original disabled grid.

PSquadList setup4B5078..4B518D writes palette0/2/5/7. At4B5193..4B519D,
its +9D8 drawing context has descriptor5, draw flags100 and the palette pointer.
4B56B9 ->4B7FD0 passes that context to both populated-list constructors.
Context vft7C0480+8 ->5D6720 translates the clipped local rectangle and calls
658520 with its selected palette colour. Native initial picture flags183
come from465970/465980 ->64F300.

With descriptor5, actual64FDB0 returns frame2 only for enabled+hover, otherwise
frame0. Selection flag4 and press flags10/20 do not change this frame. Source
RGB8 intent is `(57,130,171)` for palette0 and `(16,95,162)` for palette2;
the inline channel shifts produce the corresponding native packed values.
As with the existing Squad fonts, the modern renderer retains RGB8 intent;
this is not a claim about historical DirectDraw RGB555/565 or exact expansion.

650F60 tests the old/new pointer against the shared main/SCF row rectangles;
6515C0 sends row-vft+48 to both paired lists. Populated main-row48AA00 then
sets hover on all three pictures through64F450. Main owner width226, side
owner x239/width89, step17 and row origins154+17*i come from4B7FD0/4B8020.
The gap between the main and SCF owners is not a hit. Parent origins37/418
and panel y79 are already source-qualified. No hover timer is required.

Private bounded verification executed canonical4B5078 palette arithmetic and
5D6720 with actual64FDB0: **6,144** flag/geometry comparisons passed across
all low10-bit states, with/without8000, and all three cell rectangles. Two
explicit synthetic pixel formats checked arithmetic; neither is promoted to
the original Windows runtime format. No game state was injected into a process.

## Limits kept explicit

Picture bit8000 selects palette5/7 (RGB189,172,22), but its ordinary owner-local
producer is not proven here. Do not wire it to player selection flags. This
restores the proven populated blue cells and pointer hover, not an unproven
lineup-dependent colour mapping. SCF numeric-cell backgrounds, alternate Squad
views, Inbox and NEXT are separate unfinished work; Gate13 remains OPEN.

The host must update only existing background images for pointer motion,
without taking a new game snapshot, rebuilding text, changing membership,
adding scrolling or mutating saved player flags. Popup/modal and non-Squad
screens must not retain stale background targets.

## Verification

161 focused Squad/host/pager/header-update tests passed; asset policy passed.
Test-owned withdrawn real Windows/Tk verified the production source loader
and Southport session at1x/1.5x: all30 populated rows/90 cells, exact normal/
hover RGB pixels,300 pointer events per scale with0 game snapshots and stable
photo references, header hover/exit cycles with0 game snapshots, and disk save
followed by a fresh Python process retaining the same30 native row owners.
The per-scale300-event loops took0.020s/0.014s on this machine; these are
synthetic widget-handler timings, not native/user-visible latency equivalence.
No visible/manual/audio acceptance or working ordinary NEXT is claimed.
