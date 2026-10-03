# Ordinary Fixtures -> PMatchInfo: capture and native input

_Local/private Windows trace, 3 October 2026. Gate 13 remains OPEN._

## What is now source-closed

The authorized executable was reused, not downloaded or substituted. Every
trace parses through `OriginalPE32` and requires SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
The management backdrop from PR #177 was not retraced or changed.

### Capture eligibility and ownership

- `0x51145B..0x511470` checks **participant counts**, calculator `+0x5A4`
  and `+0xB54`. They are not pointers. `MATCH_ENGINE.md` already identifies
  the corresponding participant arrays at `+0x04` / `+0x5B4`.
- `0x60BE50` first calls `0x60B7F0`, `0x60BA80`, `0x60B8D0`, then rejects
  through `0x516080` when global byte `0x877558` is nonzero. The existing
  developer-switch trace identifies this as `/skipmatchcalc777`, not an
  unexplained football-specific policy.
- On the non-rejected path it calls `0x60BBC0`, `0x60BCB0`, `0x60BD90`,
  `0x60BE20`, then returns success. Eligibility is **not** proof that a
  complete report was actually produced.
- `0x60BF10` allocates the 0xF4 record. Successful capture allocates a
  12-byte list node, appends via `0x617D70`, increments the owner count and
  writes the previous count's low word to match `+0x40`. Failed capture
  destroys the record and does not assign a link.
- The root global is `0x8755F8`: count at `+0`, head at `+8`, tail at `+0xC`.
  Each node has report payload `+0`, next `+4`, previous `+8`.
- `0x60BF90` loads count followed by records through `0x60B470`, appending
  in that same order. `0x60C020` saves count then head-to-tail records through
  `0x60B240`. Season cleanup at `0x4F9849..0x4F9874` clears the owner.
  A result-table entry is not a replacement for this persistent owner.
- `0x511370` is the match completion path: it marks native status bit 0,
  runs the preceding completion helpers, and reaches the above capture.
  Do not move capture to match setup or reconstruct its payload later from
  scores. The shared scalar fields also contain attendance: existing
  `GATE10_LIVE_CASH_FLOW_TRACE.md` maps calculator `+0xD84/+0xD8C/+0xD90`
  to total/home/visiting attendance; the captured record copies them to
  `+0x30/+0x38/+0x3C`.

### Exact direct scalar copies

`original_fixture_report_capture.py` implements only the eleven direct copies
in `0x60B7F0`; it deliberately cannot manufacture the rest of the report.

| Report offset | Calculator offset | Bytes |
| --- | --- | --- |
| `+0x30/+0x34/+0x38/+0x3C` | `+0xD84/+0xD88/+0xD8C/+0xD90` | 4 each |
| `+0x40` | `+0xD9C` | 1 |
| `+0x94` | `+0xB68` | 4 |
| `+0x98/+0x9A` | `+0xFE0/+0xFE4` | low 2 each |
| `+0xA0/+0xA1/+0xA2` | `+0xD46/+0xD45/+0xD44` | 1 each |

Other helpers copy/generate the following distinct data, not zero-fillable gaps:

- `0x60B7F0`: `0x62AC80 -> 0x514220` low-word field `+0xF0`, three dwords
  from `0x632570` into `+0x24/+0x28/+0x2C`, and `0x5146B0` caption at `+0x41`.
- `0x60B8D0`: side team IDs, count-derived low-nibble participant metadata,
  ordered participant IDs/positions/ratings/flags in 12-byte records at
  arrays `+0x84/+0x88`, and calculator `+0x1154` into record `+0x9C`.
- `0x60BA80`: packed score nibbles from `+0xD4C/+0xD50`, conditional second
  score from match `+0x58/+0x5C`, and score-sized goal arrays `+0x8C/+0x90`.
- `0x60BBC0`: count/triplet array `+0xB0/+0xB4` from `0x631270/0x631290`,
  then native averaged possession bytes `+0x20/+0x21/+0x22`.
- `0x60BCB0`: two packed participant-statistics blocks at `+0xB8/+0xD4`.
- `0x60BD90`: goal minute/player/flag data from calculator's linked events,
  stopping on event kind 9; do not invent scorer IDs from score totals.
- `0x60BE20`: variable script bytes/count via `0x633610` into `+0xAC/+0xA8`.

### Native event acceptance is no longer unknown

`0x531CF0..0x531CFA` registers message `0x204` (WM_RBUTTONDOWN) to `0x5320B0`.
The callback passes its point through `0x5326C0 -> 0x653D80 -> 0x653600`.
Layer dispatch checks native visibility/activation and half-open rectangles;
the child dispatch calls vtable `+0x78` with owner forwarding enabled.

PLeagueGrid vtable `0x7C23D0 +0x78` is `0x64F960`, **not** left press
`0x64F7A0`. It requires enabled flag bit 1 and right-pressed bit 5 clear.
PLeagueFixtures vtable `0x7C24B8 +0x1C -> 0x42DE00` accepts the pre-owner
callback; `+0x20 -> 0x46E620` accepts only child control ID `0x59` and calls
`0x46D390`. Exact grid reduction and signed report-link lookup remain as in #177.

The separate `0x46D400` hover/cursor predicate checks non-null fixture and
native completion bit 0. It is not a report constructor and is not used as a
substitute for the independent `+0x40` link.

## Integrated boundary and truthful limit

The real host now binds `<Button-3>` to that proven gesture. The presenter
resolves the currently visible matrix cell's fixture ID, and the read-only
bridge resolves only an explicit ordered `captured_match_reports` owner plus
`fixture_match_info_links`. Missing capture ownership is a no-op. Malformed
owners/links and mismatched fixture contexts fail closed. Left press is not
repurposed into opening a report. Modal close clears its retained context.

**The GameState producer and save projection of a complete native report are
still absent.** Injected-owner unit tests prove the read-only routing contract,
not capture production in normal play. The Windows audit explicitly leaves
ordinary successful opening and secondary-context reconstruction **false**;
it newly verifies the real right-press binding and uncaptured-fixture no-op.
Do not relabel the existing explicit popup seam as normal-play success.

## Single next implementation blocker / source-backed action

Materialize and persist the complete completion-time captured report and its
append-order link in GameState/internal save. Continue from the above helper
windows, especially participant packing `0x60BCB0` and script extraction
`0x633610`, reconciling them with the exact existing calculator outputs and
post-calculation attendance/environment/participant state. Preserve capture
order and season reset. Only then run a real calculated fixture -> save/reload
-> native right-press -> correct PMatchInfo context audit and criterion-level
normal-play/timing assessment. No score-derived, completion-derived, opaque
placeholder or partial scalar projection may be promoted to a real report.

This is the normal route blocker, not a request to widen Gate 13 to obscure
secondary fidelity or duplicate the parallel Gate-14 audio/FastView work.

## Reproduction and validation

`gate13_fixture_report_source_trace.py --original-executable <authorized exe>
--output <private path outside Git> --disassemble` regenerates 28 bounded
windows and checks five native vtable slots. Hash mismatch or slot mismatch
fails before saving the report. Reports, original binaries and packaging output
remain outside Git. Final test/Windows/package receipt identities are recorded
in the closure audit and project state, not committed as uncontrolled dumps.
