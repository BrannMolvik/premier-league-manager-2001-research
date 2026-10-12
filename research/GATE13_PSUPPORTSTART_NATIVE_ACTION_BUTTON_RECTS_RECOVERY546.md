# Recovery546: original PSupportStart exit/tick source visual rectangles

Owner original footballmanager.exe 4,714,541 bytes SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. Static disassembly only, no original exe launch or Win11 GUI acceptance.

Original native PSupportStart vft+4=0x4C7B70 creates child event1 at object+0x1EB8 and calls 0x5D3900 at 0x4C7CF3 with x=0x2D9=729, y=1, sprite wrapper0x946190, flag0. Event2 at object+0x1F08 calls 0x5D3900 at 0x4C7D2A with x=0x2B9=697, y=1, wrapper0x946150, flag0.

Original 0x5D3900 forwards four source parameters into 0x651E30 at 0x5D39AC; 0x651E30 passes x/y and sprite to 0x651BA0. Original 0x651BA0 reads cropped sprite width/height from wrapper+0x14/+0x18, then calls 0x64F380, storing visual x/y and computing right/bottom. The original wrappers are SHA/source-verified original GenericButtonsAndBars/exit_button.444 and tick_button.444 with source EA444 header30x90 and each native 30x30 cropped frame. Exact source visual rectangles in the 760x500 PSupportStart client are therefore event1 EXIT (729,1,30,30) and event2 TICK (697,1,30,30). Original event1 result0 without Apply; event2 executes 0x4D0830 full staff+name Apply then result1.

These are visual/layout child rectangles, NOT independently proven native mouse hit masks, hover frame states, screen parent absolute origin, or Windows11 actual GUI acceptance. Port changes only the source action DTO and exact original-derived regression; no live click wire or altered staff lists.

Private reproduction: objdump -D -Mintel --start-address=0x4c7cc3 --stop-address=0x4c7d2e footballmanager.exe; objdump -D -Mintel --start-address=0x5d3900 --stop-address=0x5d39b8 footballmanager.exe; objdump -D -Mintel --start-address=0x651e30 --stop-address=0x651e8b footballmanager.exe; objdump -D -Mintel --start-address=0x651ba0 --stop-address=0x651bdf footballmanager.exe; objdump -D -Mintel --start-address=0x64f380 --stop-address=0x64f3be footballmanager.exe.

Source exact for bounded geometry only. Original full PSupportStart control edits/close return, Inbox CRT selected body, R1 all modes and Win11 Gates13–17 release remain OPEN. PR638 blocked.
