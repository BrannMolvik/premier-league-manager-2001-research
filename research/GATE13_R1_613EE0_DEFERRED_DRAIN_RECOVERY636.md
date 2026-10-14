# Gate 13 recovery 636: original deferred 614080 queue processing

15 October 2026 KST; main 50b19e2bd74b790dd55557bb317a3f67dff0f7ab following reviewed PR735. Source: private original footballmanager.exe, 4,714,541 B, SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. This worker rehashed and statically disassembled the original code, never launched original game or committed proprietary bytes.

## Material correction to PR735 original 613EE0 source contract

Previous original_native_613ee0_pending_list.py called header+0x10 a "pending cursor" and reset it after due processing. Actual 0x613EE0 at 0x613EE5 sets queue header+0xC=1 and +0x10=0, scans pending nodes and source vtable+0x10 callbacks, then at 0x613F30 clears active+0xC. Crucially 0x613F37 tests +0x10; if nonzero, 0x613F40 CALLS 0x614080 before 0x613F45 clears +0x10. 0x614080 invoked while +0xC active sets +0x10=1 and returns immediately, not a cursor advance. This is a **deferred reentrant drain request**, and cannot be silently cleared in a port. 0x614080 invoked when inactive iterates the queue, calling event vft+4 and +0x18, and conditionally 0x4EA190 unlink. Later original 0x5CF990 processes per-user+0x6B4 **retention/expiry**, not new Inbox delivery.

Independently checked original vtables: 0x7D7760 vft+4 AND +0x18 point to 0x4093E0 (MOV EAX,1; RET), so one native dated player-event entry is retained by inactive 614080. 0x7BD564 vft+4 is 0x40DFB0 (returns0); +0x18 is 0x404610, which jumps to referenced payload object's virtual+0x24. A zero reached payload result causes 4EA190 wrapper removal; nonzero retains. Without the **actual separately reached payload virtual result**, no safe source outcome is claimed.

## Branch changes and status

- Corrected original_native_613ee0_pending_list.py: a due callback now requires explicit reached queue+0x10 deferred flag; if nonzero, it fails closed until the subsequent native 614080 drain can be source-qualified, instead of inventing an empty/clean queue. Its former source "cursor" description is corrected. Future no-callback path cannot claim deferred due work.
- Added original_native_614080_deferred_drain.py: read-only typed original active-flag/deferred source and inactive empty/one-node 7D7760 or 7BD564 vtable+4/+18 source outcome; requires queue/event ownership and independently reached 7BD564 payload result. No native dispatch, heap free, real queue removal or GameState write.
- Added test_original_native_614080_deferred_drain.py and extended test_original_native_613ee0_pending_list.py: active deferral, idle event vtable retention/removal, future/due strict owner and flags, exact native vtable addresses and PE opcode signatures checked on private original. Gate13 focused workflow extended.
- Source-only and hosted exact-head Gate13/asset-policy not yet verified or PR merged at staging. No gameplay, original Inbox delivery or Win11 GUI acceptance inferred.

This correction is important but DOES NOT finish global 947AA8 multi-node processing, original 5CFA20/413020 recipient delivery, saveable GameState event world, real NEXT→PPreMatch modes0–3→PResults→management return, all leagues/countries/multihuman, Gates 13–17 or physical Windows11 release audit. Next source-backed work: qualify pending→per-human manager delivery and real atomic save/restore, avoiding source-only receipt churn.
