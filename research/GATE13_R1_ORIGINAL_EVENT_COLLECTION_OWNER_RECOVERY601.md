# Gate 13 Recovery601: original 0x4F3B50 schedule event owner-selection source

**14 October 2026 KST.** Baseline main `2ffb230e454b97d464c919e75f2626253a1a18c9`, verified merged PR687 (original 0x510380 event ctor). Feature branch `worker/gate13-r1-original-event-collection-owner-601`; Gates 13–17 OPEN. Canonical original source `footballmanager.exe` was directly byte-retrieved again from Daniel's verified private extracted Google Drive source (file ID `1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q`) to the private worker container, 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. The original executable was **never launched**; only original PE bytes inspected statically using GNU objdump and a Python RVA/section reader. No proprietary binary is included in this branch.

## Exact native source chain

- `0x5103D0` takes the original schedule owner argument from stack at `0x5103D3`, puts it in ECX `0x5103D9`, calls `0x4F3B50` at `0x5103DB`, then pushes returned EAX and calls base ScheduleEvent constructor `0x510380` at `0x5103E3`.
- `0x4F3B50` reads original owner vtable at +0 and calls virtual **+0x30** at `0x4F3B52`. Crucially the source uses `test al,al` at `0x4F3B55`, **not** `test eax,eax`. Its nonzero low8 chooses original secondary collection `0x947AF0`; zero low8 chooses original primary collection `0x947AD8`. Both selections are unconditional return of literal pointers, with no club, competition-kind, fixture-ID or visible-date inference.
- The proven original `0x510380` then reads **the selected collection's own** DWORD+0x0C serial, assigns event+0x0C = `((serial << 1) | secondary_bit) mod 2^32`, and increments that same counter. These *two distinct* source owners do not become one collection just because a reconstructed fixture calendar has a single array.
- Independently checked **13/13 exact opcode spans** across `0x4F3B50` and `0x5103D0` against the fresh owner-approved PE; read was local static evidence, not proof of a running original schedule.

## Source code/verification

Existing `reconstruction/original_schedule_event_native_constructor.py` now exposes `source_original_event_collection_selector_4f3b50` and `source_original_event_constructor_from_owner_5103d0`. They accept explicitly qualified original virtual-result EAX; `EAX=0x100` or `0x80000000` selects the primary (AL=0), whereas `EAX=0x101` selects secondary. A source-only combined receipt feeds the already verified constructor, requiring only the selected original collection counter. Strict type/overflow invalid inputs fail closed. Source tests extend `reconstruction/test_original_schedule_event_native_constructor.py`, with opt-in original PE opcode sites.

**Still unknown:** Native owner-class vtable+0x30 implementations and actual virtual result per reconstructable `PrimaryScheduleShadowEntry`; real original two-list materialization/loaded-event lifetime; whether both collections exist in the clean-room world; full per-event virtual+0x0C/+0x10/+0x18 and +8/+0x44 flags. No source permits choosing a collection from `node_kind`, assigned competition, cached teams, or a Python object identity. This source stage DOES NOT produce a playable NEXT/PPreMatch/FastView/PResults loop, a real event runner, world mutation, a GUI, or a Windows11 acceptance receipt.

**Next executable source task:** enumerate owner vtable+0x30 implementations and their original producer/object families, then map authenticated source owner identities to `0x947AD8/0x947AF0` native nodes and only then integrate the native two-pass `0x6168C0` and match virtual+0x10 `0x513010` semantics through real player-visible stages. Keep the normal host mode2 fail-closed until authentic modal/world-writeback and management return are implemented. All Gates13–17 remain OPEN.

## Native LeagueMatch subtype callback partition, exact original file inspection

The seven previously authenticated LeagueMatch vtables now have independently verified native **+0x28 (kind), +0x30 (date collection decision), +0x34 (match-context preparation), +0x38/+0x3C (subsequent processing), +0x44 (other owner)** pointers. Source was read directly from the original read-only `.rdata` (not current reconstruction assumptions):

| Native vtable | +0x28 kind callback | +0x30 collection callback | +0x34 prepare callback | +0x38 | +0x3C |
| --- | --- | --- | --- | --- | --- |
| `0x7C4C24` | `0x651E20` | `0x651980` | `0x510D60` | `0x5112A0` | `0x5132E0` |
| `0x7C4CE4` | `0x668766` | `0x651980` | `0x510D60` | `0x5112A0` | `0x511370` |
| `0x7C9D9C` | `0x6CE1E0` | `0x5112C0` | `0x511120` | `0x5136C0` | `0x5136E0` |
| `0x7C9E14` | `0x650250` | `0x651980` | `0x510D60` | `0x5112A0` | `0x511370` |
| `0x7C9E80` | `0x6CE1F0` | `0x5112C0` | `0x511120` | `0x5136C0` | `0x5136E0` |
| `0x7C9EF8` | `0x6CECB0` | `0x5112C0` | `0x511120` | `0x5136C0` | `0x5136E0` |
| `0x7C9F70` | `0x650010` | `0x5112C0` | `0x511120` | `0x5136C0` | `0x5136E0` |

All seven still use +0x10=`0x513010`, +0x18=`0x6559A0` (payload=self); +0x0C is common `0x510AD0` except the special `0x7C9F70` vtable's `0x510B00`. The +0x44 method is `0x513F70` for the three direct class variants and `0x514000` for the four wrapped variants. Do not interpret addresses as functionally interchangeable.

Original `0x651980` is exactly `xor al,al; ret`, so the three direct classes' +0x30 owner returns low byte zero without reading vft+0x28. Original `0x5112C0` checks actual vft+0x28 kind against numeric **2** and original match byte+0x44 bit **0x04**: AL=1 only when kind==2 and bit2 clear; otherwise AL=0. Passing this AL to actual `0x4F3B50` selects the secondary collection only on success, primary otherwise. **This only applies when the object passed to `0x4F3B50` is genuinely that original native LeagueMatch object**. Existing `PrimaryScheduleShadowEntry` is not yet source-equivalent to an instantiated native match object. No automatic migration of shadow entries is approved.

Original `0x513010` around `0x5130AE..0x5130C7` obtains the match's own vtable and invokes **+0x34** with the locally allocated match-processing context; it tests returned AL. Three vtables use `0x510D60` directly. Four use **`0x511120`**, which first invokes the same `0x510D60` and stores its AL, then ALWAYS calls vtable+0x28. If kind==5 the wrapper calls `0x513E80` and `0x513E70` on the original match+0x54 owner and writes their returned DWORDs to context+0xD28 and +0xD2C **regardless of 0x510D60 return**. Only when stored AL was nonzero does it additionally copy native match DWORD+0x50 to context+0xD24. The wrapper returns that earlier stored AL. Missing owner bytes/results must stay UNKNOWN, not zero-defaulted. Native `0x510D60` itself mutates many further fields; this source-only receipt intentionally excludes and cannot substitute its full execution.

Code `reconstruction/original_leaguematch_native_process_owners.py` records the exact seven native method pointers and strict source read-only dispatch, `source_original_leaguematch_native_virtual30_low_byte`, source-joined `0x4F3B50` selected collection only from authentic record, and `source_original_wrapped_prepare_511120_post_base` for additional source writes only. `reconstruction/test_original_leaguematch_native_process_owners.py` exercises 7 vtables, caller reachability, conditional +0x30, bit2 / kind and +0x34 wrapper writes; private original PE checks assert all seven method table entries and **31/31** direct opcode bytes verified in the private worker before review. New paths registered in focused Gate13 workflow. Unknown original subclass production and full native callback invocation remain unresolved.

**Next player-visible dependency:** trace original source producer/owner `0x5103D0` input for a real `PrimaryScheduleShadowEntry`, distinguish fresh vs loaded event+8 and full native+0x44 lifetime, integrate an actual native event callback chain `0x513010` through mode selection, genuine world-writeback and PResults+normal management return. No Win11 original executable launch or GUI acceptance. Gate13–17 OPEN.
