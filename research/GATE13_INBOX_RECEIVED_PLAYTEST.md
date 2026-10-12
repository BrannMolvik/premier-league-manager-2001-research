# Inbox Received header and short-path Windows playtest

Baseline main `8d81c44d` includes merged PR647/649; performance checkpoint
`da7ce0fa` is deliberately not included. Worker SupportStart branches untouched.

## Original evidence and smallest connected slice

Static canonical PE SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
No original execution or interactive Windows test.

Original `46F2C2..46F390` constructs PEAMail+D64, ID16, wrapper945C70,
parent-local (705,1), Zurich font9269F0, English global982814 (IDX2041:
Received), flags2000, zero offsets, normal white/selected black. Parent (0,148)
gives screen (705,149). Loader5F59B0 pins path836158: `recieved_tog.444`;
5F5A00 crops73x20. Existing art validator pins full73x60 hash f9fc8fb1...eb36.
Actual vtable7C2B04+98 dispatches474F80: selected y40, hover y20, idle y0;
there is no separate pressed frame in this source. 651F80 normalizes2000 to
centered horizontal/vertical alignment, reused from existing management text.

Input actual +6C=652CF0 calls64F7A0 enabled/not-held and parent acceptance;
parent7C2950+C=42DE00 returns1. Group setter652D80/652B40 selects one, not
inverse toggle. Actual +4C=652E00 removes selected headers from acceptance.
Raw dispatcher byte at47236C+15=1; slot472354+4=4721F2 clears row selection
and preview, refilters and sorts. Date comparator472C60 puts strictly newer
records first; existing bounded <=16-pointer sorter is reused. Sort/rebuild
472B4F..8A retains scroll offset and recomputes its bounds. Newly constructed
panel resets selection/sort and offset. Host only accepts header with loaded
verified art and no popup occlusion; selected re-click is a no-op.

Implemented bounded slice: actual Received header, native static/hover/selected
frames and text, ordinary click -> real delivered-user sorting -> selection
clear/list redraw, retained scrolling and fresh-panel reset. No save/RNG changes.
Only initial transfer messages and existing <=16-pointer source limits qualify.

Unknown: ten-filter label font9197E0 runtime ownership remains unclosed; native
compound children do NOT share the simplistic draw-slot interpretation of sort
headers (actual final tables were rechecked). From descriptor comparison, other
headers/categories, preview, actions, shared CRT and complete original Inbox
remain incomplete. No guessed live filter controls enabled to finish a build.

## Separate playtest distribution

Formal RC builder/provenance/smoke untouched. Afterwards a separate direct-layout
Actions artifact contains executable, runtime, PLAYTEST.cmd, README and per-file
SHA256/commit manifest. No nested ZIP, source archive, executable or database
added. Validate existing package requirements and <=240-character extracted
paths under C:\FMTest before upload. Launcher uses original-style default host,
explicit diagnostic FMV skip by default; `PLAYTEST.cmd videos` includes FMVs.
Existing original-directory chooser applies. No Python/rebuild/registry change.
Unsigned-executable SAC acceptance remains a distribution limitation; no security
exception or bypass. Package smoke is not actual interactive acceptance.

Local verification: 95 Inbox tests PASS (including licensed static dispatch
and original art checks), 118 focused host/presenter/Inbox/distribution tests
PASS, asset policy PASS. Six directly impacted control/distribution tests PASS
after the final state-frame counterexample was added. Exact build/CI/artifact
identity will be recorded in the PR after final-commit CI. Gate13 remains OPEN.
No automated interactive launch.
