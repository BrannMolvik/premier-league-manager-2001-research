# Native management background and remaining fixture-report boundary

3 October 2026; canonical executable SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Authorized ZIP SHA-256 was independently rechecked as
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
Raw executable, extraction inventory and disassembly remain outside Git.

## Management base is resource lookup, not procedural generation

`0x5D3490` decodes current date `0x9847FC` with `0x64CCD0`, uses its
one-based month to index `0x83339C`, and passes the club/variant to the
two-entry refcounted image cache at `0x5D3560`.

| Month | Background suffix |
| --- | --- |
| January, February, December | `background2` |
| March, April | `background3` |
| May through August | `background0` |
| September through November | `background1` |

Exact lookup order under `FM2001_Art/Generic/Team_backgrounds`:

1. `<country-art-directory>/<club-art-basename>_background<variant>.444`;
2. same club's `_background.444`;
3. `generic<fan-base-band>_background<variant>.444`;
4. static handle `0x9460B0`, initialized from `generic.444` by `0x5F5010`.

The comparisons are signed 32-bit: fan-base band is 0 for values >20,
1 for 9..20, and 2 for <=8 (including negative encoded dwords).
This is native club `+0x70`, not a randomly selected fallback.
`0x64DB90` supplies the slash, underscore and `.444` literals.
`0x40C850` uses `International` for team categories 2/3; otherwise it
uses country getter `0x411610`. Both country and club getters normalize
through `0x5EFCD0`: identity CP1252 bytes except space/dot/apostrophe ->
underscore, Ü/ü -> U/u, Ö/ö -> O/o, Â/â -> A/a. No generic accent stripping
or display-name slugification is justified.

The art fields are independently recovered from the readers:

- Master.dat club +179 -> native `+0xE0`, getter `0x40DA90`;
- Static.dat country +41 -> native `+0x34`, read call `0x410778`,
  getter `0x411610`.

These fields now reach the immutable management header through the existing
read-only source bridge. The application owns the base at (0,0), 800x600;
`0x432A20` replaces its initial front-end image with the recovered cache image.
The separately proven header is `back_2_<competition variant>.444`, at
(171,0), 385x95. Runtime club `+0x10` is competition identity, not country.
The native switch remains 0 -> Premiership, 21/22 -> Bundesliga,
50/51 -> LNF, otherwise generic.

## Live integration and scope

The clean host renders the exact base/header beneath its existing source-backed
management fragments. All 80 seasonal club images for the twenty original
Premiership clubs, 13 generic backgrounds and four headers were explicitly
selected with the existing inventory/import tools: 97 files, 23,109,088 bytes.
Manifest provenance, per-file SHA-256 and native geometry are tested.

The live selector is deliberately bounded to those twenty club families.
An unstaged club family raises an error: absence from this checkout must not
masquerade as native resource-load failure and select a different backdrop.
Fallback order is modeled independently but is not used to hide missing imports.
Other shell controls, header text and content pixels are not claimed complete.

Real Windows 11 schema-8 audit passed with the additional 800x600 and 385x95
PhotoImages across Squad, Fixtures, explicit PMatchInfo, exit and Tables.
Private receipt: `C:/Users/Brann/Documents/FM2001-audits/` followed by
`gate13-schema8-management-background-20261003.json`.
SHA-256: `e2fb13d57ef5f3cfc58f88c92ddc561377ee59cd04a65becd46a0f85f302dbf8`.
This is a real Tk composition/navigation smoke receipt, not an original-game
pixel comparison or certification of recognizability/timing.

## Successive native trace: ordinary Fixtures -> PMatchInfo

The next boundary was traced rather than inferred from scores:

- `0x46CA15..0x46CA24` calls grid setup `0x46CDF0` at (378,235).
  Size is 348x336, twelve columns by twenty-four rows, step 29x14;
  individual native cell controls are 24x13. The gap still reduces into
  the containing step's cell; it is not a separate modern hit rectangle.
- Owner callback `0x46E620` accepts control ID `0x59` and forwards the
  source point to `0x46D390`; native event acceptance is not replaced by
  an arbitrary Tk Button-1 binding.
- LeagueMatch vtable `0x7C4C24`, slot +0x18 -> `0x6559A0`, returns the
  match itself. Its +0x40 word indexes the captured-report list rooted
  at `0x8755F8`; `0xFFFF` and unresolvable nodes produce a no-op.
- The linked context's writer is `0x511479 -> 0x60BF10`. It allocates
  0xF4 bytes, calls `0x60B0A0`, and captures through `0x60BE50`.
  Only successful capture appends the report with `0x617D70`, increments
  the list count and writes the old count to match +0x40 at `0x60BF6C`.
  Native `0x51145B..0x511470` first requires both participant counts
  +0x5A4 and +0xB54 to be nonzero. `0x60BE50` also rejects via
  `0x516080` (`/skipmatchcalc777`). A played fixture does NOT prove a report.

`original_fixture_match_info_link.py` now tests exact grid reduction and
signed-word/list lookup, without claiming a live captured report. The current
runtime persists results/incidents but does not expose this proven captured-
report list/link lifecycle. Ordinary opening remains fail-closed.

The above was #177's handoff. Subsequent local work in
`GATE13_FIXTURE_REPORT_CAPTURE_TRACE.md` closes eligibility and native
WM_RBUTTONDOWN acceptance and adds a read-only cell/link adapter. The remaining
next implementation is complete captured-report production/persistence,
not a background retrace or an invented score-derived context.

Gate 13 remains OPEN; normal-play completeness and original menu timing still
need criterion-level evidence beyond this smoke receipt.

## Final local verification

- Reconciled `origin/main` through `8ea49594b827542196a4b5e94137ea4cecc5d176`,
  preserving both newer FastView score checkpoints without working on Gate 14.
- 73 focused Gate-13 tests passed.
- Full reconstruction: 1,534 tests passed, 22 expected licensed-source skips.
- Repository asset policy and `git diff --check` passed.
- Canonical private database check resolves all twenty Premiership club art
  fields across all twelve months: 240 exact base/header selections.
- Fresh real Windows schema-8 presentation audit passed (receipt above).

Only the feature branch is pushed for PR review; `main` and `agent-runtime`
ownership are not changed. This is a verified partial closure, not Gate-13
completion and not a Windows release certification.
