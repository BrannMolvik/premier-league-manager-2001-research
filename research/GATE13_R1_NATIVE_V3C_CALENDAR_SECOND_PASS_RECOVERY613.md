# Recovery613: native rescheduler second owner pass and 0x615D10 signed date-window

**14 October 2026 KST; original SHA verified, static only.** Baseline main `c650b7e31c64f3abbe23077a7cfb3c13855c18a2` after reviewed green PR708 (1,574 Gate13 tests, 128 expected skips, asset policy success). Canonical private `footballmanager.exe`, length 4,714,541, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. It has **not been executed**, and no original bytes are committed. Direct original PE mapping independently verified 13/13 new native opcode snippets listed in optional private-source regression.

## Native 0x5127A0 second-team pass

- The original `0x5127A0` outer loop increments EBX at `0x51292A` and repeats from `0x5127AF` until EBX==2. The first EBX=0 lookup was source-recovered in PR708.
- At **EBX=1**, `0x5127BB` loads its second team/event owner from **the processing owner DWORD+0x5B0**, not the first owner's DWORD+0. `0x5127CC` still reads the first owner DWORD+0 into a different local, `0x5127D2` points the second side row to owner+0x5B4, `0x51280E` points other second-side flags to owner+0x5FC, and `0x512814` reads second-side callback count DWORD+0xB54. Subsequent loops via `0x419490`, `0x4197C0`, `0x41A5B0`, `0x419680` mutate real event/club/team resources; they are **not modeled** here.
- `0x512822` again reloads original global DWORD `0x9847FC`, computes +1, then `0x510300` chooses **the same source-original first/second dated-event collection selector** from the *current reached match+0x0C bit0*, and `0x512838` invokes `0x615D10` with second owner, date+1 and literal arg3=1. The second global date and side data are read **after** the prior first pass's mutable callbacks. The reconstruction must not reuse pre-first-pass owner or cached global date by assumption.

## Native date registry's true 0x615D10 window

- Original `0x615D10` reads the selected collection DWORD+0x00 (pointer to date slot array), DWORD+0x04 (signed number of slots), and DWORD+0x08 (base date index). It computes source 32-bit wrapped **signed** `delta = requested_date - base_date`; at `0x615D22..0x615D24` it compares delta with signed count. When `delta >= count`, it returns EAX=0 immediately. Otherwise it forms first candidate pointer `(slot_array_base + delta*4) & 0xFFFFFFFF`, calls `0x615C50` and may try later date slots until it returns a native event pointer or reaches the end. **Do not represent this as an unconditional successful insertion/reschedule.**
- Crucially, **there is no negative-date lower-bound guard in the source at this entry**. Negative signed delta can form a pointer before the native array. The source-only model faithfully records the attempted negative index as *unsafe/unqualified* without dereferencing it. It also flags a null underlying slot-vector pointer. This matters for preventing Python unsigned sorting/range logic from silently rewriting the original semantics.
- The `0x615C50` predicate and linked native event graph, returned-pointer ownership and all subsequent 0x5127A0 world effects remain unproven here.

## Strict read-only source implementation

`reconstruction/original_native_v3c_calendar_second_pass.py` provides:
1. `source_original_5127a0_second_calendar_request`: requires original source gate and first-pass request receipts from PR708, **actual independently reached EBX=1**, original same native vtable match through+0x0C at second pass, owner bytes through+0xB54 from **after** the first iteration, both team pointers nonnull, and that pass's true global date DWORD. Returns only exact source second owner pointer, date, original first/second calendar identity and layout offsets, without inventing `0x615D10` return or completing the world.
2. `source_original_615d10_calendar_date_window`: accepts the exact source first or second collection address and actual raw collection bytes; computes original signed wrapped date-window check and hypothetical first candidate pointer without dereference or event result; identifies unsafe negative / null vector.
3. `source_original_615d10_reached_request_date_window`: binds that check to an actual typed first- or second-pass receipt so a modern fixture date cannot be substituted for the source requested date.

Tests cover EBX=1 owner+5B0, +5B4/+5FC/+B54, second-pass independently reloaded date, both real collection identities, positive and exclusive end, signed negative and wrapped dates, null source vector, negative signed slot count, malformed or unsupported source owners, and first-/second-pass integration. An optional original executable test verifies 13/13 original opcode signatures. Gate13 focused workflow registered.

**Verification scope:** Source evidence and unit tests do NOT establish actual original completion, correct live GameState calendar mutation, `0x615C50` event selection, replay postponement, `0x512710`/`0x512230` and tail `0x5114B1+` callbacks, or the original 0/1/2 match presentation/PResults/management return. All Gates13–17 OPEN, real Windows11 GUI acceptance absent. This component is read-only source qualification only.

**Next:** exact-head Gate13/asset CI and patch audit before merge. Then recover `0x615C50` actual per-date filter, the source-native calendar event object provenance and remaining 0x5127A0 world effects, integrate an atomic native v3C transaction with real original match state only after producer/callback proof. Continue the missing playable mode-specific calculation, PResults, Save/Load and multiuser/countries; do not mark any gate passed merely from these source tests.
