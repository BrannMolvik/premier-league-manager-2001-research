# Recovery557: normal first-human TeamSelect six-staff construction, shared RNG, club context

**Evidence:** owner's original `footballmanager.exe`, 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, statically disassembled; `Master.dat`, 3,391,446 bytes, SHA-256 `183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8`, independently parsed. The original executable was **not** launched. This is source-level evidence and data-only source component staging, **not a complete visible SupportStart, exact current CRT seed, original GUI observation or Windows11 acceptance.**

## Resolve the confused producer identity before implementation

The real **ordinary first-human TeamSelect** event `0x4D8EF3..0x4D8F7F` creates a human, resets selected user staff lists, then invokes `0x4D8F75 -> 0x4C9CD0`. It immediately stages the original SEVEN SupportStart selector positions through `0x4D8F7F -> 0x4DA4F0`. The source `0x4C9CD0` calls **`0x4C9B30`** for six types in order **1,2,3,4,5,13**. Unlike the separate `0x4D1760 -> 0x4C9D40` staff-reset path, this ordinary route **does not call `0x4CB2B0` (virtual+0x5C)**, so the source-country+0x50 club-pointer vs RNG-bound conflict found in Recovery557 **must not block work on the actual ordinary TeamSelect staff constructor**. That conflict remains relevant to the separate +0x5C pathway and is documented in the earlier source reports. The shared function `0x4CA2F0` constructs each CSupportStaff in either route.

### Original `0x4C9B30` per-staff direct draw order (source-verified, variable)

1. `0x4C9B49` calls `0x64D540(25)` once and adds 25 for original staff+0x0C.
2. `0x4C9B5C..0x4C9BE0` constructs one native staff rating-base input from **two actual caller parameters**: source first context in `EDI` and source third context in `EBX`. Native `0x4C9B30` arguments are `(staff_type, first_context, source_group_id)`. No RNG(2) call on this path. Do not borrow the other `0x4C9D40`'s RNG2 here.
3. `0x4C9C04 -> 0x4CA2F0` constructs CSupportStaff (type, fixed status0, RNG25 age, source base), invoking `0x4CA660` internally at `0x4CA334` for **one native player-name selection pair**. `0x4C9C31` explicitly calls virtual+0x10 **`0x4CA660` again** with the registered current user's original club nationality. The second pair overwrites initial name/surname. Each `0x4CA660 -> 0x421C00` draws one source FIRST and one independent source SURNAME player through the ORIGINAL player-name pools. If selected first name equals source sentinel `"-"`, the function retries **both draws**, not only the first.
4. `0x4C9C3B` calls virtual+0x2C=`0x4CA770` with arguments `(source_group_id,1)`. At `0x4CA770`, true flag forwards that source group argument to vft+0x28=`0x4CA790`. The virtual+0x28 first maps staff type/previous staff+0x10 into a source scalar, then **every recovered conditional branch converges on `0x4CADB0 -> 0x64D540(20)`**, scaling staff+0x08. This is one normal source RNG20 call, not the other constructor's rating RNG2.
5. `0x4C9C42` calls virtual+0x30=`0x4CA640` for a separate unconditional source `RNG(30)` (staff+0x14).
6. `0x4C9C4E` calls virtual+0x58=`0x4CB0F0` with **source_group_id**. This method scans original clubs `0x874B90` in original file order, comparing runtime original `DBRClub+0x10` with the supplied group. It retains the FIRST at most **24** matching club pointers. It then draws `RNG(3)` to choose 1..3 assignments. Each of the 1..3 iterations consumes `RNG(matching_stored_club_count)`, followed by **two separate `RNG(3)`** calls at `0x4CB1CE` and `0x4CB1D7`; accepted source club name/content fills staff per-row fields. If club count is zero, `0x64D540(0)` is still called and the pointer selection has not been proved safe. Do NOT silently invent fallback clubs or assume missing groups are playable.
7. `0x4C9C7B` invokes virtual+0x2C AGAIN with the same pair `(source_group_id,1)`, AFTER global staff list insertion. Thus another `RNG(20)` is consumed on the normal source branch, followed by membership insertion in the selected user's original +0x5D0 staff list.

**Correct direct draw lower bound for one ordinary `0x4C9B30` staff, contingent on normal allocation/name completion and group count>0:** `RNG25 (1) + two name pairs (4) + two RNG20 (2) + RNG30 (1) + RNG3 item count (1) + 3 draws per 1..3 assignments (3..9) = **12..18** direct CRT draws`, **plus 2 for each `"-"` first-name retry**, plus any as-yet-unverified indirect draws in date/format/list support. The numeric 12..18 range looks like a previously published (wrongly attributed) estimate for the OTHER constructor, but this result comes from a separately authenticated **actual TeamSelect +0x58 caller** and must not be conflated. No particular staff name, exact seed, fixed number of actual draws, or complete producer side effects can be claimed from this range.

Source current `reconstruction/support_staff.generate_fixed_initial_staff` calls RNG25 and RNG2 and models only staff age/rating in the *distinct* `0x4D1760 -> 0x4C9D40` pathway. It must NOT be used as a direct source-equivalent implementation of ordinary `0x4D8F75` first-human TeamSelect without a major original behavior correction. Do not patch the shared RNG yet.

## Correct exact source group, existing original club corpus and negative cases

Original `0x4C9CD0` receives its two parameters from native TeamSelect `0x4D8F6D` and `0x4D8F74`. The first context is `screen+0x68 - screen+0x64 - 1`, and the **source group ID** is `[screen-selected-row-pointer+0x4C]`. That pointer is read at `0x4D8F63` through selected screen row control array at `screen+0x2A6C+... `; no source proof yet that its +0x4C can simply be replaced by `selected.club.competition_id`, despite the vft+0x58 club comparison. The real selected row/group resolution is still a necessary input. Do not substitute country, name group, team category or a guessed league ID.

The original club serialized record `Master.dat+8` is decoded to expanded `DBRClub+0x10` by original `0x4022D0` (`0x40230A` deserializes 4-byte source field to temporary +0x10), then `0x403660` copies temp to expanded club+0x10. Existing `fm2001_data.Club.competition_id` correctly reads this original source field.

**Independent authenticated original Master.dat population check:** 1,246 source clubs, 120 unique competition IDs referenced; within original Static.dat IDs 0..192, 73 have no club match. Original ID0 contains 20 matching clubs; ID18 contains 20, ID31 20, ID51 20, while ID170 has **51** matches, **but the native per-staff scan retains only its FIRST 24**, discarding 27. All other populated source groups have at most24 matches. Actual selected first-user row+0x4C has not yet been qualified, so do not infer that an empty original group is actually selectable in the normal UI; instead fail-close any hypothetical empty source choice.

New reusable **source-only no-RNG club candidate projection** staged on existing unopened branch:
- `reconstruction/original_supportstart_teamselect_staff_clubs.py` consumes existing `Club` rows in canonical original source order, checks IDs/competition DWORDs, selects exact matching `Club.competition_id`, retains first24, reports discarded count and explicitly refuses an unresolved zero-bound as a safe playable source candidate.
- `reconstruction/test_original_supportstart_teamselect_staff_clubs.py` covers source ordering, 24-cap/overflow, nonmatching club, zero-bound refusal, invalid index/club/caller arguments and source-count guard. **These GitHub-branch tests have not yet been executed on the exact code head** and therefore are NOT a passing acceptance claim.
- Private raw-original data verification performed independently in shell, not through these new unit tests. No proprietary original source files copied into public Git and no live GameState/RNG/GUI modifications.

## Next player-visible source tasks

1. Source-qualify TeamSelect selected row `[+0x4C]` grouping and first-context fields for real selected club and non-Premier-League cases; distinguish first 2–6 humans and other career paths.
2. Reconcile full **shared CRT seed at ordinary first-human `0x4D8F75`** including earlier mandatory name/youth/competition draws and native +0x58 club selection; preserve correct chosen staff names, ratings, 1..3 club associations and staff linked-list side effects for the actual seven source selectors.
3. Trace source PSupportStart upper GUI owner/context, actual hit dispatch, and **full** seven-row edit/select behavior, original role labels/name editor, Apply versus Cancel, TeamSelect modal return; use already-staged original user_entry/Support art and verified source geometry. Do not substitute an approximate UI just to show something.
4. Then source-complete Inbox selected message/shared CRT, full R1 four match modes/PResults/return, all shipped countries/leagues and 2–6 human careers, Gates13–17 audited Windows11 GUI release. No gate closed from these static findings.

**Reproducible original addresses:**
```bash
objdump -D -Mintel --start-address=0x4d8ef3 --stop-address=0x4d8f84 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9cd0 --stop-address=0x4c9d35 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9b30 --stop-address=0x4c9cbf footballmanager.exe
objdump -D -Mintel --start-address=0x4ca2f0 --stop-address=0x4ca33e footballmanager.exe
objdump -D -Mintel --start-address=0x4ca660 --stop-address=0x4ca6cf footballmanager.exe
objdump -D -Mintel --start-address=0x4ca770 --stop-address=0x4ca790 footballmanager.exe
objdump -D -Mintel --start-address=0x4ca790 --stop-address=0x4cada9 footballmanager.exe
objdump -D -Mintel --start-address=0x4cada9 --stop-address=0x4caddb footballmanager.exe
objdump -D -Mintel --start-address=0x4cb0f0 --stop-address=0x4cb2af footballmanager.exe
objdump -D -Mintel --start-address=0x4022d0 --stop-address=0x402324 footballmanager.exe
```


## Recovery557 continuation: exact TeamSelect row+0x4C producer and shipped selectable league safety

The selected screen row's source group ID is now **fully owned by a native competition-list producer**, not a guessed country/club property:

- Original TeamSelect list construction `0x4D9D49..0x4D9E55` walks original `0x876C50` competition definition owner with source count 193 and stride 0x40. `0x4D9E16` requires source record +0x14 kind==1 (**league**); `0x4D9E1C..0x4D9E2E` requires the original definition's +0x24 country/region to match the current source UI country selector, AND native definition+0x08 parent==0xFFFFFFFF (**root**).
- `0x4D9E36..0x4D9E48` creates/reuses a 0x4C-byte screen row, sets its +0x4C to the **original competition INDEX `ebx`**, initially in source order; `0x4D9F1F..0x4DA035` extracts and sorts the selected rows using original predicate `0x4DA0B0` on native competition definition **+0x16** source signed value. That value is the original `Static.dat` signed initial order field (already read by `FM2001Database._parse_competitions`). Sorting tied +0x16 entries does not establish a unique original pointer order, and must not be changed to arbitrary modern alphabetical order.
- `0x4DA05D..0x4DA07E` writes each post-sort selected **original competition index** into actual `screen-row+0x4C`. Later `0x4D8F63..0x4D8F75` reads that exact selected row+0x4C and passes it to six fresh `0x4C9B30` staff constructors; `0x4CB13C` compares this SAME ID with each club+0x10 original competition ID. The source club-group input is now qualified through **UI list -> selected competition index -> original club membership**. Do not substitute player nationality or DBRCountry+0x50.
- Native original `0x4DA0B0` comparator `0x4DA0D1..0x4DA0E1` compares competition +0x16 signed WORDs; even for tied displayed rows (original IDs 24 and83 share country33, order9), both carry their distinct authentic source ID in row+0x4C, so its actual selected row remains authoritative. No exact original sort order is claimed for the tie.

**Privately verified entire source corpus, not an artificial example:** independent SHA-256-checked Static.dat+Master.dat parsing gives **23 source root type1 leagues**; ALL 23 have **at least 10 and at most 24** original clubs matching exactly their source competition ID. There are **NO zero-club groups and NO over-24 truncations in this native root-league selectable set.** Native source ID0=20, ID2=24, ID3=24, ID4=24, ID7=22, ID17=18, ID18=20, ID21=18, ID22=18, ID24=18, ID26=18, ID27=12, ID28=10, ID31=20, ID32=22, ID40=18, ID50=18, ID51=20, ID54=18, ID81=10, ID83=18, ID87=10, ID96=18. These represent source-eligible ROOT competition rows, not proof that all 23 are immediately GUI-visible to every human manager or that later seasons/tiers follow the same list. Original nationality/country selector may restrict which subset the user can see. The separate master competition ID170 has51 clubs and is subject to +0x58 first24 cap, but **is not a type1 root league in this canonical TeamSelect producer**, and must not be incorrectly treated as a normal UI staff generator overflow.

**Original-scope behavioral value:** The +0x58 original group-to-club count is positive and <=24 for *every source-eligible initial TeamSelect league row* in the actual shipped corpus. This eliminates the empty/over24 source group concern **only for canonical initial TeamSelect's source-eligible root leagues**; preserve the fail-closed contract for other or later unknown group IDs. It also identifies a tractable source-bound way to derive staff hometown/club associations without touching ambiguous DBRCountry+0x50 or inventing player names.

Reproduce: `objdump` `0x4D9D29..0x4D9E55`, `0x4D9F1F..0x4DA095`, `0x4DA0B0..0x4DA0E1`, `0x4D8F54..0x4D8F7F`, `0x4CB115..0x4CB16B`; privately hash and decode 193 original Static.dat competition rows and 1246 Master.dat club rows with the existing port parser field offsets (comp parent +4, kind +14, signed order +15, country/region +27; Master.club competition ID +8). No original bytes or UI screenshots committed.


### Source correction: TeamSelect row ties ARE resolved by its native small-range stable sorter

The earlier text above saying the initial TeamSelect league-row equal-key order is UNKNOWN was too conservative, because it conflated this selector sort with the separate country+0x48 competition-pointer `qsort` from `0x4F7380`. **Those are different source sort operations.**

- The original TeamSelect list `0x4D9FE3..0x4DA035` tests its pointer-array byte span against **0x40=16 pointers**, invoking **`0x4DA980`** small-range sorter (as also encoded in the already-merged `original_teamselect_native.native_competitions_for_country`).
- Original `0x4DA980..0x4DAA1D` is an insertion-sort-style implementation using `0x4DA0B0` strictly-less-than predicate and not shifting equal original+0x16 initial-order keys out of their input order. It therefore **preserves original Static.dat source index order on equal keys** for lists at most 16.
- All 23 actual original type1 root competitions are distributed among eight country/region IDs, maximum **five root leagues per country** (source country26). Thus **every ordinary initial TeamSelect league row list uses the stable small-range path**, never the >16 comparator/quicksort path. The only observed tie is country33 with source IDs **24 and 83** both signed source order9; the correct TeamSelect tie order is therefore **24, then 83**.
- This is the same behavior that active main's `native_competitions_for_country` already implements with Python's stable `sorted()` on original source order. **Do not needlessly reimplement or fail-close that source-known initial UI tie**. Continue treating source country+0x48 sorting and later-game dynamic tables as separate, potentially unresolved cases.

This correction is source-proven by static x86 and original corpus, not original process/GUI observation. Reproduction: disassemble `0x4D9FDB..0x4DA035`, `0x4DA0B0..0x4DA0E1`, `0x4DA980..0x4DAA1D`; inspect the original decoded `Static.dat` root league country/order pairs. The actual UI row+0x4C source competition ID and **stable initial row ordering** can be reused from the already-merged native TeamSelect model. 


## Recovery557 source scalar closure: first-manager initial rating base is not RNG2

The normal player-visible `0x4C9B30` source now also qualifies the **exact deterministic fourth constructor argument**, read by CSupportStaff+0x10 and later virtual+0x28:

- `0x4C9B50: mov ebx,[esp+0x28]` loads the original *third* `0x4C9B30` call argument, already traced to selected TeamSelect source league index at screen-row+0x4C. `0x4C9B68..0x4C9BE0` loads `edi=[esp+0x20]`, the native *second* argument, already traced to `screen+0x68 - screen+0x64 - 1` from `0x4D8F6E..0x4D8F74`.
- Source dispatch table at exact original PE `0x4C9CC0` contains branch addresses for group IDs 0/1/2/3: `0x4C9B68 / 0x4C9B82 / 0x4C9B9C / 0x4C9BB5`. Each branch selects base **4,3,2,1** respectively; any group ID >3 takes default base1. `edi ==1` or `edi ==2` **increments that base by one**. No other values alter it.
- The source `0x4C9C01..0x4C9C04` passes this `esi` base, source fixed byte0, age RNG25+25, and staff type `edi` (reloaded from actual staff type first arg at `0x4C9B68..0x4C9BC9`) to `0x4CA2F0`. `0x4CA2F0` stores the first input type at native+0x04 and the derived base at native+0x10. Source normal constructor does **not** consume RNG2 here; it consumes subsequent two RNG20 through +0x2C and the separate RNG30, as documented above.
- The new pure source helper `original_teamselect_staff_initial_scalar(source_group_id,selection_context)` is staged alongside authentic club-pool projection. Tests cover source group0/1/2/3/default, source context1/2 increment, other values and input validation. This does **not** replace/reset the preexisting `support_staff.initial_staff_rating_base` for the **different** `0x4C9D40` path, and it does **not** advance the live GameState RNG or fabricate staff names.
- In the actual shipped initial source root-league set, group IDs include 0,2,3,4,7,...,96, so base can be 4 for source ID0, 2 for ID2, 1 for ID3+, plus the second-context increment when appropriate. Any code that blindly equates “Premier League” with just source context0, or assumes the type/rating is uniform across all original selected human slots, is incomplete.

Reproduce original at `0x4C9B49..0x4C9BE0`, PE raw 4× DWORD jump addresses from `0x4C9CC0`, `0x4C9BF1..0x4C9C09`, `0x4CA2F0..0x4CA33C`, `0x4D8F54..0x4D8F79`. **No original process was executed, new helper tests not executed on exact branch head**, live original shared CRT checkpoint and original visible SupportStart remain incomplete.
