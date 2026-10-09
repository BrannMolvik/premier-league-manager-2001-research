# Source-runtime startup and Squad follow-up, 7 October 2026

Canonical executable SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Only static original evidence was read; no new original-game execution.
Raw disassembly, user data, screenshots and event receipts remain private.

## Demonstrated startup regression

The source-windowed-playtest-2 receipt recorded WPF MediaEnded at
11:24:08.2758894 UTC, followed by child HWND PID=0/parent=NULL during
normal teardown. The Python viewport validator treated this as foreign
ownership, killed the player and raised the generic launch error. This was
not proof that the user pressed Escape or that media decoding failed.

An absent HWND now prevents resize/input while waiting for the actual player
exit. It is not accepted as completion: exit 3, timeout and foreign/reused HWNDs
still fail closed. Real source-windowed-playtest-5 completed EA MediaEnded at
11:51:53.1621930 and Premier MediaEnded at 11:52:48.0864430, each exit 0,
then displayed the main menu. No input was injected during those clips.
Those are source-runtime observations, not frozen-package acceptance or a
subjective audio verification.

## Native startup input boundary

461900 masks argument bit 0. If set, it saves/replaces handlers for WM_KEYDOWN
100h, WM_LBUTTONDOWN 201h and WM_RBUTTONDOWN 204h via 6A4B20/6A4BA0.
The callbacks 461BB0/461C10/461C70 set byte 876638, stop active player
876674 via 69B980/69B9C0, and forward original arguments to previous handlers.
461B62..461B93 restores those handlers. The callback does not inspect a
particular key. EA uses bit 0 clear; Premier uses bit 0 set at 531172..53117A.

The player hooks only its own child, after MediaOpened. A stopped clip returns
exit 4 plus a strictly parsed single registered-message receipt. This cannot
qualify EA or malformed/foreign input. Parent Escape is forwarded only while
that qualified player is active and cannot mutate game geometry. Other parent
input forwarding and exact native fade timing remain unclaimed. The child
hook leaves ordinary message forwarding intact, matching the native callback.

## Required Squad column headings

4B51B9..4B51D0 attaches PSquadList+8C at owner-local (238,22,91,122).
48C040/48A590 constructs four 22x99 labels at local x=0,23,46,69, y=0.
Their globals/English.idx indexes are:

| Global | Index | Text |
| --- | --- | --- |
| 984554 | 169 | Status |
| 984550 | 170 | Condition |
| 98454C | 171 | Form |
| 982910 | 1978 | Skill |

The sequential loader at 64661C qualifies Skill; previously proven First Team
166 and 1ST & RES 2490 calibrate the language reader. All four use font 8CAB80
(Zurich_XCn_BT_16pixel.fnt; the old18px claim was disproved by the direct
6044AC/6044F4/6044F9 loader on9October), white, raw flags 2050h. The first-roster
parent origin is (37,101); heading parent is therefore (275,123).
6520C0/657280/6570F0 prove counterclockwise rotation, centering by native line
height and bottom anchoring with the space glyph width as initial advance.
Each mask remains clipped to its actual label control; no modern rotated font
or guessed inset is substituted.

97 focused host, Squad-row, startup-input, WPF and playback tests pass.
Asset policy and whitespace checks pass. Existing four Gate-17 Windows
lock-fixture baseline failures remain separately reported, not weakened.

## Why this is still not a complete playable host

2673bc0e introduced first-20-row slicing from the outset, while the database
contains 30 Southport players. Remaining entries are retained but ordinary
list navigation is not wired. 62a1bbcd changed normal launch from the generic
development notebook to this original-style host. The notebook had explicit
advance/play/save controls; their presence does not prove the original host
has equivalent bindings. Current original-host omissions must not be blamed
on Escape or certified by a backend-only calculation test.

Daniel authorized a separate, visibly labeled development fallback for travel.
It does not replace or close Gate 13. Frozen signing/distribution acceptance
also remains separate from authorized source-runtime development.
