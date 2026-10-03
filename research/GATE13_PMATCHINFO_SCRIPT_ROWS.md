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
digits. Two deliberately imported 36x1280 custom atlases cover the genuine
Coventry/Middlesbrough route; their canonical provenance is in the asset
manifest. Unstaged, generic/alternate and out-of-range shirts stay unavailable.

## Genuine Windows milestone

60 focused resource/row/host tests pass. The genuine calculated fixture2
(Coventry5 vs Middlesbrough11), complete publication, disk save, fresh reload
and actual Tk Fixtures right-click all pass. Twelve visible native row owners
now render labels/minutes/names/icons/custom numbered shirts. No report
context is manufactured, and no report/save/calculator implementation changed.

Private receipt `gate13-calculated-reload-script-rows-20261004.json` SHA-256:
`65ba38b69e27f511f438d2a5adb1db7cc739074655b47abee3daec566f88722b`.
Private PNG: `gate13-pmatchinfo-script-rows-20261004.png`. Private expanded
owner evidence: `gate13-closure-tail-private-20261003.json`, SHA-256
`3acde972d8d28b546854324c22538693a19b034b33ca2494d4e63dd21ed7cdec`.
All reside outside Git beneath the authorized local scratch directory. The
expanded evidence supersedes the older same-path private trace digest.

## Still-open closure boundary

This milestone does not certify the complete report surface across normal
contexts: empty native rows/scroll interactions, unstaged required shirt
families and display-color fidelity need final adjudication. Fresh uncontrolled
club +13C/+140 remains unknown. The constructor iterator `6687C1` only calls
the supplied constructor per element; it does not initialize the club-array
payload beyond that constructor. No zero-filled allocation is assumed.

Gate13 remains OPEN. Continue those concrete source-backed boundaries, then
run the final genuine route/full suite/Windows schema8 and roadmap audit.
Disjoint Gate14 work and the ownership protocol remain unchanged.
