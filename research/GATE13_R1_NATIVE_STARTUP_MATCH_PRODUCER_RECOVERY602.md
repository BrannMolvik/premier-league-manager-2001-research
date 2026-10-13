# Gate 13 Recovery602: original startup match constructor class provenance into actual symbolic schedule factories

**14 October 2026 KST.** Recovered canonical baseline main `7740c152996055460cd942299f8345cd4b73a128`, after PR #690 exact-head Gate13 1,401 tests / 112 expected private skips and green asset policy. Existing branch `worker/gate13-r1-native-startup-match-producer-602` was found already created at baseline main but empty (no duplicated branch or restart). Owner-authorized original `footballmanager.exe` at private Drive source was independently hash-checked in local execution runtime, 4,714,541 bytes and SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. The source EXE was inspected **statically only** with `objdump -d -M intel`, never executed, and no proprietary bytes were committed.

## Recovered direct native emitter constructor callsites

The existing `reconstruction/competition_schedule.py` already models original startup per-round materialization. Its `StartupScheduleNode.node_kind` strings were not proof of a real original native runtime event vtable; the branch now attaches a separate, immutable source-proven constructor-class receipt only where the **actual original creator and its reached constructor call** have been identified:

| Original direct producer | Original constructor callsite | Target | Verified final vtable / original saved-event type | Existing factory |
| --- | --- | --- | --- | --- |
| `0x6173D0` fixed real fixture traversal | `0x617490` | `0x5104F0` | `0x7C4C24` / type1 | fixed_league_match |
| `0x4F64D0` single-leg Cup round | `0x4F66C9` | `0x510520` | `0x7C9D9C` / type2 | cup_match |
| `0x4F6820` two-leg Cup first leg | `0x4F6A02` | `0x510640` | `0x7C9EF8` / type4 | first_leg_match |
| `0x4F6820` two-leg Cup second leg | `0x4F6A64` | `0x510680` | `0x7C9F70` / type5 | second_leg_match |
| `0x4FAC60` Scottish split | `0x4FADBE` OR `0x4FAE30` | both `0x5104F0` | `0x7C4C24` / type1 | scot_split_league_match |

Original `0x6170F0` **generates procedural pairing/order/source events but contains no direct `0x5104F0` call itself** in its read-only disassembly. The prior broad phrase "0x6170F0 league constructor" is insufficient proof of each Python-emitted procedural `league_match` becoming one authenticated native `0x7C4C24` object. The existing procedural factory therefore **deliberately receives NO original class receipt**, rather than blindly applying fixed League type1. A separate original producer/consumer trace must establish which function eventually materializes such procedural pairs as actual events.

Constructor calls were verified by directly inspecting original code at the six native callsites, and the class vtable stores at `0x51050E,0x51054D,0x51066B,0x5106B3` corroborate previous PR689 original serialization type-to-vtable signatures. The explicit original executable test suite checks these bytes when owner-private `FM2001_ORIGINAL_EXE` is supplied; hosted CI skips private binary reads. For Scottish split, code deliberately records producer `0x4FAC60` but no particular selected callsite because the two original branches both construct the same native type; selecting the wrong specific branch would exceed evidence.

## Integrating into the existing reconstruction without a fake match instance

- `reconstruction/original_native_schedule_producer_source.py`: strict `source_original_schedule_constructor_for_verified_producer` checks original producer+callsite and original saved loader's class contract. Returns immutable source constructor/type/vtable evidence; explicitly **not** a live original object.
- `reconstruction/competition_schedule.py`: optional `StartupScheduleNode.original_native_constructor_evidence` emitted by authenticated fixed League, one-leg Cup, both two-leg roles and Scottish split factories. The generic procedural League schedule continues with `None`. Existing dates, pairings, teams, token identities, RNG and dynamic execution are unchanged.
- `reconstruction/test_original_native_schedule_producer_source.py` and existing `test_competition_schedule.py`: exact five class families; Scottish dual site; reject missing or mismatched producer/callsite; no automatic conversion of generic procedural pair outputs; require the normal factory to attach authenticated class metadata only where source proven. Gate13 workflow paths and test module added.

**Critical unfinished source/acceptance boundary:** `original_native_constructor_evidence` is only a class receipt attached to startup symbolic emissions. It is NOT original native event+0x0C ID, two-container source registry assignment, actual live +8 link pointer, post-callback full +0x44 flags, original v+0x0C/+0x18 eligibility, 0x513010 match execution, source PResults ticking, normal player-visible GUI, original modes0/1/2/3, all competition countries/leagues, SaveLoad or Win11 acceptance. It is intentionally **not persisted into PrimaryScheduleShadow as if it were a live original object** until the object producer/lifetime and actual event IDs are source-qualified. No widening of normal host Quick-only guard. Gates 13–17 remain OPEN.

**Next:** verify fresh exact-head Gate13 and asset CI/privacy and review this coherent source/factory integration. Source-trace the actual original `0x6170F0` procedural pair producer into concrete native match constructors and original `0x615950` date insertion, then stage *actual* authenticated dual-date/event/registry state through original NEXT→PPreMatch→all match modes→PResults→management return. Never fabricate event identity/flags from class type alone.
