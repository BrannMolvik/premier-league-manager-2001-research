# Recovery552: original PSupportStart action button visual rectangles

This source-recovers the exact two original actionable visuals and
integrates the prior draft PR #645's verified narrow result into the
current source-based **whole modal milestone**, avoiding a separate
small CI/review cycle. Original file
`footballmanager.exe` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

At original `PSupportStart` virtual+0x04 `0x4C7B70`,
native child event1 at object+0x1EB8 calls `0x5D3900`
with original position (729,1) and original 0x946190
exit-button wrapper at `0x4C7CF3`. Child event2
at object+0x1F08 calls the same native source method
at `0x4C7D2A` with (697,1) and original 0x946150
tick-button wrapper. `0x5D3900→0x651E30→0x651BA0→0x64F380`
stores x/y and sprite cropped width/height; SHA-byte-proven original
`exit_button.444` and `tick_button.444` are 30×90
three-state atlases cropped to 30×30 by native resource wrappers.

Thus the source native client rectangles are exactly
`Exit/event1=(729,1,30,30)` and
`Tick/event2=(697,1,30,30)`.
Original event1 returns modal result0 without Apply;
event2 invokes actual original staff/name Apply then modal result1.

**Important:** the rectangles are original layout bounds,
not verified click hit masks, user event gating, hover state,
screen absolute origin or live Windows11 acceptance.
This is one component of a full seven-row original
SupportStart UI integration; old draft PR645 remains
unmerged and should be explicitly superseded once a
coherent reviewed modal feature PR integrates its work.

Reproduce privately:
```bash
objdump -D -Mintel --start-address=0x4c7cc3 --stop-address=0x4c7d2e footballmanager.exe
objdump -D -Mintel --start-address=0x5d3900 --stop-address=0x5d39b8 footballmanager.exe
objdump -D -Mintel --start-address=0x651e30 --stop-address=0x651e8b footballmanager.exe
objdump -D -Mintel --start-address=0x651ba0 --stop-address=0x651bdf footballmanager.exe
```
