# Recovery529: native PEAMail small-array sorter and eight-row selected-human window

11 October 2026 KST. **Gate13 OPEN.** Fresh continuation from main `841a371cabd469e5bb588a5ee9491f1a9ec729b0`, after PR608. The original first-party executable is already privately materialized at SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` (4,714,541 bytes); independent native `objdump` reexamination this recovery. The executable has **not** been run and its bytes/disassembly output are **not** committed.

## Reproducible original source, scoped claim

```sh
sha256sum footballmanager.exe
objdump -d -M intel --start-address=0x472680 --stop-address=0x472cc5 footballmanager.exe
```

1. `PEAMail::0x472680` first walks the real selected DBRUser+0x6B4 message list and constructs a separate `PEAMail+0x68` pointer array. For the source-proven transfer message class, original constructor `0x56FAD0` and producer `0x41B68B` establish category5/initial flag0x06, so native filter indices 0,1,5 include it and other category indices reject.
2. `PEAMail::0x472880` selects first active original order control `+0xC14/+0xC68/+0xCBC/+0xD10/+0xD64`, falling back to fifth date comparator `0x472C60` when none is active. The native comparator functions at `0x472C80`, `0x472CA0`, `0x472BA0`, `0x472C00`, `0x472C60` are **strict predicates**; date comparator returns 1 only if first native record day is **greater** than the second.
3. Source `0x472919..0x472920` selects its small-list branch for **at most sixteen 32-bit pointers** (<=64 bytes). Insertion loop `0x47293D..0x4729A4` compares the newly encountered message pointer against prior entries: when strict comparator is nonzero, preceding entries move right; when equal (strict comparator returns 0), original append order survives. This conclusion is **limited to the small source branch**, not the larger source `0x4729AB..0x472B4B` hybrid partition/sort, which has distinct tie possibilities.
4. For the initial PlayerAskTransferList subtype only, native flags `0x06` mean the first sort comparator (bit0x01) is always false and second (bit0x02) is always tied. Source append order remains unchanged in those two sort modes. Default/fifth uses source scheduled record dates descending, stable among identical dates in this small native insertion branch. The existing port date field is the chronological representation of the original scheduled event day; **no arbitrary message-created-now dates** or future pending events are substituted.
5. Two remaining sorts use message `+0x1C` resolved text and virtual `+0x18` text. Original text bytes, locale comparison and subtype-specific generated string source are not independently closed. Thus **fail closed for >=2 rows in modes2/3**, accepting zero/one rows only because no comparison is executed. Native lists **above sixteen** fail closed rather than silently switch to Python sorting. This is a deliberate non-acceptance boundary, not completion of the original Inbox.

`PEAMail::0x472B4F..0x472B84` computes max scroll `max(0,count-8)` and calls the existing eight-slot `CMessageList` whose source panel-relative region is (233,30,545,160), row pitch20, original source row graphics532x18 already hash-imported. This work produces a **read-only native data viewport** using the existing verified owner and source helper; it is NOT a rendered row, input mapping, or original GUI acceptance.

## Reconstruction implementation

- `reconstruction/original_eamail_native_small_window.py` composes source-verifiable filter+original small insertion sort+eight-row viewport, preserving original source selection/comparator addresses, strict source subtype and cutoff, and rejecting unsupported comparison modes.
- The `build_selected_user_initial_eamail_window` entry first calls the live `ManagementSourceDataBridge.source_delivered_mailbox_for_selected_user()`. That bridge verifies actual selected registered manager mailbox (not other users or the global pending transfer queue); the runtime simulation implementation is *not imported back into the bridge*.
- Source-driven tests exercise true registered-human source ownership, pending-invisible case, ordering/ties across 10 records, viewport scroll, status and date modes, 16 vs17 boundary, string-mode refusal, invalid selections and no mutation. Exact-head Gate13 source/test CI required before merge.

## Whole original player journey and remaining blocking requirements

**Source-verified:** original initial transfer subtype category/flags, exact 10 filtering categories, five comparator function identities, **small-list** insertion tie rules, source viewport width/count/scroll. **Port tested:** only after exact PR-head CI passes. **Unimplemented / not VISIBLE-ACCEPTED:** original input PBg header ID1 and PMenu child0x65 navigation; actual raster of row/header/filter controls; original EAM record +0x1C and virtual+0x18 string construction, original source fonts and icons; interactive row selection/re-activation and PEAMMessage modal/action/Escape return; live status mutation; original >16 sort algorithm; class-specific expiry; other polymorphic inbox messages; full 2–6 human control and all countries, non-PL and secondary fixtures; native Windows11 mouse/render validation. This is a foundation for **completing those player-visible steps**, not another claim of an entirely restored screen.

**Next:** source-close native original transfer-message text/field producer and rendering while integrating the authentic ten category and five order controls into the player-visible PEAMail menu/header journeys. Gates13–17 and the verified Windows11 release remain OPEN.
