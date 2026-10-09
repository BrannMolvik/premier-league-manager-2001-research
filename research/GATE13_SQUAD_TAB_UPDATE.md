# Squad tab update contract — 9 October 2026

## Original contract, before implementation

Canonical executable SHA256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
was independently rehashed. No original Windows process was launched.
Private bounded disassembly and comparison receipts stay outside Git.

PSquadScreen setup4B5720 registers controls3/4/5 at local37/113/189,92,
73x25, in the update-child array +2C. Its +48 count is4: the pitch owner
and these three controls. Constructor42DEB0 installs vft7BE814, whose
+68 is6527F0, +AC is652AE0, +A8 is652BC0, +98 is5D4D70.
Visible-owner traversal6538F0 invokes each visible update child's +68 once
per serialized UI pass. No millisecond hover timer is present in this path.

652AE0 selects group2 when flag2 is clear, group1 when8000 is set, else0.
652BC0 returns group lengths **11,1,1**, NOT Button@ease's11,11,1.
652780 rescales subframe with integer newLength*oldSubframe/oldLength when
the group changes.6527F0 increments toward the current group's last frame
while flag8 is set and retreats toward0 otherwise.5D4D70 uses source-row
bases0/11/22. Thus selected control3 stays at frame11 even when hovered;
enabled unselected controls4/5 advance0..10 and retreat10..0. Other atlas
rows must not be assigned meanings simply because they exist.

Pointer callback64FBE0 and setter64F450 retain flag8 from half-open native
control containment. Stored origins acquire the existing PSquadScreen
parent(0,79), giving screen37/113/189,171. Existing source caption colours
remain selected black / ordinary white; hover does not recolour text.

## Minimum implementation and limits

Restore those three state machines on the existing serialized management idle
update pass, alongside the recovered header. Update existing tab bitmap items
in place: no full gameplay snapshot, canvas rebuild, new timer or click action
on pointer motion. Main-menu, popup/modal and non-Squad ownership must not
animate stale tab items. Full panel/viewport/data changes retain fresh draws.

This does not enable unfinished formation tabs. Their actual container events
4B8E70 bind first/reserve to the LEFT and a separate PSquadPitch on the right.
New read-only tracing confirms pitch resource8376E4 -> coaching/pitch/pitch.444,
wrapper943F10; title_bar_31/30 wrappers9467F0/9467B0. Placement4B60A0/4B5ED0
depends on actual role counts/aux normalization405FF0/406320 and user-manager
shape bytes180/183 via5F0CC0/5F0BD0, not a modern formation diagram. Complete
live input/producer/render coverage is still required before ordinary tab
activation. No guessed shape defaults, arbitrary player coordinates or blank
tab wiring are introduced. Inbox and NEXT remain separate unfinished work.

## Verification

Offline execution of canonical6527F0/652AE0/652780/652BC0/5D4D70 matched
the clean-room state and source offsets for6,656 cases: all valid current
group/subframes, all low8 flag combinations and selected8000 clear/set.
Only UI invalidation64F600 was stubbed as an explicit no-op; no original
process or game state was involved. Original vtable bytes were used.

Withdrawn real Windows/Tk used the production loader and a fresh Southport
session at1x and1.5x. Four hover/retreat cycles took exactly40 visible tab
updates per scale;240 actual Tk bitmap reads matched the original atlas via
the production scaler. No game snapshots, full redraws, new canvas items or
photo-reference growth occurred. All30 Squad player owners remained intact.
This is not manual/visible/audio acceptance or working formation activation.
