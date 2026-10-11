# Recovery527: original EAMPlayerAskTransferListsub native readiness and retention

11 October 2026 KST. **New directly inspected original executable bytes via the private Drive connector; no executable process launched.** Gate 13 and Gates 14–17 remain OPEN.

## Exact source identity and reproducibility

- Original executable: separately uploaded private Google Drive file `1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q`, `footballmanager.exe`, 4,714,541 bytes.
- Previous independent direct-download SHA-256 verification recorded in `research/ORIGINAL_SOURCE_LOCATOR.md`: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. This specific Recovery527 read decoded original bytes and mapped the PE sections; **it did not repeat the entire-file hash**.
- Original PE32: DOS MZ header, image base `0x400000`; for `.text` and `.rdata` under the source image, the RVA of the recovered sites maps directly to the file byte offset.
- Found the unique MSVC RTTI type descriptor containing `.?AVEAMPlayerAskTransferListsub@@`: descriptor VA **`0x818F40`**, COL **`0x7DF7C8`**, final vftable VA **`0x7BDB1C`**. Vtable[-4] directly references that COL; COL+0x0C directly references that descriptor. This establishes the class rather than guessing from adjacent unrelated EAM subclasses.

## Source-proven class-specific virtual methods

1. **vftable+0x3C → original `0x4093E0`**. Actual instructions: `mov eax,1; ret`. This class's readiness virtual is **unconditionally true**. The existing original `MPMEAMail::0x5CFA20` retrieves its record at envelope+0x08, invokes the record's virtual+0x3C and proceeds with stamping/manager routing only on a nonzero return. Thus for a source-qualified EAMPlayerAskTransferListsub record this *one predicate* no longer needs to be unknown; **due-event qualification is separate**.
2. **vftable+0x40 → original `0x470CE0`**. Actual instructions load message field+0x04, add `0x16D = 365`, compare the global original date `0x9847FC` to the result and return `setle`. The original-style retention check is `source_current_day <= source_record_day + 365` in the game's native date units, **not calendar timedelta conversion**. The existing source code already modeled precisely this virtual for another EAM subclass; this verifies the PlayerAskTransferList class uses the **same** function.
3. **vftable+0x44 → `0x667D30`** is a native `ret` stub. This source observation does not assign unverified meaning to the original maintenance owner; no extra auto-removal action is invented.

These class-specific facts are backed by direct PE byte inspection now, not reconstructed screenshots/tests or an invented event name. No source bytes are committed to Git; this note records only necessary addresses and instruction semantics.

## Reconstruction changes and explicit non-effects

- `original_eamail_mailbox.py` adds these exact RTTI/vtable/virtual addresses and the strict `source_player_ask_transfer_list_record_ready(original_class)` returning true only for the identified class.
- Existing caller-level `deliver_source_ready_transfer_request` **still demands an explicit readiness bool** plus independently source-authenticated scheduled-envelope identity, recipient/sender and due date; an unprocessed entry is *not* automatically considered delivered merely because its virtual returns true. Unsupported EAM classes still reject.
- `source_known_eam_record_retained` now supports EAMPlayerAskTransferListsub's independently proved 365-day native +0x40 virtual, preserving the strict numeric-day type guard and 21/365 boundaries for already supported classes.
- Tests independently pin RTTI/vftable/function identities, exact due-date rejection even for a ready record, unsupported-class refusal and exact 365-unit inclusive retention/exclusion; no original GUI or mail content claim.

## High-impact continuation

The source-proven underlying scheduled `MPMEAMail` envelope retains its native due date, class/record link and original queue owner `0x947AA8`, drained through `0x613EE0` and `0x5CFA20` during actual original NEXT/PResults. The current port stores `GameState.player_transfer_requests` as pending; there is not yet a complete **native-qualified** dispatcher translating actual distinct envelope/list-node identity and scheduled event tick into per-manager delivery. A timestamp or message in the game's `due_player_transfer_requests()` convenience query is not sufficient alone to assert that the original queue event was visited, removed and stamped. Next establish original pending envelope event identity and execution order across primary/secondary events, then wire actual source-approved per-user delivery and original PEAMail UI.

Original standalone bytes are now reachable with the connected Drive connector, while local `container.exec` still fails harmless commands with `caas.internal.errors.ClientError`. Private source access does not establish a Windows 11 game playtest.
