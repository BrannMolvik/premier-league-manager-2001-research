# Gate 13 Recovery582: native Inbox filter geometry and missing-asset identity boundary

**Date:** 13 October 2026 KST. **Original executable:** owner-authorized `footballmanager.exe`, 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Verified again by local `sha256sum`, inspected only through static native PE disassembly. The original process was **not** launched or GUI-playtested. Gate 13–17 remain OPEN.

## Reconcile stale specialist Inbox work before new implementation

The old `codex/original-inbox-list` branch HEAD `da5a1d6b6b5620295d67ab2cd3da12d8dfdd822b` is 12 historical commits behind main at the Recovery582 inspection and its `original_eamail_row_text.py`, `original_eamail_tagged_player_masks.py`, and `test_original_eamail_list.py` were **byte-for-byte identical** to then-current `main`. Other changed files in `main` contained all old-branch lines except more recent independent Received-header sorting and host support. The original readable-list milestone was already integrated as main commit `8d81c44d27463ee52a287e98d2db60b919c64877`, as confirmed by commit search and actual file comparison. **Do NOT merge the old Codex branch or reproduce this already-completed work.** Main later advanced by PR661 to `be50dcc8850b767a8ae199f5704685a3ba133ebf`.

## Original ten native Inbox filter groups, static proof

- `0x47B202 -> 0x474B10` constructs PEAMail, and `0x474C71..0x474C8B` invokes MSVC vector constructor `0x6687C1` with count **10**, stride **0x4C**, initializer `0x5D4DE0`, owner start PEAMail `+0x64C`. Original `0x474CAF..0x474CC9` separately creates FIVE sort controls at `+0xC14`, stride 0x54; never conflate these groups.
- Filter `0x5D4DE0` uses final native vtable **0x7D6CC8**, creates two actual children at `+0x44` (radio) and `+0x48` (label), and registers them through `0x5D4580` with native flags `0x17`, `0x15`. Final parent vft+0x6C is `0x5D4AC0`, **not** generic `0x64F7A0`.
- Each PEAMail UI owner invokes `0x5D4F00` with original source input x=22,y=30+30*i for indices 0–9, width **183**, height **28**. `0x5D4F00` calls actual native coordinate setter `0x64F380` with those dimensions, and separately binds child radio wrapper `0x941430` through `0x652940`, child label source. The native PEAMail panel origin is `(0,148)` in the prior source-qualified management route, so for that exact origin the first panel-local box is screen `(22,178,183,28)` and the tenth `(22,448,183,28)`. These are **native rectangle prefilters, not unconditional native mouse acceptance**.
- English source label IDs come from globals `0x984534-4*i` with original `English.idx` ordinals **177–186**. Native string values from the earlier independently verified original table: New, All, Finance, Building, Events, Player/Team, Transfer Market, Youth Team, Contracts, FA. Do not confuse New filter0 with Unread status bit2: original initial source filter0 tests status bit4.
- Native `0x5D4AC0` input handler checks `control+0x18` state bit1, additionally reads `control+0x38`, tests `control+0x20` with event nonnull and invokes owner+0x24 virtual+0x0C, and checks native boolean byte +0x40 before virtual+0x98 and event callback+0x10. The `+0x38` producer/current state is not closed from this trace. Therefore **do not dispatch native filter changes from 183×28 bounds alone**. `0x472680` selects first active group via `0x651AB0`, then applies index0/status bit4, index1/All or category equality predicates; this is already bounded in `original_eamail_native_filter.py` for initial transfer request only.

## Original bitmap provenance problem, explicitly unresolved

- `0x5D4F2D` passes radio wrapper **0x941430** to native `0x652940`. That wrapper initializer `0x5FFF20..0x5FFF4A` calls `0x64E500` with original source crop 28×28; its loader `0x5FFF60..0x5FFF73` passes filename literal VA **0x8397BC** to `0x64D750`. The literal is exactly `fm2001_art\\generic\\GenericButtonsAndBars\\boost_type_11.444`. A sibling wrapper `0x5FFFB0` expects a **169×25** source frame loaded through literal `0x8397F8`, `boost_type_11_anim.444`. Filename bytes are verified **in the original EXE**, not guesses from current reconstructed art.
- The authenticated extracted private Google Drive `FM2001/FM2001_Art/Generic/GenericButtonsAndBars/` currently lists **115 files with no `boost_type_11.444` or `boost_type_11_anim.444`**. That folder does contain `button_type_11.444` and `button_type_11_anim.444`, but they are **NOT automatically proven substitutions or aliases**. Separately byte-materialized original `button_type_11.444` is 1,448 bytes, header 169×25, SHA-256 `de2b1153398bd1c170459e10b634a8079dd642184a7a19e0826603b84e558393`. Original `button_type_11_anim.444` is 972 bytes, header 27×25, SHA-256 `e5a755396195121748b1b0f9f07cada4c98137f239b82e3fd9979189ac390d91`. Those dimensions do not establish the loader's 28×28 radio identity; do not silently use a same-sounding file.
- Source `0x64D750` delegates to `0x64D870` and later a resource provider (`0x64D930`), so **directory filename absence alone does not establish absence from `Resource.res` or the original at runtime**. Audit exact original resource-pack entry/provider or actual original observation before declaring a missing shipped sprite, drawing a substitute or wiring the visible filter group. The user's already uploaded original files should be reused. Do not request them again because of this bounded discrepancy.

## Branch work and next player-visible step

`reconstruction/original_eamail_filter_controls.py` records only original ten owner offsets, registered native children, English ordinal identity and half-open window prefilter. `test_original_eamail_filter_controls.py` covers all ten records, native bounds including edges, disabled states and malformed source identities. **No UI is wired**; current player-visible Inbox has readable rows, Received sort and arrows, but complete ten filters are missing. This branch has not opened a PR or run exact-head CI; full Windows 11 acceptance remains unverified.

**NEXT:** inspect the private `Resource.res` exact boost sprite path/provider (`0x64D930` and referenced resource map), source native filter +0x38 callback/owner and PEAMail vft event forwarding, then render the authentic ten controls with actual source fonts/art and connect a received click into the existing selected-user delivered EAMail filter and scroll reset. If source pack mapping remains unavailable, defer only that art boundary and work on the next source-verified visible Gate13 control. Do not merge this research-only branch as a standalone PR.

### Reproduction commands (private original EXE, no bytes in Git)

```bash
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x474c71 --stop-address=0x474cca footballmanager.exe
objdump -D -Mintel --start-address=0x5d4de0 --stop-address=0x5d4eb9 footballmanager.exe
objdump -D -Mintel --start-address=0x5d4ac0 --stop-address=0x5d4b43 footballmanager.exe
objdump -D -Mintel --start-address=0x5d4f00 --stop-address=0x5d4f75 footballmanager.exe
objdump -D -Mintel --start-address=0x5fff20 --stop-address=0x5fff80 footballmanager.exe
objdump -D -Mintel --start-address=0x5fffb0 --stop-address=0x600010 footballmanager.exe
objdump -s --start-address=0x8397bc --stop-address=0x839830 footballmanager.exe
objdump -D -Mintel --start-address=0x472680 --stop-address=0x47276d footballmanager.exe
```

## Recovery582 resource-provider follow-up: no inferred `button` alias

Additional targeted authenticated source byte checks:

- Private extracted `FM2001/Resource.res` was separately materialized, **2,114,750 bytes**, SHA-256 `7abd0213aacede533af438296ecc67271ada8c16b69f2aacd96df9b8d050bb38`. A case-insensitive raw-byte scan showed **zero readable occurrences** of `boost_type_11`, `button_type_11`, or `.444`. This is only a negative **plaintext-string** check, not proof a compressed/hash-indexed resource pack lacks the image.
- Original EXE separately contains the distinct literal `fm2001_art\generic\GenericButtonsAndBars\button_type_11.444` at VA **0x835B28**, loaded at `0x5F4814`, while the native Inbox filter radio `0x941430` loader uses its **different** `boost_type_11.444` literal at VA **0x8397BC** in `0x5FFF64`. The two paths and loader objects are not automatically aliases. The original EXE also contains `boost_type_11_anim.444` at VA `0x8397F8` loaded by `0x5FFFF4`. The extracted `button_type_11_anim.444` is NOT named in the original EXE's plain filename literals.
- Original image loader `0x64D750 -> 0x64D870` stores the exact filename, later `0x64D930` builds a resource lookup through `0x657820`; deeper provider semantics and possible mapped aliases remain **UNQUALIFIED**. Do not assert the alternate source will be loaded by the genuine original. No bytes from the original EXE/resource pack have been put in Git.

**NEXT:** static trace `0x657820` actual filename/file/resource resolver and inspect exact native list constructor/callback owner +0x38 for filter rows; if the boost asset remains absent or provider can't be bounded without running original, record only the art/UI criterion as a deferred blocker and work on another already-evidenced playable Gate13 surface. Do not accidentally repair the original game's files by substituting the `button_type_11` atlas absent source evidence.

## Opt-in native-source regression and resource provider limit

`reconstruction/test_original_eamail_filter_controls.py` now contains a gated, **real original PE32** test using `FM2001_ORIGINAL_EXE`: canonical SHA check, final filter vft+0x6C exact `0x5D4AC0`, source `0x5D4F10` width183/height28 bytes, direct native 0x5FFF64 `boost` literal push, and *distinct* 0x5F4814 `button` literal push. The original process is never run. Ordinary deterministic bounds/guards have separate tests that do not require private files. Exact-head branch tests have NOT been run or claimed passed.

Native `0x64D750 -> 0x64D870` registers the loader name pointer. `0x64D930` builds a backslash-delimited lookup candidate using global string VA `0x818950` and calls `0x657820`. That routine traverses a provider interface through `0x684F9D/0x684DEF`; the latter invokes a virtual file/read provider and can return a source error. These bounded static facts do **not** establish that `button_type_11.444` automatically substitutes for `boost_type_11.444`. The native provider implementation and any lookup aliases remain unverified. No DLL/process was executed.

**Next safe research/action:** trace concrete provider backing and the seven actual filter group state/callback owner fields; if unresolved beyond available original source bytes, leave the exact art as blocked, and choose another independent source-qualified Gate13 player-visible function rather than invent a resource or drawing the wrong image.

## Recovery583: filter ID2–11 source dispatch and real presenter snapshot

13 October 2026 KST, original EXE SHA-256 independently recalculated `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Only source disassembly; **the original process was not run**.

**Original control/event/producer proof:**

- `0x46E8E8` initializes **EBP=2**, before first filter registration `0x46EA34..0x46EA54` passes it to row vft+0x08; 0x46EA57 passes first source label English ordinal177 to `0x5D4F00`, with source `push 1` initial selected. Subsequent nine registrations at `0x46EADC..0x46F04F` pass literal native row IDs **3,4,...,11**, always the same first group pointer `PEAMail+0x64C`, and source `push 0` initially unselected. They are NOT all native event0. This corrects the earlier source-owner ambiguity.
- PEA first owner `0x474B56` vft `0x7BE674`; its **+0x0C = 0x42DE00**, exact `mov eax,1; ret8`, so owner callback gate accepts. Its +0x10 `0x428AE0` is **a no-op**: do not claim that this particular callback immediately calls the full modal dispatch. The source event `0x4721C0` may be delivered through a separate route; full Win32-to-PEAMail delivery is not observed.
- Filter final vft `0x7D6CC8` **+0x6C=0x5D4AC0** and **+0x98=0x5D49F0**, byte-confirmed from real PE. `0x5D4F00` calls `0x5D49B0` with first group address; source `0x5D49B0` writes `filter+0x38` group pointer and iterates every `0x4C` to maintain group member count in group+0x3C. All ten original radio owners share that exclusive-selection group. Source `0x651AB0` reads each row+0x40 selected flag. `0x5D49F0(select 1)` first clears all previously selected flags and the matching child +0x44/+0x48 selected bit0x8000, then marks the chosen row selected and its actual children. `0x5D4AC0` gates state bit1, checks +0x38, PEA virtual+0x0C and +0x40 and only calls vft+0x98(1) if the row is not already selected. Re-click of active filter is idempotent but is still an eligible handled event, not an unselect toggle. Its native vft+0x6C returns 1 when enabled and grouped even for some branches that do not change selected state.
- Original PEA dispatcher `0x4721C0` reads `[control+0x20]` and a source 25-byte branch selector at `0x47236C`. The **ten IDs2..11 ALL map to `0x4722C3`** by exact original jump-table entries `0x472354`. That handler loops ten original group pointers (`esi+0x66C`, stride0x4C), matches native event ID to each `control+0x20`, clears native preview selected pointers (0x876754/0x87675C), calls `0x472680` source-selected-user mailbox filter and `0x472880` source sort. The original initial native first filter index0 tests status bit0x04 (`New`), index1 accepts all, indexes2–9 compare categories. No `Unread` substitution.

**Implemented in grouped WIP branch, not player-visible art:**

- `project_original_eamail_delivered_filter_event` is an independently useful, **explicitly source-delivered-event-only** boundary. It maps control IDs2..11 to ten mutually exclusive filter indexes and original `0x4722C3` rebuild/preview-clear flags. A bare rectangle or non-delivered event cannot invoke it. The function is not a substitute for proving original Win32->PEA delivery.
- `OriginalManagementPresenter` now retains an original `eamail_filter_index` (initial0), projects it through the actual real selected-user delivered EAMail row filter/sort snapshot, preserves choice during qualified Received-sort or scroll interactions, and resets it on new Inbox panel construction. It exposes `source_accepted_eamail_filter_event(id)` for a future authenticated GUI source adapter; it does **not** connect the missing physical radio art/WM input. When old scroll offset is nonzero, it fails closed rather than invent source scroll repositioning; this is explicitly a LIMITATION, not original end-user parity. Tests cover all ten ids, invalid events, zero-row category filtering, full matching category source records, sorting/scroll/new panel state and transactional invalid-input behavior.
- Original native filter radio `0x941430` still loads literal `boost_type_11.444` not listed in authenticated extracted sprite directory. Resource provider mapping and whether it falls back are unresolved. This is a **real player-visible fidelity blocker**, not permission to paint `button_type_11.444` or a modern substitute. Existing ordinary Inbox screen does **not** display ten original filter groups. No original Windows GUI acceptance or Gate13 completion.

**Reproduce static switch table and owners from verified original executable:**

    objdump -D -Mintel --start-address=0x46e8e8 --stop-address=0x46e905 footballmanager.exe
    objdump -D -Mintel --start-address=0x46ea34 --stop-address=0x46ea6e footballmanager.exe
    objdump -D -Mintel --start-address=0x46ef77 --stop-address=0x46f061 footballmanager.exe
    objdump -D -Mintel --start-address=0x5d49b0 --stop-address=0x5d4b45 footballmanager.exe
    objdump -D -Mintel --start-address=0x4721c0 --stop-address=0x472354 footballmanager.exe
    objdump -s -j .rdata --start-address=0x7d6cc8 --stop-address=0x7d6d65 footballmanager.exe

**Next:** exact-head automated tests/independent review of WIP; trace original Win32 modal-to-PEA event forwarding and original boost image actual provider. If impossible without native original observation, record exact unresolved condition and advance a different original graphical Gate13/player-visible milestone. Do not mark this a complete Inbox, Gate13 or Windows11 release.
