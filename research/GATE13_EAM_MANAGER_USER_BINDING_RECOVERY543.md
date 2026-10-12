# Recovery543: original selected-user MANAGERNAME source pointer ownership

## Source and test boundary

Investigated only the owner's private original `footballmanager.exe`, SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`,
4,714,541 bytes. Re-materialized the already uploaded private Drive original
from source folder 03, independently recalculated SHA-256, and statically
examined x86 through `objdump -D -Mintel`. The original was **not executed**.
A separate local audit verified 13 native instruction addresses in the
SHA-authenticated original file. No proprietary source bytes were committed.

## Proven original new/selected-user manager chain

1. Native first-screen/new-user handler `0x4D8E90`, in its supported
   `0x4D8EB5` branch, reads the manager **object pointer** from
   `[[first_screen+0x3C]+0x4C]` at `0x4D8EBE..0x4D8EC4`.
   It runs `0x4D9800` using that manager pointer at `0x4D8ECB`,
   then reads manager `+0x40` (an index) and writes it to its
   selected registration entry at `0x4D8ED0..0x4D8ED9`.
   This distinguishes the selected **manager object pointer** from its index.
2. The same native handler registers that selected manager pointer in
   `0x874C10::0x413BB0` at `0x4D8EEC..0x4D8EF8`.
   `0x413BB0` adds the user to the `+0x9CC` linked list and passes
   its original manager pointer to `DBRUser::0x4258D0`
   (`0x413C4F..0x413C54`). The latter stores that pointer verbatim at
   `DBRUser+0x5B4` (`0x4258F2`). It is **not** a club alias and
   **not** a numeric manager index stored in the user field.
3. Current user selection `0x4139D0` obtains selected user position from
   `registry+0x9C4`, calls linked-list positional accessor
   `0x413B10` on `registry+0x9CC`. This returns the **user pointer**.
   Original initial Inbox `0x56FE01` invokes that current-user accessor,
   reads `user+0x5B4` (`0x56FE0C`) and passes that exact manager
   pointer to typed `MANAGERNAME` context constructor `0x612FD0`
   (`0x56FE20..0x56FE2D`).
4. `0x612FD0` reads the pointed-to manager object's DWORD `+0x40`,
   retaining its low 16 bits as the typed manager index
   (`0x612FEA..0x612FF1`). Native name handler `0x613040` uses
   manager table base `0x875628` and `index * 0x40`
   (`0x613043..0x613052`). Native `0x414F30` and `0x414FA0`
   obtain the name fragments, and `0x613067` uses original
   literal `%s %s` (VA `0x81858C`) via `0x66876F`.
   The actual name is thus tied to the registered manager record,
   not a selected club caption or an arbitrary AI manager entry.
5. The original `DBRUser+0xD0` is a **different, blank-initialized**
   club-alias string (`0x424F3F`). Its empty value is not evidence
   that `MANAGERNAME` is empty.

## Reconstruction discrepancy and non-acceptance

Current `GameState.bind_original_user_mail_recipient` assigns
`native_user_recipient_key` by scanning modern `state.managers`
for an initial `!` name (or reusing the club's imported manager index
under a fallback); the native source instead preserves an explicitly selected
manager object pointer and derives the typed name from its `+0x40` index.
A mailbox recipient index alone does **not** certify the manager-name field
or provenance of the source first-screen selection. The modern presentation
bridge has no verified selected-native-manager-object identity/name state;
therefore **do not** map `native_user_recipient_key`, imported club
`manager_id`, `native_user_club_caption`, or a guessed name to
`{MANAGERNAME:1}`. Existing Inbox selected-body rendering remains
unimplemented/fail-closed. This discrepancy is SOURCE-VERIFIED, but a
complete port-side identity remedy is NOT VERIFIED.

## Reproduction and next action

Use the same SHA-verified original file (private), without launching it:

```bash
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x4d8e90 --stop-address=0x4d8f0b footballmanager.exe
objdump -D -Mintel --start-address=0x413bb0 --stop-address=0x413c87 footballmanager.exe
objdump -D -Mintel --start-address=0x4258d0 --stop-address=0x425901 footballmanager.exe
objdump -D -Mintel --start-address=0x4139d0 --stop-address=0x413b36 footballmanager.exe
objdump -D -Mintel --start-address=0x56fdfe --stop-address=0x56fe4e footballmanager.exe
objdump -D -Mintel --start-address=0x612fd0 --stop-address=0x613079 footballmanager.exe
```

**P0 next:** investigate how `0x4D9800` and the first-screen
`[first_screen+0x3C]+0x4C` original manager record is created/selected
and named, whether the modern clean-user creation records that same identity,
then implement explicit per-selected-human original manager binding and
negative-case tests before showing actual MANAGERNAME. In parallel,
resolve native shared CRT seed from startup->calendar->Inbox first click.
PR638 stays DRAFT/BLOCKED. Continue selected Inbox native text palette,
PEAMMessage, and R1 full match journey after source qualification.
Gate13–17 and genuine Windows 11 GUI acceptance remain OPEN.
