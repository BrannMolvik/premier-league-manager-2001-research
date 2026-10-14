# Gate 13 R1 recovery 634: original 510D60 match event-counter source prefix

15 October 2026 KST. Source-only verification on canonical original private `footballmanager.exe`, length 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. The executable was statically inspected, never run and never committed to Git. This is an extension of the existing original LeagueMatch vtable/virtual+34 fidelity audit. **No original native callback, calculation, match rendering, PResults, or GameState transition has executed.**

## Exact original-native control/owner evidence

The known seven LeagueMatch vtables include a virtual+0x34 owner of original `510D60` for three classes, and `511120` for four. Original `511120` first calls `510D60` at `51112A`, then may execute its class-specific supplemental `+D24/+D28/+D2C` writes. At `510D95/510D9B`, the base method separately caches original raw global mode `877530` into processing context DWORD `+D3C`. Mode cache does **not** prove the later `51325D` outer presentation decision occurred.

The base `510D60` calls its match vtable+0x28 **twice** (at `510DBF` and `510DEC`), each to derive a different context counter. Six original vtable+0x28 methods are independent and confirmed trivial `mov eax,N; ret`; the same kind is therefore source-stable for those six in both calls:

| Original match vtable | vtable+0x28 implementation | Literal kind |
| --- | --- | ---: |
| `7C4C24` | `651E20` | 1 |
| `7C9D9C` | `6CE1E0` | 2 |
| `7C9E14` | `650250` | 6 |
| `7C9E80` | `6CE1F0` | 3 |
| `7C9EF8` | `6CECB0` | 4 |
| `7C9F70` | `650010` | 5 |

**Exceptional seventh class:** `7C4CE4` uses v+0x28 `668766`, which pushes 0x19 and calls diagnostic `66ABCF` rather than returning a numeric literal. The complete runtime outcome is not established, so neither an invented kind nor an assumed safe continuation is allowed. The source-only projector rejects this class.

## Both context counter predicates, source-only

From `510DC2..510DE7`, first context DWORD `+D0C`:

- If first native kind is **2** AND match DWORD `+44` bit `0x04` is **clear**: store `0`.
- Otherwise: store `(match+44 >> 1) & 1`.

From `510DEF..510E15`, second context DWORD `+D10`:

- If second native kind is **3** AND match DWORD `+44` bit `0x04` is **clear**: store `1`.
- Otherwise: store `(match+44 >> 2) & 1`.

These two writes are **not** the whole original `510D60` transaction: it also resolves native side data, initializes arrays, writes `+D14/+D18/+D1C/+D20/+D24/+D28/+D2C/+D3C`, later performs other operations, and returns a native AL outcome. No implication that this source prefix completed a real match is allowed. The existing `original_native_match_v3c_entry.py` zero-event v38→v3c receipt can use actual reached `+D0C/+D10` **only after** qualifying the entire original context and callback path, never from these projected values alone.

`reconstruction/original_leaguematch_native_process_owners.py` adds a strict immutable `source_original_510d60_two_event_counter_writes` receipt for just these two proven writes, validates an actual native vtable and reached match+44 flag bytes, and rejects unqualified 668766 and forged/short records. Tests cover all six classes over flag patterns, exceptional/non-native owners, strict types and 24 additional optional original PE opcode/constant signatures. The private original 24 sites matched independently, but the Python branch tests must still be executed and reviewed before PR/merge.

## Functional boundary and next source-backed player journey

Real `513010` NEXT match progression cannot publish a score simply because virtual+34 prepared two counters: after native +34 AL and `516080`, it may call `5DA2F0` for the original first-side owner (source mutable world), conditionally opens 3D/FastView/Quick mode UI and invokes virtual+38/+3C including scorer/event and calendar changes. The original PResults progress cardinality, injury pending events, and live registered-user Inbox cannot be inferred from this source receipt. Next reconcile actual 510D60 source context, 5DA2F0 pre-presentation mutations and verified post callbacks in a staged transactional saved world and ordinary all-mode play. All original leagues, 2-6 humans, Gate13 and Gates14–17 including genuine Windows11 GUI release audit remain OPEN.
