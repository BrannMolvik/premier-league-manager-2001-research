# Gate13 Recovery601: original serialized event loader type-to-native-class source

**14 October 2026 KST.** Baseline main `733a7f3e194eb95376552c8c663b64252a4a655d` after reviewed, green PR688. Source owner: privately connected original disc-root `footballmanager.exe` (4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`), **statical disassembly only** with `objdump -d -M intel` and direct PE section bytes. No game launch or original binary added to Git.

## Loaded native event family, independently source verified

At native `0x616100`, original serial event discriminator DWORD is loaded via `0x667E90`; source control flow distinguishes zero `0x616145`, one `0x6161F7`, six `0x616235`, and unsigned range 2–5 through `0x6162A7..0x6162B3` and jump table at `0x6163D0`, containing exactly `0x6162BA,0x6162FF,0x616339,0x616370`. **This is the ORIGINAL serialized discriminator, not the reconstruction's Python `node_kind` enum.**

| Original serialized DWORD | Original allocation bytes | Constructor called at source branch | Resulting original vtable |
| --- | ---: | --- | --- |
| 0 | `0x1C` | `0x6161A0→0x510380` then direct additional writes | `0x7C9FE8` (NOT one of seven LeagueMatch classes) |
| 1 | `0x50` | `0x61622B→0x5104F0` | `0x7C4C24` |
| 2 | `0x5C` | `0x6162F5→0x510520` | `0x7C9D9C` |
| 3 | `0x5C` | `0x616332→0x510600` | `0x7C9E80` |
| 4 | `0x5C` | `0x616369→0x510640` | `0x7C9EF8` |
| 5 | `0x5C` | `0x6163A1→0x510680` | `0x7C9F70` (special pre-count v+0x0C) |
| 6 | `0x50` | `0x616265→0x5105D0` | `0x7C9E14` |

Actual loaded type fields outside 0–6 take the different source `0x6163AC` path, whose object semantics are not proven; do not assign them an inferred native class or silently ignore. Type0 is **not** an original LeagueMatch according to the seven authenticated table vtables. The seventh known LeagueMatch `0x7C4CE4` is created by another producer and does NOT follow from these type0–6 loader branches. All 6 loaded match classes call the original `0x510380` base event constructor through native wrappers, and source 0 fresh vtable is `0x7C9FE8` after its own base constructor.

Native `0x6163E0` reads a source count via `0x667E90`, invokes `0x616100` once per loaded item, links returned original native event objects in the same order via object+0x04, and terminates last next pointer at NULL (`0x616434`). Source `0x616100` after constructing an event uses its native event+0x0C identifier (arithmetic shift right1) to place its pointer into a parent array (`0x6163B0..0x6163BD`). This establishes a concrete native loader/list owner and a source event-ID registration path, not an automatic link from every reconstructed fixture to a native event.

## Important qualification about native event+8

Previous source constructor proof `0x510380` writes new event+8=0; `0x616100` runs that constructor through type0–6 native chains. This authenticates **immediate post-construction** zero for the bounded class path, but does **not** prove that any later game event at time of PResults is still zero, nor that source virtual+0x0C succeeds, payload+0x44 filter bit6 clears, nor that the original world/mode effects have happened. Original `0x6168C0` deliberately re-reads event+8/flags dynamically and must not be fed static constructors as simulated live values.

## Branch artifacts and continuation

`reconstruction/original_native_serialized_event_loader.py` preserves source type0–6 → allocation/constructor/vtable/callsite as read-only typed metadata, strict unknown inputs raise. `reconstruction/test_original_native_serialized_event_loader.py` asserts six original LeagueMatch classes vs type0 separate, unknown fallback, exact original opcode sites and 2..5 jump-table (private PE opt-in); **20/20 source opcode bytes and all jump-table words independently checked locally**. This does not parse actual original saved bytes, supply live original event objects, assign `PrimaryScheduleShadowEntry.node_kind`, or load any file to the reconstructed runtime. Source type0–6 is a branch-level bound only.

**Next source task:** Identify the original serialized record provenance and creation/restore call chain for `0x6163E0/0x616100`; establish original active-date bucket ownership, original loaded event state after initialization, and a verifiable mapping to the reconstructed primary/secondary runtime objects. Then integrate the authenticated `0x513010` event/callback and `0x6168C0` PResults runner into actual NEXT/PPreMatch/Match/PResults/return. Gate13–17 OPEN, no Windows11 GUI acceptance.
