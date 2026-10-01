# Gate 13 TeamSelect user-selection trace

Recovery 143 re-ran the bounded TeamSelect selection trace directly against the
canonical original `footballmanager.exe`:

- SHA-256: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`;
- source: the authorized 511,121,336-byte source archive, re-materialized outside
  Git and verified before extraction;
- both disc copies of `footballmanager.exe` matched that canonical hash.

No original executable bytes or disassembly dump are stored in Git.

## Corrected selection-record interpretation

The earlier interrupted trace incorrectly treated the first dword of the
TeamSelect private selection record as a club identity. Recovery 143 disproves
that interpretation.

### Record address and initialization

`0x4D9240` maps the clicked 0x40-byte club control plus the current TeamSelect
page/window state to a private record with a 0x30-byte stride.

The TeamSelect constructor initializes a 9 by 24 record region at
`0x4D96C5..0x4D96DE`. The first dword of every record is written as `-1`.
That sentinel is therefore inactive rollback state, not an at-rest club ID.

### Club selection, 0x4D8E90

On the select path:

1. `0x4D8EA0 -> 0x4D9240` resolves the private record.
2. `0x4D8ED0..0x4D8ED9` follows the clicked control to its club and copies
   `DBRClub+0x40` into record `+0x00`.
3. Existing executable research independently identifies `DBRClub+0x40` as
   the club's manager ID/reference, including the Arsenal/Wenger source example
   and `0x403E10` manager-table validation.
4. `0x4D8EDB..0x4D8EE9` saves the displaced manager's `+0x24` state in
   record `+0x04`.
5. `0x4D8EEC..0x4D8EF8` passes the clicked club pointer directly to
   `0x413BB0`.
6. `0x413BB0` rejects a duplicate club, creates a new 0x10F0-byte user,
   calls `0x4258D0(user, clicked_club, 0)`, appends it to the global user
   list, and increments the user count.
7. `0x4258F2` stores that clicked club pointer at user `+0x5B4`.
8. `0x4D8EFD..0x4D8F07` stores the created current-user pointer in private
   record `+0x08`.

The club identity therefore comes from the clicked TeamSelect row/control and is
bound to the user immediately. It is not encoded by the private record's first
dword.

### Deselection proves rollback semantics

The deselect branch at `0x4D9042..`:

- resolves record `+0x08` back to the selected user and removes that user via
  `0x413B80 -> 0x413DB0`;
- restores the displaced manager `+0x24` state from record `+0x04`;
- restores the club's `+0x40` manager reference from record `+0x00`;
- writes `-1` back to record `+0x00` at `0x4D9166`.

This is a rollback record for the original manager/user mutation.

## Multiple human users are source-proven

Selection does not replace the previous selected club. `0x413BB0` appends a
new user unless that club is already represented.

`0x4DA4D0` returns the TeamSelect saturation condition. It becomes true when
either:

- TeamSelect `+0x6C <= 0`, where the constructor derives the available count
  from manager records accepted by `0x4151C0`; or
- global user count `0x8755E4 >= 6`.

The original thus supports multiple simultaneously selected human clubs, with a
hard global upper bound of six and a potentially tighter source-manager
availability bound.

## Start does not resolve a row payload into a club

TeamSelect event `0x2A` at `0x4DA480` calls `0x4C41C0` with page/context
arguments. It does not read the private 0x30-byte selection record.

`0x4C41C0` instead operates on the already-created global user list. Recovered
calls repeatedly resolve users through `0x4139D0/0x413B10`; the current
user's club is read from user `+0x5B4` during continuation.

There is therefore no missing "selection-record ID -> gameplay club ID"
translation after Start.

## Reconstruction consequence

The clean-room TeamSelect presentation now keys active rows by the canonical
club ID carried by each populated row and preserves ordered multi-club selection
across hierarchy navigation. It enforces the source-proven six-user hard cap.

The current `HumanGameplayController` still models one `HumanManagerState`.
The front-end seam therefore records multiple original-style selections but
fails closed on Start when more than one is active. A single selected club still
hands off to the existing backend at Start. This is an explicit backend
capability boundary, not a claim that the original was single-player-only.

The remaining Gate 13 validation item after this correction is the upgraded real
Windows/Tk audit of the corrected TeamSelect interaction, plus any broader
presentation/resource criteria still marked open by the Gate 13 audit.
