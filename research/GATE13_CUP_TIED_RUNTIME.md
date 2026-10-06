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
