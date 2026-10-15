# Recovery644: original PResults complete initial five-child inventory, static source

15 October 2026 KST. Starting canonical main after reviewed/merged PR753: `d3db81d86029873ac63ab525f1050cdf64b072c6`. Active WIP branch `worker/gate13-r1-original-normal-player-644`, intentionally **no PR/remote CI yet** because complete normal player-visible match route remains unresolved. Active Gate13 reopened; Gates14–17 and actual Windows11 user GUI/release acceptance **OPEN**.

## Original authority, not synthetic imitation

Private user-authorized **shipped** `footballmanager.exe` 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, read-only `objdump -D -M intel --start-address=0x4a6e45 --stop-address=0x4a6fbe`. The original executable was **not run**. The original `FM2001_Art/Generic/Waiting/waiting_back_2.444` was independently retrieved as **46,448 bytes SHA256 `289b692919b3048bbe932eaf83083c622089fe4367d8124cd26a8bbf566899e5`** from the private extracted original Drive tree, specifically exact non-shared file ID `1MlTY24WId0hnynvkAk5chJLFhG3Acy8t`. Original graphic is not uploaded into GitHub by this branch. Original user-provided extracted disc source, not the Windows reconstruction RC, supplied the bytes.

### Native child factory and positions

The PResults initialization at original `0x4A6E50` checks already-initialized +0x5C and only constructs once. `4A6E61 PUSH 0x14` allocates five 4-byte child-array slots. `4A6E74` writes native child count 5 at owner+0x38. The initial registered children are, in their actual native index order:

| index | embedded PResults offset | source (x,y) | source (w,h) | initial control ID | constructor |
|---|---|---|---|---|---|
| 0 | +0x16C | (0,513) | (800,87) | **0** | 0x651BA0 / wrapper 0x946630 original waiting_back_2.444 |
| 1 | +0x1A0 | (0,518) | (800,38) | **0** | 0x6503F0 |
| 2 | +0x1E0 | (0,556) | (800,18) | **0** | 0x6503F0 |
| 3 | +0x220 | (0,579) | derived from original global 0x946604/0x946608, **not a fixed known size** | **0** | 0x64F380 |
| 4 | +0x270 | (0,581) | copied from original embedded progress-owner +0x250 bounds, **not a fixed known size** | **0** | 0x64F380 |

Child0 bitmap source/position original `4A6E98..4A6EA6`. Children1/2 exact (y=0x206/0x22C,w=0x320,h=0x26/0x12) at `4A6EC0..4A6EDD` and `4A6EF7..4A6F17`. Child3 origin y=0x243 and initial dynamic bounds through 0x64F380 at `4A6F31..4A6F53`. Native **+0x250** control is constructed at `4A6F63..4A6F76`, but **is not an additional index 5 in the five-pointer initial child array**; child4 gets its width/height from +0x250 at `4A6F90–4A6FA9` with y=0x245. Native 0x4A7190 later adjusts actual progress width from event counters, not match-result cardinality.

All five initial child IDs are zero because `4A6E54 XOR EBP,EBP`, the five parent registration sites each push EBP as ID, and bitmap control +0x6C 0x64F7A0 does **not** emit a parent return event with ID zero. Do not bind a modern click on the 800×87 bottom waiting strip to PMenu. See existing `research/GATE13_PRESULTS_ORIGINAL_BACKGROUND_RETURN_NEGATIVE_AUDIT_RECOVERY443.md`.

New source inventory `reconstruction/original_presults_child_inventory.py` is strict about the unknown dynamic sizes and source-reused original Waiting art identity, declares static display facts with no player return/control behavior; three local tests **PASS** against the actual private original PE and actual private graphics, including **17 original native opcode signatures**, changed-byte/size asset counterexamples, and five child/callback geometry/scope checks. Tests registered on focused Gate13 workflow in WIP branch, no GitHub Actions dispatched before a meaningful integration boundary.

### Whole original user journey remains missing

This source receipt is not a renderer, no original PResults progress event queue is executed, and no original-game GUI or release validation is claimed. Main code `original_game_host.py` currently keeps a Tk spinner/retained PPreMatch frame during calculated Quick3; `human_gameplay.play_original_user_primary_match` has a Quick-only calculation while source-different modes0/1/2 raise without mutating the pending match. Original expected PResults 0x431F70->4A83F0 actual dated work + original 0x4A71F0 event ticks, and original normal return 0x432505+, are **not** modeled by this control inventory.

**Next player-visible integration work**:
1. Prove native PResults +0x250/+0x270 actual dynamic extents and underlying original colors/Font/Resource sources, plus original 0x4A83F0 initialization/0x4A7190 progress update, and render source-qualified PResults child layers in the **ordinary** Tk host (not a separate inspector). Event-driven progress can only come from actual qualified original dated-event callbacks, not synthetic time or match count.
2. Continue normal original `513010→513252→5DA2F0→v38/v3c` first/second side score/event state and original modes 0,1,2,3 with presentation wrapper branch semantics; implement atomic saved live GameState lifecycle, preserve unknown/rejected branches. PResults should release management based on original 0x432505+ route, not guessed click events.
3. Verify physical normal Windows 11 GUI against original behaviors and all shipped countries/leagues and human managers before Gate13 closure and subsequent Gate14–17 audits.

This WIP does not merge PR739 or rewrite canonical main CURRENT_STATE until coherent integration.
