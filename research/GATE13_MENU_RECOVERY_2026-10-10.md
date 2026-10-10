# Ordinary management menu recovery — 10 October 2026

Scope: Daniel's missing Inbox and broken MENU actions/presentation. Gate13
remains OPEN; no later-gate implementation, original process or runtime-owner
change. Source truth is canonical footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.

## Original behavior and minimum repair

Re-read actual 47AD60/47C928/4C3280/4C3770, not just the previous audit:
accepted child323 invokes PStartMenu and returns a null panel; 47ADC5 exits
without ordinary child selection/refresh. 4C3280 replaces the UI stack without
resetting the live game. Continue event1 invokes PMenu through4C2FB0. The
reconstruction wrongly attempted an unsupported content panel. Repair the
shared action/session/host route, retain the game identity and return through
Continue; no new menu or confirmation is invented. New Game's separate
existing-game prompt and fresh Continue disabling remain separate boundaries.

Re-read concrete row vfts7C3A20/7C3A80 +2C ->47ACF0. A nonnull event with
+20==2 sets/clears mask8 in BOTH embedded arrow+74 and background+C0 according
to its inside argument; other events do nothing. Existing source-qualified
whole-row SelectBmp acceptance/geometry and selected/disabled setters remain
unchanged. Shared652780/6527F0 advances/retreats one frame per visible-owner
update, with the already-recovered child11/11/1 and title11/1/1 partitions.
Current host instead fixes every arrow at frame0 and never observes row hover.
Reuse the existing source helpers and serialized management idle update pass,
updating only menu bitmap items; no invented millisecond timer, gameplay
snapshot per frame or hover-induced selected/text-color change.

## Evidence and acceptance limits

Prior trace anchors: GATE13_PMENU_CHROME_TRACE.md (concrete resources, fonts,
geometry, animation and press ownership), recovery451 Return special-case.
These have been challenged against the actual canonical instructions locally.
Raw disassembly and bounded probes remain private outside Git.

Return/Continue currently passes110 focused tests including two normal host
click routes and retained backend identity. This is integration verification
with FakeTk, not physical-mouse Windows acceptance. Inbox is still absent;
do not conflate pending simulation queues with delivered per-user EAMail.
Its genuine mailbox producer/persistence and native screen owner must be
connected before claiming Inbox restored.

## Verified implementation checkpoint

Private menu-hover-proof.py executed actual47ACF0/64F710/64F750 in96 cases
(null/other/event2, inside/outside, preserved unrelated flags); title vft7C3B98
executed actual6527F0/652780/652AE0 across832 cases. No native method replaced;
controls/flags are fixtures, sound service is absent and repaint parent is null.
This is bounded native code proof, not original-process UI observation.

148 focused tests passed in24.198s (presenter/compositor/chrome/action/session/
management/host). Private menu-withdrawn-tk-check.py then exercised real Windows
Tk/production resources at1x and1.5x:20 menu updates per scale, no gameplay
snapshot or item/photo growth, exact source arrow/background indices, and
Return/Continue preserving the same Southport game and all30 roster owners.
Twenty updates took0.263s/0.041s, not an end-to-end latency acceptance claim.
Setup and input were explicit test adapters, not physical-mouse acceptance.
The separate bounded visible source-only launch reached Southport but capture
returned unrelated foreground pixels; no clicks were sent and it expired.
No original process, user save or other app was manipulated.

Inbox dependencies have existing private original-function fixtures for three
actual pending families, delivered-user ownership, filter/sort/lifecycle and
text/detail leaves. These are NOT a live integrated Inbox. Preserve their
explicit substituted RNG/staff/graphics/text contexts; do not populate a fake
mailbox from those fixtures or promote pending suggestions to delivered mail.
