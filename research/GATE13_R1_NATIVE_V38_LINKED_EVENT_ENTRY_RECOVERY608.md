# Recovery608: original 0x513570 nonzero linked-event entry (Gate13 OPEN)

Baseline main `30dc2e89f2f216e1d447f1e05b857af41cb876df` after fully reviewed green PR703. Static verified private source original PE SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; did not run original executable or embed bytes.

Direct `objdump -d -M intel --start-address=0x513570 --stop-address=0x5136c0` independently confirms:
- `0x513577` reads source match context +D0C; `0x513583` checks +D10 only if first is zero; both zero jump direct to 0x5136B6.
- Nonzero either count: `0x513591` reads +B60 linked event pointer. Primary count nonzero and head nonzero starts original predicate `0x6326B0`; walks event+34 until predicate passes, then sequential `0x632680`, `0x6326E0`, `0x632940` and conditionally increments match +58 or +59 by event+4 pointer; source signed bytes +58/+59 subtract from match WORD+3C/+3E.
- Primary count zero and event head nonzero starts `0x6326E0`, walks +34 until predicate passes (or null). Secondary count nonzero and surviving current event pointer invokes `0x632940`, conditionally increments match+5A/+5B, unless event+28 ==7.
- Match byte+44 bit2 gates continuation; source compares virtual helper results 0x513F00/0x513ED0 and optional event+0xD14 getter equalities before source `0x64D540(2)` can increment +5A/+5B. This is **real mutable scoring logic**, not a generic event completion.

New source-only model `reconstruction/original_native_v38_linked_event_source.py` reads actual supplied context bytes at +D0C/+D10/+B60, classifies its first reachable callback branch, and refuses to claim event callback interpretation or native match completion. Negative tests cover invalid owner, zero counters/no dereference, primary/secondary and null event head; registered in focused Gate13. This deliberately does not execute guessed 0x6326B0/680/6E0/940 callback semantics. The reconstructed live game remains behind this source qualification boundary.

**NEXT:** Source-prove the exact 0x6326B0, 0x632680, 0x6326E0, 0x632940 predicates and 0x513570 event+34 chain list ownership/world effects; validate with actual source event structs and reachable match values, extend negative tests and integrate typed native world writes only when original callback effects are proved. Then complete v3C rescheduler 0x511370→0x5127A0/0x615D10, full 0/1/2 match modes, PResults/management return, all Gates 13–17 and real Windows11 GUI acceptance. **Tests/PR/CI not yet green; no gate closure.**
