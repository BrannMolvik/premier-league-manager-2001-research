# Explicit temporary travel playtest, 7 October 2026

Daniel approved a separate development-mode fallback while the original-style
management host remains unfinished. `development_playtest.py` is that fallback,
not a new production default and not Gate-13 closure. It calls the existing
verified canonical controller, primary scheduler and internal-save codec;
no scores, reports, capacities or unavailable source inputs are manufactured.
Generic widgets, autofill and background work are explicitly developer tools.

## Verified on Daniel's Windows PC

- A canonical Southport session retains all 30 players and the actual
  22-club Conference table. It does not reuse the bridge's Premier-only table.
- Actual window buttons Take Control, Auto Fill, Advance and Play were operated.
  Southport-Telford calculated 1-1; player condition and the Conference table
  updated. The UI remains responsive while scheduling/calculation runs.
- Daniel completed the Save dialog and supplied Downloads/train-playtest.fm2k.
  The exact supplied file loads into a fresh controller, retains all 30 players
  and the completed game date, and continues through Southport-Kettering and
  Dagenham & Redbridge-Southport. Each additional fixture was calculated,
  saved to a private disk file and reloaded. No original game was executed.
- Independent pending-match and completed-match disk reload also succeeded.
  A first advance took about 10 seconds; two later full scheduler/calculator
  passes took about 21 and 17 seconds. No constant-time performance promise.
- Five developer-session regressions cover full-roster retention, runtime
  selectable clubs, primary/procedural routing and actual League ownership,
  explicit pending participants, disk roundtrip and failed-load preservation.

Private receipts: development-train-proof.log, train-user-save-proof.log,
train-user-save-proof.json and development-ui.stderr.log. User game data and
saves remain outside Git. The actual Load dialog itself is not yet certified
by this record; the same callback's codec path is tested separately.

## Original-layout diagnosis: do not invent scrolling

The previous initial-20 slicing proves a host omission, not a native scroll
contract. The user correctly directed attention to the paired first/reserve
view: recovered control 3 enables both PSquadList owners at (37,0) and (418,0)
inside the (0,79) panel. The native 4B6FE0 mapper uses selection-dependent
slots/empty rows, first selection counters from 407060, reserve counters from
4070F0, the actual 408500 competition substitute quota, filtered-list count
from 48B6E0 and context+ D8. Counts are not guessed 20/10 membership.
4B7170 emits the appropriate empty-row owner for -1; 406F00 reads the ordered
team +244 word array. The current host's direct first-20 projection is not
that mapping. Remaining required proof: the context D8 producer and exact
ordering/availability lifecycle consumed by those counts, followed by both
original list owners and pointer bindings. No prototype scrollbar is promoted
into an original-game solution, and no guessed split is implemented.

## Limitations

This offers lineup/autofill, advance, calculated results, the selected live
League table and port save/load. It does not provide the complete original
management UI, transfers/finances interface or original save compatibility.
Only several fixtures have been acceptance-tested, not a six-hour session or
a complete season. Save frequently. Production startup verification is not
bypassed: this separate entry point has no startup movie path in the first
place. The normal original-style entry point and its checks remain intact.
Unsigned frozen-executable distribution acceptance remains separate; Windows
security settings are unchanged. No main merge or agent-runtime write.

## Pinned local handoff and final regression

The independent source snapshot at
`C:\Users\Brann\Documents\Codex\FM2001-Train-Playtest` is pinned to a91ad35e.
Its `Launch development playtest.cmd` uses the installed Python 3.13 runtime,
not the unsigned frozen executable. The exact launcher opened its labeled
window successfully. An independent import from that snapshot loaded Daniel's
supplied save, retained 30 Southport players, and passed a fresh-controller
disk roundtrip. The Load dialog was opened, but UI automation could not reliably
target its owned modal; this is not claimed as completed Load-button acceptance.
The startup source archive SHA-256 is
`a133bdb9eec6deea3bdf242d13c63d5c677e89d42a231fa740c0f9336b4c1be3`.

Integrated focused validation: 106 tests passed; final targeted validation:
14 tests passed with one opt-in skip. Full reconstruction with the private
Capstone dependency available ran 2,953 tests in 341.283 seconds: three failures,
one error and 24 skips. All four non-passes are the unchanged Gate-17
FFmpeg toolchain package-lock fixture/digest tests, not new startup/fallback
failures. This is NOT an all-green full-suite claim. Asset policy and diff
whitespace checks pass. No proprietary saves, data or private receipts entered
Git, and no Gate-13 completion claim is made.
