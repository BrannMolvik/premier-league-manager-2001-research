# Gate 11 Human Youth Workflow

Verified against canonical FM2001 `FOOTBAL.EXE` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

This note continues the already-recovered startup youth RNG work and closes the
runtime ownership boundary required before integrating the fresh human-youth
workflow.

## Fresh generation caller

New-game setup reaches:

```text
0x413830
  -> 0x414330 generated-name startup block
  -> 0x413980 per-user youth pass
       -> 0x61E0E0 clear user youth list
       -> 0x61DF90 generate youth records
       -> 0x61DD30 post-generation age/contract adjustment
```

The exact candidate pool, option-driven target count, swap-delete candidate
selection and interleaved candidate/name/name RNG ordering were already
recovered in `startup_rng.py`. The structural findings below are new.

## User youth list is a separate fixed 20-record container

The object used by `0x61DF90` stores inline records beginning at object
offset 0. The active count is at `+0x1800`.

`0x61DF90` checks that count against literal `0x14`, so the list has a hard
cap of **20** records.

Each record is exactly **0x18 bytes**. Record `i` is addressed as
`youth_list + i * 24`.

This is a separate user-owned youth container. It is not the club first-team
roster at `DBRClub+0x244`.

## Youth record layout

Constructor/reset helpers `0x61E480`, `0x61E540` and the list mutators
establish the following fields:

| Offset | Size | Proven behavior |
|---|---:|---|
| `+0x00` | 2 | DBRPlayer ID; `0xFFFF` is the empty sentinel |
| `+0x04` | 4 | pointer to an allocated **0xA4-byte** per-youth subobject initialized through `0x4EAB80` |
| `+0x08` | 4 | initialized to 1 |
| `+0x0C` | 4 | initialized to 1 |
| `+0x10` | 4 | initialized to 1 |
| `+0x14` | 1 | initialized to 0; separately set/read by list helpers |

The business meanings of the `+0x04` subobject and `+0x08/+0x0C/+0x10/+0x14`
fields are not yet all source-named. They should remain neutral in the
clean-room data model until a direct UI/event binding proves labels.

`0x61E520` frees the `+0x04` allocation.

## List operations

`0x61E0E0` clears the list by repeatedly removing the last record.

`0x61E100(index)` removes one record and compacts all later records forward
with `0x61E690`, decrements the count, then resets the final slot to the
`0xFFFF` sentinel.

`0x61E170(player_id)` scans `+0x00` IDs, removes the first match and returns
success/failure.

`0x61E1B0(player_id)` scans for the player and sets record byte `+0x14 = 1`.

`0x61E1F0(player_id)` returns record byte `+0x14` for the matching record,
or false when not found.

DBRUser wrappers `0x42A920` and `0x42A940` expose the latter set/get pair
through the user-owned youth object at `user+0x6BC`.

## Record initialization and candidate transformation

For a selected candidate, `0x61DF90` creates the next record through
`0x61E540(record, player_id, 0, 0x18)`.

For a non-sentinel player, `0x61E540`:

1. resets the record's `+0x04` subobject through `0x61E7A0 -> 0x4EAB80`;
2. resolves the DBRPlayer;
3. calls `0x4185B0(player, 0, 1)`;
4. reads the player's current contract-duration state and adjusts it through
   `0x419190` so this initializer targets **24 months**;
5. writes the record player ID and clears record `+0x14`.

The selected player is then passed to `0x41E510(player, country_id, userClub)`.

`0x41E510`:

- rewrites DOB so the player becomes age **15** while preserving the calendar
  date components;
- clears shirt number `player+0x70`;
- calls `0x41A9C0`;
- writes the passed country ID low byte to `player+0x12`;
- calls `0x421C00` to replace `player+0x08` first name and
  `player+0x0C` surname using the already-recovered two name-source RNG draws;
- calls `0x4185B0(player, userClub, 1)`;
- finally writes the user club's runtime ID word to player registered-club field
  `+0x10`.

### Important roster-ownership result

Direct `0x4185B0` disassembly confirms it is a player-state reset. It clears
and initializes player status/stat fields, but it does **not** add/remove a
DBRClub roster entry and does not rewrite `player+0x10/+0x72`.

Therefore `0x41E510`'s final `+0x10` write must not be interpreted as a
first-team roster insertion. Youth-list membership and club-roster membership
are separate states.

## Immediate post-generation adjustment 0x61DD30

After `0x61DF90`, `0x413980` immediately calls `0x61DD30(user)`.

The routine walks the user's youth records and, for each youth player:

- calls `0x61E630(record, -12)`, adjusting the underlying player's contract
  expiry by minus 12 calendar months;
- rewrites DOB so the player becomes age **17**;
- calls `0x4185B0(player, userClub, 1)` again.

Thus the fresh startup pipeline deliberately passes through an age-15 / 24-month
intermediate state before the immediately-following age-17 / reduced-contract
state. A clean-room fresh-game materializer may compose these only if it
preserves the same final state and exact RNG ordering; the intermediate itself
does not consume extra shared CRT RNG.

## Promotion/move bridge is distinct from generation

`0x61E3D0` is the later youth-to-club move path. It is reached by named youth
event/action code including the `EAMyouthpromoteplayer` family.

Its instruction order is:

1. resolve the youth record for the player and retain the record's `+0x04`
   subobject;
2. remove the player from the youth list through `0x61E170`;
3. resolve the player's current club and call `0x4051F0(player_id)`, the
   existing club-roster removal path;
4. write player byte `+0x76 = 0x29`;
5. resolve the target club and call `0x405360(targetClub, player)`, which
   enters the club-roster addition path;
6. call player helper `0x417700` with the saved youth subobject and remaining
   action arguments to apply the promoted player's club/contract state.

This proves that **promotion**, not fresh youth generation, is the point where
the player becomes a normal club-roster member.

## Youth release/detachment

The explicit player release helper `0x4177C0(player, club_id)` first resolves
that club/user's youth list and calls `0x61E170(player_id)`.

Only when youth-list removal succeeds does the path continue through normal
club-roster removal and the explicit free-player transition: player status is
reset, Out-of-contract bit 7 is set, and club IDs are detached to `-1`.

This provides the source-backed remove/release behavior for a youth-list member.
Do not model youth release as merely deleting a list record.

## Clean-room implementation boundary

The next implementation slice can now safely:

1. add a separate per-user `YouthTeamState` with hard cap 20 and neutral
   24-byte-record fields needed by active behavior;
2. extend the existing startup RNG helper so it returns the actual generated
   first name and surname sources, not only consumed bounds;
3. transform selected global RuntimePlayers into the fresh youth final state
   while adding youth records but **not** inserting them into the first-team
   roster;
4. expose promote and release operations that perform the source-backed list
   removal plus club-roster transition;
5. persist youth-list membership and neutral record state in the internal save.

The `+0x04` 0xA4-byte subobject can remain neutral unless the promote helper
`0x417700` requires specific fields for behavior visible in the currently
active Gate-11 slice. Do not invent labels for it.


## Follow-up boundary: 0x61DE40 two-cohort initializer

After the first implementation was verified, direct xref tracing found a
distinct call `0x425680 -> 0x61DE40(user+0x6BC, user)`.

`0x61DE40` is materially different from the already implemented single
`0x61DF90 -> 0x61DD30` slice:

1. it clears every existing youth record;
2. obtains the active user club country;
3. calls `0x61DF90` once;
4. calls `0x61DD30` over that first cohort;
5. calls `0x61DF90` a second time;
6. computes a calendar date and writes it to every youth player's
   `DBRPlayer+0x154`;
7. resets every record's `+0x04` training state through `0x61E7A0`.

Therefore the final list can contain two generated cohorts and its contract-date
handling supersedes the simple single-cohort final-date model when this caller
is active.

The only direct `0x61DE40` xref found so far is inside `0x425680`.
`0x425680` is reached from the `0x4A8070` family, but that surrounding
routine also performs broad user/staff initialization. Do **not** classify
`0x61DE40` as daily, monthly, annual or one-shot until the lifetime/caller
chain is instruction-closed. This is the next active youth trace.


## Club-activation initializer resolved — 29 September 2026

The follow-up `0x425680 -> 0x61DE40` dependency is now instruction-bounded.

### Cadence

This is not an annual youth refresh. The unique direct caller chain reaches `0x425680` from the normal calendar-advance wrapper, but `0x4A8070` gates the call on `DBRUser +0x10E0 != -1`. `+0x10E0` is a pending runtime club index (DBRClub stride `0x2A8`); `0x425680` clears it back to `-1` before returning. A separate user-selection callback `0x60DBD0` is the identified re-arm writer.

The youth reset therefore runs once when a pending controlled-club selection/switch is activated.

### Two-cohort final state

`0x61DE40`:

- clears the separate youth list without reverting the DBRPlayers previously selected into it;
- generates one `0x61DF90` cohort;
- post-processes that cohort through `0x61DD30` to age 17;
- generates a second `0x61DF90` cohort, which remains at the age-15 state produced by `0x41E510`;
- assigns every final youth player's `+0x154` to the next 30 June;
- resets every youth training subobject.

On the ordinary fresh path category-3 facilities are absent, so both target counts are exactly four with no size RNG draw. Final activation state is therefore **eight youth players: four age 17 followed by four age 15**.

The clear operation preserves the original quirk that old selected DBRPlayers retain status bit 3. Consequently the first new cohort rescans past the earlier startup cohort, and the second new cohort rescans past both the earlier startup cohort and the first activation cohort before applying the 512-candidate cap.

### RNG consequence

Each four-player cohort consumes 12 draws (candidate + first-name + surname for each player), so `0x61DE40` adds 24 mandatory draws before `0x5E3FD0`. From the canonical fresh post-loan state this moves the shared CRT from `0xA54D70C6` to `0xFA1C595E` before support-staff selection. The corrected post-fixed-staff state is `0xA2FEE1E1`; Youth Team Coach rating remains 2.
