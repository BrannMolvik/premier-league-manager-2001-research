# Recovery518 continuation — bind the actual selected human to original EAMail delivered owner

**Gate13 remains OPEN**. This is a follow-up to merged PR593's source-typed
per-manager delivered mailbox persistence. It does **not** generate welcome
messages, invoke original due-event dispatch or render PEAMail.

## Direct source owner and existing runtime boundary

Hash-verified earlier native receipts:
- `research/GATE13_INBOX_OWNERSHIP_2026-10-10.md` establishes original
  `TeamSelect::0x4D8EF8→0x413BB0` new DBRUser registration,
  `DBRUser+0x6B4` new empty mailbox list header at `0x424E2E`, and fresh
  `0x426090→0x4151C0` active manager key selection based on a first-name
  prefix `!` and unoccupied imported manager. Original fresh Southport human
  may be runtime recipient key **0**, even though imported AI manager key
  is **195** and club row index is **349**. This is independently tested
  for native source conditions.
- `research/GATE13_EAMAIL_DELIVERY_LIST_VS_IMMEDIATE_MODAL_AUDIT_RECOVERY451.md`
  proves current `PEAMail::0x472680` reads the selected manager/user's
  own `+0x6B4` append-ordered delivered-mail list, **not** the
  pending MPM queue or a shared club/global mailbox.
- `research/GATE13_INBOX_RUNTIME_MANAGER_KEY_VS_DELIVERY_OWNER_AUDIT_RECOVERY473.md`
  documents that the modern port rightly stores a sidecar
  `GameState.native_user_recipient_key` equivalent to original live
  `DBRClub+0x40`, leaving imported source AI club manager metadata intact.
  The original source distinction is an actual delivery hazard if
  future code looks up `club.manager_id` instead.

## Minimum source-preserving integration

Current `HumanGameplayController.select_club` is the one supported normal
TeamSelect new-human path; it already invokes source manager key binding at
that explicit boundary. Once the native effective recipient is known,
initialize **only that user**'s currently empty, persistent
`OriginalDeliveredEAMailboxes` header if not already registered. Do not
delete an existing mailbox on club re-selection, do not create a fabricated
recipient when synthetic source lacks the `!` manager key, and do not
register all imported AI managers as humans.

Expose a strict **read-only, unsorted** method
`ManagementSourceDataBridge.source_delivered_mailbox_for_selected_user`
that obtains the current selected human club, then the effective runtime
`native_user_recipient_key`, and finally only the matching registered
mailbox. This is the original `user+0x6B4` list owner, **not** the original
`PEAMail+0x68` filtered/sorted display array, nor the visual eight-row
CMessageList with original bitmaps/font or true pointer hit regions.

The backing `GameState` and modern internal-save owner already exist from
PR593. These tests preserve per-user node insertion order, captured source
recipient/sender, no early exposure of a future pending transfer, both
distinct manager keys and modern save/reload across a real
`HumanGameplayController` fresh selection. The only special test
manager `!Spare` name is based on the first authorized original reserve
source name, not an invented mail body. Unsupported synthetic manager
tables leave the recipient UNKNOWN and cannot show a fake empty/live Inbox.

This integration uses prior verified original executable findings;
`container.exec` still fails `caas.internal.errors.ClientError`, so no
new PE was disassembled or original Windows game played. No original game
files/disassembly are added to Git.

## Remaining hard acceptance

Real NEXT/PResults source `0x613EE0` and class readiness `+0x3C`;
registered 2–6-human careers and all-manager mailbox maintenance;
original five PEAMail filtering/sort actions, 532×18 rows, 545×160 list,
source graphics and language-based string materialization, first vs second
neutral row activation, true player/team links and detail modal actions;
direct PBg ID1 and PMenu child0x65 stack paths, Windows 11 real input, full
all-original-league/country career and Gate13–17 physical release audit.

**SOURCE-VERIFIED**: new native DBRUser header, recipient manager identity,
manager-specific delivery owner. **INTEGRATION-VERIFIED** only after full
source-free reconstruction/management tests on this PR head.
**VISIBLE-ACCEPTED: NO**.
