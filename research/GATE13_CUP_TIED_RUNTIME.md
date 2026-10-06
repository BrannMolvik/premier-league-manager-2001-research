# Gate 13 Cup-Tied runtime recovery

## Status

**Confirmed from the hash-verified original executable.**

Canonical executable SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

This note closes the producer/lookup semantics needed to model PSCFRow frame 3
without treating Cup-Tied as a DBRPlayer status bit.

## Record and collection layout

`0x4E95D0` constructs an 8-byte `CCupTiedPlayer`-like record:

- +0x00: vtable
- +0x04: signed 16-bit player ID
- +0x06: signed 16-bit club/team ID

The two serializer helpers at `0x4E9630` and `0x4E9660` read/write those two
16-bit fields independently.

The owning competition object exposes the collection through object +0x48.

- `0x4F8E20(context, player_id, club_id)` adds +0x48 and calls `0x4E9690`.
- `0x4F8E40(context, player_id, club_id)` adds +0x48 and calls `0x4E9710`.

### Insertion: first club wins

`0x4E9690` first calls `0x4E96E0`, which walks the collection and compares
record +0x04 against the requested player ID.

If that player already exists, insertion returns without changing the stored
club. Otherwise it allocates one record with the supplied player ID and club ID
and inserts it into the collection.

Therefore the clean-room equivalent is **idempotent by player ID**. The first
club recorded for that competition-root context remains authoritative.

### Lookup: tied only after changing club

`0x4E9710` walks the same collection by player ID. If no record exists it
returns false. When a record exists it compares record +0x06 with the supplied
club/team ID and returns true only when they differ.

In clean-room terms:

`cup_tied(player, current_club) = recorded_player && recorded_club != current_club`

A player remains eligible for the club with which the first qualifying
appearance was recorded.

## Competition-root ownership

`0x4F3DC0` walks object +0x04 parent pointers until it reaches the root
competition object.

`0x511170`:

1. resolves the current match competition through `0x4F3DC0`;
2. invokes root virtual +0x18;
3. returns that root only when the predicate is true, otherwise returns null.

The already recovered competition-class invariant identifies the same virtual
+0x18 predicate:

- League / ScotPremierLeague: false
- Cup / DummyLeague: true

So Cup-Tied state belongs to the **root competition context**, not blindly to
the immediate child competition. A League child beneath a Cup root can
therefore share the root Cup-Tied collection, matching the original parent walk.

Clean runtime class codes already recovered elsewhere are:

- 1 = League
- 2 = Cup
- 3 = DummyLeague

Do not attach Cup-Tied state to ordinary root League competition 0.

## Exact producer path

`0x41B7E0` is the appeared-player post-match update. Its third argument is a
competition/context pointer.

When that pointer is non-null it pushes:

1. DBRPlayer +0x04 player ID;
2. DBRPlayer +0x10 current club/team ID;

and calls `0x4F8E20`.

The sole direct caller is `0x404E05` inside `0x404CE0`.

`0x404CE0` walks the club roster after a completed match. For each current
club player that passes `0x41B7D0`, it inspects that player's per-match
0x4C-stride record. The byte tested immediately before `0x41B7E0` is the
same appeared/not-appeared split already reconstructed by
`persist_premier_league_morale_and_form`: starters count as appeared and a
substitute counts once a type-10 substitution record names them as incoming.
Non-appeared players take `0x41BA00` instead and do not call the Cup-Tied
producer.

The only calls to `0x404CE0` in this match-finalization path are the two team
passes at `0x5115A4` and `0x5115C3`. Each receives the optional context
returned by `0x511170`.

Therefore the exact mutation boundary is:

- after a match has completed;
- once for each player who actually appeared;
- only when the match's root competition virtual +0x18 predicate is true;
- store the player's current club on first qualifying appearance only.

Transfers do **not** create or rewrite Cup-Tied records. A later club change is
what makes the existing root-context record evaluate as tied.

## Clean-room integration seam

The existing `GameState._persist_domestic_cup_shared_post_match` helper is the
closest clean-room counterpart of `0x404CE0`: it already receives both clubs,
both prepared match sides, the runtime participant arrays, and the final
`NormalMatchResult`.

The source-safe implementation should therefore:

1. resolve the immediate competition ID to its root through
   `parent_competition_id`;
2. require root runtime kind 2 or 3;
3. use `appeared_player_indices(side, result)` for each side;
4. insert each appeared runtime player's ID/current club into a collection keyed
   by root competition ID;
5. preserve the first record for an existing player;
6. expose lookup using the same root key and current club comparison.

This seam also covers procedural League children under Cup roots when their
shared post-match path passes the child's competition ID.

## PSCFRow consequence

The earlier `0x418480 -> 0x4F8E40 -> 0x4E9710` lookup is now semantically
closed. Frame 3 is the original **Cup Tied** status.

Rendering must still preserve `0x418360` priority. The special alternate
On-loan and Non-EU branches precede the Cup-Tied branch, so frame 3 may only be
published where those higher-priority predicates are known false or after those
predicates themselves are materialized exactly.


## Recovery 340: PSCF current-date resolver boundary

Further canonical-executable analysis closes the outer `0x418480` context around
the collection lookup.

### Current match context

`0x418480` does not query an arbitrary competition. It first resolves the
player's **current** club through `0x417270` (DBRPlayer +0x10), then calls
`0x407F20`.

`0x407F20` passes:

- the global current date at `0x9847FC`;
- the current club;
- mode `1`;

to `0x615D10`, after selecting the schedule container through `0x4079D0`.
`0x4079D0 -> 0x403640` uses DBRClub +0x74: values 2 or 3 select the
secondary container at `0x947AF0`; every other value selects the primary
container at `0x947AD8`.

If no match for that club exists on the global current date, `0x418480`
returns false before any Cup-Tied collection lookup.

When a match exists, the match competition is resolved to its root through
`0x4F3DC0`. The root virtual +0x18 must be true before the Cup restriction
path is entered.

### Cup runtime +0x34 source mode

Cup construction `0x4F51E0` derives runtime +0x34 directly from packed
DBRCompetition source byte +0x24:

- source `0x7B` -> runtime mode 1;
- source `0x74` -> runtime mode 2;
- every other source value -> runtime mode 0.

The clean parser now retains this source byte neutrally as
`CompetitionDefinition.packed_rule_code_24` and exposes the exact
`cup_restriction_mode` projection.

For modes other than 1, `0x418480` returns the ordinary
`0x4F8E40 -> 0x4E9710` collection predicate directly.

For mode 1, a **true collection predicate also returns true immediately**.
Only a collection miss continues into the additional date/cutoff branch.
Therefore a source-qualified positive collection hit is sufficient evidence for
PSCF Cup-Tied frame 3 even before that negative branch is fully materialized.

### The mode-1 date is CPlayerTransferHistory state

The player field used by `0x419350` is not the already recovered
DBRPlayer +0x158 current-club join date itself. DBRPlayer +0x198 is an embedded
0x24-byte MSVC RTTI object whose vtable `0x7C8A5C` identifies the class as
`CPlayerTransferHistory`.

Within that object:

- +0x08 is initialized to -1 by `0x4EBE60`;
- +0x18 is initialized to the current date;
- `0x4EBF60` writes the complete transfer-history payload;
- `0x4EBF90` updates +0x18;
- `0x419350` returns no date while +0x08 <= -1, otherwise returns +0x18
  through `0x4EBE80`.

Startup `0x4172E0` normalizes DBRPlayer +0x158 and copies that date into
transfer-history +0x18, but transfer-history +0x08 remains a separate
availability/source field. Consequently the clean runtime must not substitute
`current_club_join_date` for `0x419350` unless +0x08 is also recovered.

When `0x419350` yields a date, the remaining mode-1 branch selects one of two
global cutoff dates using `0x8755E8` and compares the transfer-history date
against `0x8755EC` or `0x8755F0`. Those globals remain to be source-closed.

### Higher override safety for frame 3

`0x418360` priority remains:

1. alternate On-loan frame 13;
2. special Non-EU frame 12;
3. Cup-Tied frame 3;
4. later bit-based/fallback statuses.

The alternate On-loan branch is exactly representable by existing clean state:
DBRPlayer bit 6 is the loan state, +0x10 is the temporary/current club and
+0x72 is the registered/parent club. In clean terms it is
`loan_club_id is not None and loan_club_id != club_id`.

The special Non-EU branch is gated first by DBRPlayer bit 11. Startup
`0x421CE0` sets that bit only after the already reconstructed exact
`0x421760` Non-EU predicate succeeds. Therefore `RuntimePlayer.non_eu ==
False` is a source-safe proof that this higher override cannot fire. A true
`non_eu` value is not yet enough to reproduce the separate registration-record
expiry lifecycle in every case, so lower-priority status rendering must remain
unresolved for those players unless that lifecycle is modeled.

Safe partial frame-3 publication is therefore possible only when:

- direct frames 0/1/2 did not return;
- alternate On-loan frame 13 is false;
- `non_eu` is false;
- the current-match competition context is source-qualified; and
- the root Cup-Tied collection predicate is positively true.

A collection miss in mode 1 remains unresolved, not false, until
`CPlayerTransferHistory +0x08` and the global cutoff selector/dates are
materialized.


## Recovery 357: DBRGame cutoff lifecycle and corrected transfer-history date

The previously unresolved mode-1 negative branch is now source-closed from the
hash-verified executable.

The three absolute addresses are fields of the global `DBRGame` instance at
`0x874C10`, proven by MSVC RTTI (`.?AVDBRGame@@`):

- selector `0x8755E8 = +0x9D8`;
- cutoff 1 `0x8755EC = +0x9DC`;
- cutoff 2 `0x8755F0 = +0x9E0`.

`0x413A20` resets the selector to 0 and derives the two cutoff **dates** as
`current_date + 60` and `current_date + 207` days. The date helper
`0x64D500` computes `base + 7*weeks + days`; the results are immediately
formatted through `%D %Mf %Yf`.

The daily `0x4138E0` path decomposes the current date through
`0x64CCD0` and moves the selector to mode 1 on August 30 and mode 2 on
January 30.

This also corrects Recovery 354. `CPlayerTransferHistory+0x18` is the
transfer-history **date**, not the appearance count. At transfer commit
`0x422E3E..0x422E82`, DBRPlayer `+0x18C` is passed as setter argument 4
and lands at history `+0x1C`; global current date is setter argument 5 and
lands at history `+0x18`. Constructor `0x4EBE60` and formatter
`0x4EBFA0` independently confirm `+0x18` as a date.

For the mode-1 Cup runtime branch, after a normal Cup-Tied collection miss:

1. `0x419350` requires history `+0x08 > -1` and returns history
   `+0x18`; otherwise the extra branch is false;
2. selector 1 chooses `DBRGame+0x9DC`;
3. selector 2 chooses `DBRGame+0x9E0`;
4. selector 0/other values do not activate the branch;
5. the player is Cup-Tied on this fallback exactly when
   `transfer_history_date > selected_cutoff_date`.

Positive root-competition collection hits remain unchanged and still win
immediately. The clean-room integration must now propagate the actual
transfer-history availability/date state and DBRGame cutoff lifecycle rather
than guessing from `current_club_join_date` or appearance totals.
