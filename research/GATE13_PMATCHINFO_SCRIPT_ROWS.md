# Gate 13: default captured-script row projection

4 October 2026 KST; canonical executable SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
This is a verified rendering milestone, not Gate-13 closure.

## Reader, eligibility and ownership

`original_pmatchinfo_script_rows.py` consumes the retained packed script, not
scores or reconstructed semantic events. The actual `633C50/633D00` reader
provides truncated native field widths and the inverse chance-tag mapping.
Non-row families consume their exact encoded widths but expose no invented
presentation fields. Truncation, extra bytes and nonzero padding are rejected.

`487B80` stores ordinary mode zero and calls `4872C0`. Both ordinary concrete
lists filter event +4 == 1. The executable does NOT filter by the list's +50
side. The two switch tables at `48743C/48745C` classify kinds 0..10 as
`0,0,0,0,0,1,4,4,4,2,3`: chance outcomes 0/3, incident5, marker9 and
duplicated substitution10 are selected; kinds6..8 are ignored. No modern
home/away predicate is substituted for this surprising native behavior.

`486EC0` computes duplicate/prior-card state before shifting past marker9.
`485B30` resolves report-owned participants: ordinary goals use +88, inverted
goals +84; incident and substitution paths use +88. Substitution participant
index depends on the concrete list-side constructor argument. Six visible
slots use 38px spacing.

## Written text, geometry and original art

`485F50` binds the previously recovered labels/icons. Its decimal buffer starts
with the decoded minute. Duplicate rows omit the source English2554 suffix
`" MINS"`; only its specific goal/shootout branch clears the decimal entirely.
Duplicated substitutions retain the minute number. Boundary and repeated-card
flags are retained rather than deduplicating the source entries.

Shared setup `483500` puts original name/incident grids at (0,0)/(189,0), icon
at (191,11), label at (210,2), decimal at (210,18), abbreviated player name at
(40,2), and the shirt at (0,2). Parent translation adds 145 to list y115.
The two popup-local list clips are (39,260,332,228)/(411,260,332,228).
Text uses source BdXCn16, style0x21 and native vertical metrics/control clips.

`417AE0` mode0 writes `%c. %s`, or surname alone when the first-name byte is
`-`. `5D6C50` first tests live player +14 bit4 (white), then bit5 (RGB
E8/BF/5E). Both actual persisted runtime selection flags are consumed. The
renderer retains those explicit pre-display-packing RGB channels with source
glyph alpha; this does not certify legacy display-format quantization/blending.
Unknown +174 color branches do not receive a white/default approximation.

`485D80 -> 5EF940` selects original kit context using primary/alternate colors
and the canonical sentinel-terminated clash table at `834AF8`. Compact reader
`4022D0` maps disk+3A/+46 to club+4A/+56; `403660` copies them unchanged.
`408320` loads the custom `40DA90` basename before any generic kit fallback.
The existing recovered byte-level art-name translation is reused.
`485F50` selects source frame `(captured shirt number - 1)*32`, not generated
digits. Twenty deliberately imported 36x1280 custom atlases cover the original
Premiership primary custom-shirt family, including the genuine Coventry/
Middlesbrough route; canonical provenance is in the asset manifest. Generic/
alternate and out-of-range shirts stay unavailable rather than using a substitute.

`6510F0/483750` create and paint all six slots, including original blank grids
when fewer records exist. `487520/487550` set scroll bounds to
`max(native count - 6, 0)`. The source `483AA0` top/down control rectangles are
(17,260,18,25)/(17,460,18,25) and (389,260,18,25)/(389,460,18,25), after parent
translation. Arrow events3/5 and6/8 reach `650020 -> 64FF30 -> 4874B0 ->
6512A0`: one entry per accepted press, clamped to those bounds. Row factory
`486EE4` uses viewport offset plus slot; duplicate/prior-card/boundary scans
remain global rather than being reset at the viewport edge. `64F7A0` rejects
an already-pressed control; `64F860 -> 64F470(0)` clears bit4 on release without
a second scroll. Tests and real Tk press/release exercise this distinction.

`5F2BC0/5F2C00` bind two 18x25 slices of canonical `scroller_vert.444`.
The 72x50 atlas hash is
`3f96ef29d80c7d369f65236c29ae8281b7e490c3c71a65644490daefe5f1f9f7`.
`64FDB0/64E5D0` select idle0/pressed1/disabled3 across 18px horizontal frames.
The original atlas is provenance-imported, not drawn as modern arrows. The
thumb/bar, hover flags and six-tick held-repeat cadence are not yet certified
by this implementation; wheel/drag/repeat are not guessed.

The directly required thumb/bar continuation is now narrowed to original
loaders `5F2DA0/5F2E30/5F2E80/5F2F10`: respectively
`scroller_bar_vert.444`, `scroller_blue_bar.444`, `vscroll_end.444` and
`vscroll_blue_bar.444`. Thumb descriptor946FB0 binds an 18x25 source slice,
flags0xD. Startup603540 sets renderer87BEE8 to vtable7D7AB8, whose drawing
slot+8 is64EBE0 and whose cap inputs are both3. That renderer's native
page/range arithmetic and composite blits still need complete adjudication,
especially the zero-range x87 conversion/clipping path. Exact filenames or
the partial window are not permission to invent a knob, tiling or rounding.

## Genuine Windows milestone

65 focused resource/row/host tests pass. The genuine calculated fixture2
(Coventry5 vs Middlesbrough11), complete publication, disk save, fresh reload
and actual Tk Fixtures right-click all pass. Twelve visible native row owners
now render labels/minutes/names/icons/custom numbered shirts. Both lists reach
all eight source entries, including the 89-minute substitutions, through actual
Tk arrow clicks. Repeated held presses and disabled bounds do not step; release
allows the next press. No report
context is manufactured, and no report/save/calculator implementation changed.

Private receipt `gate13-calculated-reload-script-scroll-20261004.json` SHA-256:
`dda3d6c6cdb289cd953fff6413b6f0fd762c159a3af7d8a7921e60642821840c`.
Private PNG: `gate13-pmatchinfo-script-scroll-20261004.png`. Expanded owner,
control and kit evidence: `gate13-script-scroll-owner-private-20261004.json`,
SHA-256 `b4e18704c6c3dde7088a7bf6dfa241e32cc5ef054e77b5885f7e87057cee861a`.
All reside outside Git beneath the authorized local scratch directory. The
earlier first-six-only receipt remains historical, not final scroll evidence.
The final PNG captures actual HWND bounds; the earlier desktop bounding-box
capture was DPI-cropped and is not a complete-report visual audit.

Final milestone validation: 1,791 full reconstruction tests, 23 expected
licensed-source skips, zero failures/errors; private receipt
`gate13-script-scroll-full-suite-20261004.json`. The initial full invocation
omitted the private Capstone module path; it was rerun with that verified
dependency available. Fresh real Windows schema8 passes on final code,
`gate13-script-scroll-schema8-20261004.json`, SHA-256
`131866c416673c306c932a11899dc4bfe3810c60ee683fd87e82aa7aae2e8cc9`.
Repository asset policy, JSON and diff guards pass. This is not a frozen-package
launch, timing sign-off or Gate13/Gate17 release claim.

## Still-open closure boundary

This milestone does not certify the complete report surface across normal
contexts: thumb/bar/hover/held-repeat behavior, required unstaged shirt
contexts and display-color fidelity need final adjudication. Blank slots and
single-press arrow traversal are now integrated and tested. Fresh uncontrolled
club +13C/+140 remains unknown. The constructor iterator `6687C1` only calls
the supplied constructor per element; it does not initialize the club-array
payload beyond that constructor. No zero-filled allocation is assumed.

Gate13 remains OPEN. Continue those concrete source-backed boundaries, then
run the final genuine route/full suite/Windows schema8 and roadmap audit.
Disjoint Gate14 work and the ownership protocol remain unchanged.
