# Original Squad number text — 9 October 2026

## Original evidence and minimal correction

The Southport screenshot showed blank leftmost cells in both populated lists.
This is a missing text binding, not evidence for scrolling or omitting numbers.
The private canonical executable was reverified as SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Manual call/argument flow establishes:

- `CSquadPlayerList` vtable7C5AF4 +C8 is factory4B6E80. It passes list+50
  (represented team), selected player and parent to48A8E0. The constructor
  retains player at row+74 and team at row+78.
- Populated `PSquadPlayerRow::489530`, specifically48979D..4897F3, registers
  child+1E8 and calls41E3F0(player,row+78). That helper reads team+4, then
  calls41E3D0: compare with signed DBRPlayer+10; read byte+70 on equality,
  byte+76 otherwise. The caller masks the result withFF.
- Exact numeric rectangle `(1,1,22,14)`, raw alignment flags24, font94758C
  (verified original18px Squad font), whole-number `%N` at81ACAC and white
  endpointFFFF.6507A0 forwards setup to6503F0 and format to655F40. Auxiliary
  wrapper87B6B0 is not the format string or another font.
- Native list parents remain x37/x418, panel y79. Empty owners have no
  numeric child. A retained byte0 formats as `0`; it is not an empty sentinel.

The bridge now exposes the selected byte separately from primary
`shirt_number`. The viewport retains it; the host rasters both native owners.
No roster order, selection flags, RNG, save schema, source font or scrolling
behavior changed. Unavailable alternate/loan context stays blank: no primary
number is borrowed on mismatch. Missing primary bytes no longer become an
invented zero via `getattr(...,0)`.

## Validation and limits

- 1,024 bounded comparisons of actual41E3F0/41E3D0 instruction bytes passed:
  all256 primary bytes, distinct alternate bytes, matching/mismatching team
  IDs, signed-1 versus unsigned65535, selected byte and stack cleanup. No
  original process launched.
- Real **withdrawn, test-owned** Windows/Tk widgets ran the production menu
  -> Southport -> paired Squad/loader/renderer. All30 numbers rendered at1x
  and1.5x, then survived disk save and a fresh process/presenter/projection.
  This is not visible/audio/normal NEXT acceptance.
- 228 focused Squad/bridge/presenter/host tests passed /13.103s; asset policy
  passed. Six new regressions cover selector context, unknown/zero,
  raster clipping, holes, both-owner host transport and bridge validation.
- Full suite:3,070 /166.821s /25 skips; four failures/one error. Three
  failures/one error are the existing disjoint Gate17 package-lock digest
  drift. The extra source-audit subprocess resolved a duplicated repo path
  under sandboxing; that unchanged test passed outside it /0.062s. The full
  suite is **not green**. No Gate17 check was relaxed or changed.

Private comparison/Tk/reload harness SHA-256:
`5f4353988f8f358453d66ca8d320c4ef47fb5a94b50729116f46995e6ddd42f9`.
Executable, private player receipt, harness and saves remain outside Git.
The immutable playtest170970e5 is unchanged and does not contain this fix.

Ordinary NEXT/live pre-match input/modal binding remains the main playability
boundary in `GATE13_ORDINARY_ADVANCE_BOUNDARY.md`. Gate13 is not closed and
this correction does not establish an original-look playable build.
