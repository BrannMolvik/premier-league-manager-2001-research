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

### PR #183 continuation: packing and script codecs source-closed

On 3 October the branch reconciled `origin/main` at
`66c0886a49581ac3461e0c242fb5e333bf73ac8c`, preserving the continuous
worker's Gate-14 changes. No runtime ownership changed.

`original_fixture_report_packing.py` now implements the recovered snapshot
codecs. They remain fragments, not complete reports or gameplay context:

- `0x60BCB0` writes **12 bits per participant**: rating `+0x30` low four
  bits followed by eight one-bit writes from `+0x35..+0x3C`, in participant
  order. The next participant is not byte-aligned. Eighteen participants copy
  27 bytes; the helper copies only `ceil(bit_count / 8)` bytes into each
  28-byte destination, not a zero-filled 28-byte replacement.
  `0x60B0A0` does not initialize these destination blocks; `0x60B240` writes
  the entire 56-byte pair. The snapshot codec therefore deliberately does not
  manufacture unused tail bytes or claim original-save compatibility.
- Those eight bytes are now source-identified by `0x630C4F -> 0x630DE0`:
  threshold `>=200` on DBRPlayer offsets `+0x1E`, integer mean of
  `+0x27/+0x1E`, `+0x24`, `+0x26`, `+0x28`, `+0x25`, `+0x25`, `+0x22`.
  The duplicated selector is real. They are **skill flags**, not numeric
  event counters or the separate FastView performance trajectory.
- `0x659CF0` ORs the supplied byte shifted within the current byte, then
  advances **one** bit. It does not first mask the input to one bit and does
  not carry overflow into the next byte. `0x659D30` explicitly masks each
  successive low bit. Both behaviors are preserved and tested.
- `0x633610 -> 0x6336A0` emits a ten-bit linked-event count, then traverses
  the entire native list in order (including records after kind 9). Every
  record first writes `+0x00` in eight bits. The calibrated dispatch covers
  kinds 1..16, all six kind-11 subcommands and both kind-5 branches, using
  `0x6337B0/0x633870/0x6338E0/0x633990/0x6339D0/0x633A20/0x633B30`.
  Unknown families/subcommands or count overflow fail closed; no unsupported
  semantic event is converted into a plausible native record.
- `0x632570` is exactly `return calculator +0xFEC`. Thus report
  `+0x24/+0x28/+0x2C` copy calculator `+0xFEC/+0xFF0/+0xFF4` dwords;
  report `+0x9C` copies calculator `+0x1154` in `0x60B8D0`.
- Captured possession is **not** the five-minute display segment list.
  `0x631270` returns 2 when calculator `+0xFF8 == 18`, otherwise 4.
  `0x631290` averages the three dword arrays starting at
  `+0x100C/+0x106C/+0x10CC` over indices 1..8, 10..17, 19..20 and 22..23.
  Boundary entries 0/9/18/21 are excluded. Dword sums wrap, averages truncate,
  and the copied triplets are low bytes. `0x60BBC0` averages their second and
  third bytes into report `+0x20/+0x21`; `+0x22` is the byte remainder to 100.
  Snapshot projection and tests now preserve this exact distinction.

**The remaining single blocker is the live completion-time calculator output
and full report owner/save integration, not either packing codec.**
`NormalMatchResult` currently retains semantic events and possession segments,
not the complete native compact-event list or required scalar snapshot.
`PreparedMatchPlayer` does not retain the native final rating/flag record;
performance finalization remains opt-in on an explicitly distinct MatchEngine
RNG. The gate receipt finalizer returns its output, but its league callers
currently discard that return. Those inputs must be retained at their proven
production points and projected into the complete report before appending any
link. A synthetic native snapshot or codec test is not that producer.

Materialize and persist the complete completion-time captured report and its
append-order link in GameState/internal save. Continue from the above helper
windows and source-closed codecs, reconciling the exact calculator outputs and
post-calculation attendance/environment/participant state. Preserve capture
order and season reset. Only then run a real calculated fixture -> save/reload
-> native right-press -> correct PMatchInfo context audit and criterion-level
normal-play/timing assessment. No score-derived, completion-derived, opaque
placeholder or partial scalar projection may be promoted to a real report.

This is the normal route blocker, not a request to widen Gate 13 to obscure
secondary fidelity or duplicate the parallel Gate-14 audio/FastView work.

## Reproduction and validation

`gate13_fixture_report_source_trace.py --original-executable <authorized exe>
--output <private path outside Git> --disassemble` regenerates 49 bounded
windows and checks five native vtable slots, five dispatch tables and the
boundary index table. Hash mismatch or calibration mismatch
fails before saving the report. Reports, original binaries and packaging output
remain outside Git. Final test/Windows/package receipt identities are recorded
in the closure audit and project state, not committed as uncontrolled dumps.
