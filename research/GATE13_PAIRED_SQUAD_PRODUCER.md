# Paired Squad producer qualification — 7 October 2026

Scope: restore the original default first/reserve view, not add a scrollbar
or divide Southport into an invented 20/10 membership split. Static canonical
executable only; no original-game launch or simulation modification.
Executable SHA-256: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

## Confirmed context lifecycle

The earlier unknown global `87686C` is the live PSquadScreen receiver, NOT a
DBRUser pointer or an allocator-derived default. Proven fresh panel factory
`47AF2D` calls `4B8240` (see GATE13_MANAGEMENT_SHELL_ROUTE.md).
Constructor `4B8240` retains its club in +C8, constructs the paired player
lists at +130/+1030 with discriminator 0/1 (`4B82A4/4B82BA`), and writes its
receiver to global `87686C` at `4B8416`. The constructor explicitly writes
+D8=0 at `4B8456`, but this is only an intermediate state: it passes
`&receiver+D8` and club to `4B7500` at `4B84C6..4B84CE` before completion.
Destructor `4B8759..4B876B` clears the global only if it still owns it.

The authoritative producer is therefore `4B7500`, not the constructor zero.
Refresh `4B8C90..4B8CB1` calls it again with the same output address before
rebuilding both player and SCF lists. The factory's paired visible-slot
mapper `4B6FE0` consumes this +D8 boundary at `4B7097/4B70C8`.

## Confirmed producer dependencies

`4B7500..4B7BC5` is a bounded complete function, not a byte-pattern hit.
It counts first XI/bench through `407060(4,0)/(5,0)` and reserve XI/bench
through `4070F0(0,0)/(1,0)`, and reads the native substitute quota through
`408500`. It clears excess source selections by `4181B0`, then reorders the
club's +244 word-ID array using adjacent swaps. The comparison reads the
actual player +248 role through `4EA3C0`; do not substitute surname, player
ID, skill or database order. `407C00` is validation, not this sort producer.

`4B785C` writes quota+11 to the output, then `4B79B3..4B79C3` conditionally
adds the bounded remainder computed at `4B7870..4B78A9`. This value is an
actual produced list boundary, not a universal literal 20. The exact ordered
normalization/sorting branch sequence still needs executable-to-port tests
before live membership integration; this note does not certify that mapping.

Native predicate identity is explicit and club-qualified:

| Entry | Actual source predicate |
| --- | --- |
| `417EA0` | club word +10 matches; reserve +174 bit 0 |
| `417EC0` | club word +10 matches; reserve +174 bit 1 |
| `417EE0` | club word +10 matches; first-team +14 bit 4 |
| `417F00` | club word +10 matches; first-team +14 bit 5 |

The directly preceding `4B7BD0` is also required. For a roster at least
quota+25 with no reserve selections, it reads club+1DC through the no-argument
getter `404A70`, then calls `40AB40(roster_count, reserve_formation, 3, 1)`
and `4067B0`; the earlier PUSH 1/PUSH 3 belong to that later call, NOT the
getter (which returns without popping arguments). For smaller rosters it clears reserve-selection flags through
`4181B0` and calls `4067B0`. These are source state producers, not merely
visual filtering. Their exact selection/ordering implementation must be
qualified before treating the current bridge's fresh state as native input.

## Minimum faithful implementation / remaining unknown

Use the original two list origins and row/empty-row owners, fed by the exact
source preparation, then `4B6FE0` slot mapping for each discriminator. Reuse
original row art/fonts and translate each nested owner's geometry. Do not
publish the database-first-20 projection as original membership. No guessed
zero boundary, fixed split, automatic modern selection or scrolling is added.

Next source action: adjudicate `404A70 -> 40AB40 -> 4067B0` in this precise
fresh-view call chain, then lock `4B7500` ordered mutations and `4B6FE0` holes
with source-qualified tests. The canonical post-#482 audit remains an open
implementation prerequisite; no new acceptance build is certified here.

Follow-on dependency read: `40AB40` is the original reserve XI/three-player
bench producer already described in MATCH_ENGINE.md, not a modern UI autofill
substitute. Its candidate mask (`40ABC9..40AC47`) explicitly excludes players
rejected by `418050(player, club, 0)` or already first XI/bench via
`417EE0/417F00`. The exact native caller/arguments above are now qualified.
Further complete-function adjudication (`40AB40..40AF57`) establishes that
this is NOT the competitive first-team selector's preferred-role two-pass
algorithm. `40B360` is the roster-size guard `N - quota - 11 >= 14`, not a
human/AI branch. Formation 22 is explicitly normalized to 0 through `404A90`.
For each of eleven formation slots, it scans unmasked roster entries in
original order, computes `41C7E0(target_role) * 41B970(Form)`, converts through
`668350`, coerces zero to one, and replaces the winner only on strict greater
score (`40ACF5..40ACFF`); ties retain the first eligible entry. There is no
preferred-position pre-pass. Failure to find a slot exits via `40AF37` before
any commit. With commit argument 1, it clears old selection for eligible
non-first-team members, installs all eleven reserve-XI flags and exact
formation role/auxiliary bytes, then marks the first three remaining eligible
roster entries as reserve substitutes (`40AEC7..40AF12`). This bench is not
ranked by skill or first-team category passes.

`418050(player, club, 0)` is still a real availability dependency: its
competition-null path checks the low three +14 bits, club ownership, and
`41B490 -> 41B4D0 -> 4E9BE0`. Do not replace that last predicate with an
always-available default. `41FA50` protects the explicit secondary-club case
in the commit clear loop; reserve-XI setter `4181E0` calls the actual role-byte
swap `418220`, while `418280` clears the other selections and role state.

Correction to the earlier dependency label: `4067B0..40694E` does NOT sort
the roster. It counts selection classes and, when the unassigned overflow
requires it, walks the roster backwards, excludes already selected or
secondary-club players, and applies bounded first/reserve-XI/bench setters.
Its four quota checks are sequential, not an invented mutually exclusive
partition; `406690/406720` can adjust roles using source occupancy helpers
`406A50/406C70` and `5F0D20`. The later adjacent-swap ordering is in `4B7500`.
Native selector, role-swap and overflow-repair state must therefore precede
slot mapping. These exact differences rule out substituting the existing
`select_ai_lineup_core(409C90)` or simply drawing players 20..29 on the right.
Follow-on adjudication closes the primitive occupancy counters:
`406BE0` counts club-qualified first-XI members of the requested current role,
excluding the supplied player pointer; `406DF0` does the same for reserve-XI.
The jump tables at `406B98/406DA8` qualify the directly called aggregation
branches, including the first-team role-8 contribution divided by three at
`406AE3` versus the reserve full contribution at `406D03`. These cannot be
collapsed into a single generic role counter. `5F0D20` walks 0x24-byte source
position records until sentinel 1000 and returns one plus the highest matching
record +8; it is not a guessed formation occupancy cap.

The availability tail is exact date behavior: `41B490` tests bit 11,
`41B4D0` looks up/ensures the original Non-EU record by player ID, and
`4E9BE0` returns `native_current_date <= record+14`. The existing bridge uses
the source-qualified contract-expiry projection for this state; its producer
is separately recorded in the prior Non-EU lifecycle research. An absent
required record/date must not become an always-eligible selection default.

Both original row factories now have explicit caller proof: `4B7170` and
`4B7240` pass club, row index, first/reserve discriminator, and the player
list's virtual +C0 count to `4B6FE0`. The +C0 slot at `7C5BB4` is `48B6E0`:
with list filter +4C=0 it returns the actual club roster count; nonzero filters
take their own source role/category scan. A -1 mapping creates the exact
PPlayerEmptyRow/PSCFEmptyRow owners, not a missing player or scrollbar.
The successful mapping is then resolved through club `406F00` / player-list
virtual +B4. The fourth mapper argument must not be substituted with 20.

After the normalization counts, `4B7500` initially produces D8=11+quota;
its additional first-list allocation is a positive bounded unassigned remainder,
not a fixed ten-player split. Its three adjacent-swap phases separately
handle first selections, unassigned additions, and the remaining reserve
selections. Preserve their exact signed role comparisons, equality stability,
starting offsets, excess-selection clears and hole rules rather than replacing
them with a single modern key sort. Remaining work is to lock the complete
ordered branch translation and source state binding with tests, then perform
the actual paired-list correction after the retrospective audit prerequisite.

## Reproduction

Run the repository's existing hash-gated `gate13_squad_source_trace.py` with
the canonical private executable, `--disassemble`, and `--output` outside Git.
Its added bounded anchors cover constructor, preparation, reserve normalization,
mapper and refresh. Linear output is an aid, not automatic CFG/type proof.
Private manually reviewed instruction-aligned receipt:
`work/squad-context-aligned-functions.txt`; dependent getters are in
`work/squad-context-adjudication.txt`; complete reserve producer/overflow
functions are in `work/squad-reserve-normalization-dependencies.txt`, with
aligned guards/setters in `work/squad-reserve-producer-guards.txt`. No raw
disassembly or proprietary game save enters the repository. Further aligned
receipts: `work/squad-paired-availability-role-occupancy.txt`,
`work/squad-paired-counts-and-mapper.txt`,
`work/squad-row-factories-and-registration.txt`, and
`work/squad-mapper-count-and-registration-init.txt`. The exploratory window
`work/squad-slot-mapper-callers.txt` begins unaligned and is NOT CFG proof.
