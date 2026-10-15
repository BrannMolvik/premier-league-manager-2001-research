# Recovery649: native 5DA785 team grid coordinate distance and conditional 5112F0 factor

15 October 2026 KST. Canonical main baseline `d4217b3ae498bc1df2355e2148a221f1a175b6d9`, after reviewed PR758 source inputs. Active source WIP `worker/gate13-r1-native-grid-distance-649`; no PR yet. Shipped owner-authorized original `footballmanager.exe` length 4,714,541, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, **static source only**. No original native execution, no private executable committed.

## Precise original 5DA785..5DA8D9 scoring-distance input

Original `5DA2F0` invokes `5DA785` after the team+134..140/registered-user weighted FPU inputs and match-context+4C encounter selection. It obtains first/source team from ESI and other/source team from saved `[ESP+0x44]` (original opponent selected from match-context+28 getter at `5DA30A`). It reads signed **team+0x20 X coordinate** for each, and signed **team+0x24 Y coordinate** for each. For both axes the original uses native `IDIV 1000` and two optimized signed quotients:
- remainder (signed IDIV1000) multiplied by immediate magic **0x1B4E81B5** in `IMUL`, signed-high shifted six, with sign compensation, is **integer truncation of signed remainder / 600**;
- raw signed coordinate multiplied by immediate magic **0x68DB8BAD**, signed-high shifted twelve, sign correction, is **integer truncation of coordinate / 10000**.

The original native grid-cell coordinate equals the **sum** of those two quotients. The x and y differences between teams are computed in source x86 signed arithmetic and absolute-valued. The original then squares both differences through signed `IMUL`, adds to a signed DWORD, converts via native signed DWORD `FILD`, invokes x87 **FSQRT** and calls native **`668350`**. At 66835F the original flips x87 rounding-control bits via `OR AH,0x0C` and `FISTP QWORD` to **truncate toward zero**, restoring its previous x87 control word. Within a valid nonnegative 31-bit squared-sum domain, this yields Python `math.isqrt(sum)` exactly, not a rounded-to-nearest Euclidean distance.

Negative signed coordinate inputs follow signed truncation, *not* Python `//` floor. Example x= -600 produces cell -1; x= -1000 produces cell0; x= +10600 produces cell2. These are source-defined integer manipulations, not latitude/longitude, screen pixels or fixture scheduling coordinates.

At `5DA885`, original checks native truncated distance:
- **0** -> skip 5112F0 call and multiply two FPU inputs by original 0x7BD8F8 double **1.5**.
- **nonzero**, calls original **5112F0** on native match context; if returned AL true -> original 1.5 branch.
- AL false **and** distance exactly **1** -> original 0x7BD678 double **1.2** multiplier on both FPU inputs.
- AL false with distance greater than1 -> leaves the two FPU inputs unchanged (effective multiplier 1.0).
These factors modify pre-existing FPU match-power inputs; they are **not** a final score or an original RNG value.

The new `original_match_5da785_grid_distance.py` strictly consumes original native two-team pointers and exact team+20/+24 signed records, including independent saved opponent pointer from native `5DA7FB [ESP+44]`; rejects pointer alias, wrong source records, fixed-width coordinate-square overflow (source undefined/unsupported signed FILD sqrt), forged original 5112F0 return, or a 5112F0 return when the original zero-distance branch bypasses it. It returns exact projected grid differences/squared sum/truncated distance and **unexecuted** multiplier decisions, never native score mutation or GameState output.

Unit coverage checks signed positive/negative edge inputs, magic quotient equivalence against independently computed truncating signed divisions including INT32 boundaries, x/y 3-4-5 distance and √18 truncation, original source constants + modifiers, source pointer and overflow errors. Private original PE **17 exact opcode sites and 2 direct calls PASS**, plus original doubles 1.2 and 1.5. These tests are registered in focused Gate13 workflow, but **new module/test exact-head CI is not yet run** on the WIP branch.

## Next concrete original-world dependency, not yet resolved

At `5DA8D9–5DA967`, native `5DA2F0` allocates temporary QWORD output slots, zeros each explicitly, calls **40CBC0** with two QWORD output pointers and actual scoring team context. Then `5DA96C` reads the produced QWORD; if equal to 0.0, it jumps to `5DAC05`. Otherwise `5DA995` builds native 5E43B0 and 5E48D0 source transformations from the other output before reaching score/event callback code. The two outputs from **40CBC0** must be source-mapped and stored to original match-world semantics before classifying an actual score/goal event. Do not treat an integer grid distance or 1.2/1.5 adjustment as the result of original 5DA2F0.

The normal game is still the reconstructed one-human Quick Match with mode0/1/2 explicitly fail-closed. 513010 native match calculation, v38/v3c save updates, 4A7210/6168C0 dual-calendar actual event writers, 432505 original return, true 2–6 human registry, all original leagues and physical Windows11 GUI acceptance are not source-complete. Gate13 and Gates14–17 OPEN. Source-first but prioritize real player-visible integration once 40CBC0 score path qualifies; no micro CI/PR unless this slice forms a coherent reviewed milestone.
