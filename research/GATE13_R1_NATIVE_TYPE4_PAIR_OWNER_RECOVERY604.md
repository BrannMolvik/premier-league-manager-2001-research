# Gate13 Recovery604: original Type4 SideRef pair-family lookup, bounded WIP

**14 October 2026 KST.** Baseline main `a220e316f02eeb3791436b5d48b4061b21ed04ff` after independently source-reviewed PR696 merged (Gate13 1,455 tests /119 expected private skips, asset policy green). Static source is owner-private original `footballmanager.exe`, **4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**; byte-identical file fetched from private Google Drive and checked locally. No original game process was executed, and no original bytes were committed to Git.

## Exact reached source: Type4 from 0x4F28A0 to 0x4FAF70

PR696 established that real embedded LeagueMatch SideRef virtual+0 is `0x510320`, with uncached (SideRef DWORD+4==0) delegates into `0x4F28A0`, not an unconditional club equality. Its native selector WORD+0x0C type4 dispatches `0x4F2A78`.

On native SideRef+0x08 owner, `0x4F2A7B` invokes original **0x4FAEA0** and **does not continue if AL=0**. This gate is stateful: original 0x4FAEA0 examines owner +0x3C/+0x68, may construct two pair arrays via +0x6C/+0x70, records +0x74/+0x78 and +0x7C/+0x80 and calls original `0x617500`. These arrays cannot be supplied from arbitrary symbolic modern cup fixtures or assumed stable before this gate.

When gate AL=1, `0x4F2A88..0x4F2AA4` splits SideRef WORD+0x0E into the actual original 0x4FAF70 call arguments: **flag0=selector&1**, **flag1=(selector>>1)&1**, **index=selector>>2**. Original `0x4FAF70` reads owner **+0x74 array if flag0=1**, otherwise **+0x7C**, obtains the pair at `index*8`, returns its **first** member pointer if flag1=1, otherwise its **second** member pointer. The returned object is an input SideRef; it is **NOT** yet the final resolved club pointer. Original type4 then constructs/modifies a temporary standalone SideRef with vtable 0x7C4D60, invokes its virtual+0 and writes the final return to embedded SideRef+4 at `0x4F2B2A`. Its real nested getter, mutating owner and registration effects are not yet reconstructed.

Independent private PE check: **19/19** direct control-flow opcode signatures in the source-guard test match native file exactly (0x4F2A78/7B/80/88/91/96/98/9B/A4 and 0x4FAF70/74/78/84/8E/92/94/97/9B/9D), without launching the original. Not all material input owners are proven by this bounded result.

## Staged independent code and tests, not integrated

On branch `worker/gate13-r1-native-type4-pair-owner-604`:

- `reconstruction/original_native_type4_pair_selector.py` only selects the exact *post-gate original SideRef pointer* for supplied owner arrays; requires authenticated Type4 embedded vtable, zero cache, nonzero owner and actual 0x4FAEA0 AL; declines invalid/missing/out-of-bounds native array data.
- `reconstruction/test_original_native_type4_pair_selector.py` checks four flag combinations, index/high selector bits, failed gate without touching arrays, missing owners/typed pointers/caches and the opt-in private native opcode signatures.
- Gate13 workflow registers the new test; **no hosted exact-head CI and no code review for this WIP branch yet**. The independent opcode test was evaluated locally only, not the branch's full Python tests. Do not assert it passes until tested.

**Nothing in this WIP changes the normal game player journey.** The live `PrimaryScheduleShadowState.first_dynamic_conflict_near` still has transitional symbolic `club_refs_conflict` and lacks authentic original post-gate SideRef owner/club pointer identity. Gates 13–17 remain OPEN.

## Next exact source-first action

Trace real producers of Type4 SideRef+0x08 parent League owner and +0x0E selector, owner +0x68/+0x6C/+0x70 pair generation and the `0x617500` mutations, together with original `0x4F2B02..0x4F2B2A` nested temporary SideRef resolution. Build a qualified native-equivalent owner/date/SideRef cache object in the two-calendar runtime before replacing the symbolic v0. If this path remains blocked, continue type1/2/3 owner virtual callback traces and normal NEXT→all modes→PResults→return dependencies. Preserve failures/unknowns rather than mapping synthetic club IDs to raw pointers. Do not open a new PR merely for this individual bounded insight; group a substantive original workflow integration and run exact-head CI/asset checks before merge.
