# Gate 13: original 7D7760 expiry may create a new 7BD564 human return notice

15 October 2026 KST. **Independent original static source, not native game execution or live Inbox.** Base main `5c98135a10c8e5628fb0ab230d62bfa36c2d6922`. This is an independent source-evidence work-ahead branch while PR #739's Gate13/source/save package undergoes full CI/review; do not merge/pr this investigation alone.

## Verified actual original player journey dependency

Original executable `footballmanager.exe` 4,714,541 bytes SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, independently read with x86 `objdump -D -Mintel`. This source is a **critical counterexample** to equating `GameState._run_daily_injury_returns` with original `7D7760` expiry.

Native `60AB77..60ABDD` inserts 7D7760 with event+4 raw due date, +8 count=1, +C allocated pointer to player ID. Due `613EE0` calls vtable+10 `5D7B40`. Original `5D7B40`:
1. Loops event +8 player-count and resolves array +C[i] into original player+10 signed club index / roster base `875640`.
2. Tests current registered human club owner via `4139E0` at `5D7BA5`; AI/unmatched paths bypass notification but still reach cleanup.
3. For human, first `4D1190` from registered-user+5DC at `5D7BCD`; if null, then `4D1110` at `5D7D77`; else generic family. Distinct native status 0/1/2/3 constructor jump tables `5D8108`, `5D8118`, `5D8128`, 12 classes.
4. If a notice object is constructed, `5D8098→5D80C6` allocates a *new* 12-byte 7BD564 envelope with **current** native `9847FC` day (not original expiry day guessed from Python), points +8 to newly constructed message, ORs notice+8 bits 2 and 1 (`0x6`), and enqueues global `947AA8` through `613EC0`.
5. Regardless of branch, `5D80CB..5D80E2` resolves current player and calls `418AD0` to clear original player+24C descriptor and player+14 injury bit. The event has multiple-player loop capability; do not assume every 7D7760 event is one player simply because the 60AA20 constructor first creates count1.
6. Any resulting 7BD564 notice must later be processed through global pending `613EE0` / original 413020 registered-user routing, retention and PEAMail, **not immediately displayed**.

This return notice class is **not the injury-onset 606540 class** and is **not a transfer mail**. Its original localized +18 title maps to STR ID **1407**, text template `{PLAYERNAME:1} recovery`, independently verified in **all 12** concrete vtables and IDX ordinals using original EnglishEAM.str/idx hashed bytes. Distinct +1C body variants must not be flattened to one invented message.

## Original constructor/status × title/body source mapping

Rows are in original branch families: original `4D1190` non-null (type31), original `4D1110` non-null (type30), both null (type2). The original second 5CE660 descriptor pushes literal 31, 30 or 2 respectively. Status3 branches explicitly OVERWRITE the constructors' initial vtables after native construction: family31 `5D7D51` writes `7CB37C`, family30 `5D7F04` writes `7CB424`, and family2 `5D8082` writes `7CB2D4`. These final vtables retain the shown +18/+1C callbacks but **must not** be mistaken for the temporary constructor initial vtables `7CB3D0`, `7CB478`, `7CB328`. Family30 status3 calls actual constructor `59EFA0`, NOT `59EF90` (an adjacent 4-byte-return stub). All table values here were directly read from the original PE and language table, not inferred from modern reconstruction.

| Family | Status | Original constructor | Concrete vtable | +18 title callback | +1C body callback | Title IDX | Body IDs at +1C arg 0/1/2 |
| --- | ---: | --- | --- | --- | --- | ---: | --- |
| 31 | 0 | 59D6B0 | 7D3F8C | 59D740 | 59D7C0 | 2328 | 1411,1411,1411 |
| 31 | 1 | 59DFF0 | 7D4088 | 59E080 | 59E100 | 2343 | 1417,1417,1417 |
| 31 | 2 | 59E970 | 7D4184 | 59EA00 | 59EA80 | 2358 | 1423,1423,1423 |
| 31 | 3 | 59F2B0 | 7CB37C | 59F340 | 59F3C0 | 2373 | 1429,1429,1429 |
| 30 | 0 | 59D3A0 | 7D3F38 | 59D430 | 59D4B0 | 2323 | 1408,1409,1409 |
| 30 | 1 | 59DCE0 | 7D4034 | 59DD70 | 59DDF0 | 2338 | 1415,1415,1415 |
| 30 | 2 | 59E660 | 7D4130 | 59E6F0 | 59E770 | 2353 | 1421,1421,1421 |
| 30 | 3 | 59EFA0 | 7CB424 | 59F030 | 59F0B0 | 2368 | 1427,1427,1427 |
| 2 | 0 | 59D9C0 | 7D3FE0 | 59DA60 | 59DAE0 | 2333 | 1413,1413,1413 |
| 2 | 1 | 59E340 | 7D40DC | 59E3E0 | 59E460 | 2348 | 1419,1419,1419 |
| 2 | 2 | 59EC80 | 7D41D8 | 59ED20 | 59EDA0 | 2363 | 1425,1425,1425 |
| 2 | 3 | 59F5C0 | 7CB2D4 | 59F660 | 59F6E0 | 2378 | 1431,1431,1431 |

All 12 original body functions statically contain explicit addresses of the three selected EnglishEAM.idx slots immediately following the title ordinal, each descending 4 bytes from native slot base 87AC28. Original title source verified all 12 map to IDX 1407; first body variant STR IDs listed above. This does **not** prove original GUI argument beyond the separately audited original first-click +1C(arg0) user route, native token substitution, actual use/read status or human Inbox rendering.

## Source-constrained adapter and verification

A separate portable **source-only** helper, `reconstruction/original_native_7d7760_human_return.py`, now records all 12 native 5D7B40 human lookup/status routes and the potential new 7BD564 wrapper date, paired with the existing original `418AD0` cleanup projection. It restricts the current path to an actually reached **count1** original 60AA20 event (native 5D7B40 itself can handle count>1). It requires source event+0 vtable, +4 due day, +8 count, +C nonzero original payload pointer, +10 status, independently reached allocated player-ID DWORD and native player+4/+14/+24C. Original source `60ABDA` writes ONLY BYTE+0x10; event padding +0x11..+0x13 is uninitialized and deliberately unconstrained. It requires explicit original human gate 4139E0 and conditional 4D1190/4D1110 inputs. Source notice creation is conditional on native allocations, and neither GameState nor true 613EC0/418AD0/PEAMail mutation is claimed.

`reconstruction/test_original_native_7d7760_human_return.py` stages the 12 family×severity cases, AI cleanup with no notice, signed native due boundaries, all 12 original title/resource IDs, forged owner/status/payload negatives, and optional private original PE instruction/jump-table assertions. Independently executed private PE checks confirm **12/12 +0x18 title vtable functions, 36/36 +0x1C body slot references, 12 original IDX title 1407 entries and all 3 final status3 vtable overrides with zero mismatches**. These are source-static checks, not an execution of the NEW Python tests. This research-only branch has not opened a PR or run CI while cross-cutting parent PR #739 awaits independent review.

## Unresolved integration and next actions

Original `5D7B40` contains native constructors, owner lookup and allocation branches, which source-prove *possible* behavior but are not direct original-run acceptance. Read the complete native status-case and actual notice callback ownership before claiming all branches. Implement a typed return-notice event family **separate from 606540 onset** and linked 7D7760 cleanup with both native calendar/raw dates and human owner first-match. Stage atomic GameState + registered-user queue + saved state + original Inbox + tests for 2+ same-day injuries and expiry, owner changes, no doctor/physio, raw signed wrap, no registered user, and deferred 614080. Restore matching original body/title before rendering. PR739 already adds source-only onset notice Save/Load and still must undergo exact-head full CI/review. Do not merge overlapping GameState save changes blindly.

Gate13–17 and physical Windows11 install, native GUI and all-mode gameplay audits remain open.
