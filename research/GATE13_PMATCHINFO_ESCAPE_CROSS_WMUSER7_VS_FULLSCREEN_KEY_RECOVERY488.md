# Recovery 488 — PMatchInfo cross and Escape must send native event 7, not exit fullscreen

_10 October 2026 KST. Independent original-executable re-verification and current-host fidelity audit. Research only. Canonical starting main `d80db2ff4f16bc4b989c2388545d8016ba357677`; Codex implementation last observed `e166ae4d70c32b41f8dcef86b3d3d42b19a24262`. No game code/tests, original binary, licensed assets, saves, CI, release, Windows GUI, merge, or gate status was modified by this worker._

## New private-source recovery and independent source receipt

The authorized private source was **actually recovered in this recovery**, after repeated earlier ephemeral container `caas.internal.errors.ClientError` episodes. The existing workspace contained the user-authorized 511,121,336-byte `The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`, containing a 631,627,248-byte 2352-byte-sector `famg2001.bin`. Joliet volume descriptor sector17 (`CD001`, `%/E` escape) maps root `/footballmanager.exe` to **ISO LBA260425**, length **4,714,541 bytes**. Reading each MODE1/2352 data sector at physical byte `(LBA+i)*2352+16` recovered the root executable in the **private** `/mnt/data/fm2001_private/` directory. Fresh SHA256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

This exactly matches the historical canonical original. No licensed executable, raw disc or private extraction output was committed. This proves original **source bytes are available to the audit worker again**, unlike Recoveries470–487. It does **not** prove the original game can be started or interacted with under Windows11; the container is Linux.

Using `objdump -d -M intel` on the freshly rehashed root PE, source disassembly directly reconfirms prior historical `research/GATE13_PMATCHINFO_RESOURCES.md` (PMatchInfo tab and exit interaction):

| Exact PE address / bytes | Independently observed source action |
|---|---|
| `0x488C45: 83 78 20 07` | `cmp DWORD PTR [eax+0x20], 7`: non-tab `PMatchInfo` control source ID7 (cross) |
| `0x488C4B: 6A 07`, `0x488C4D: E8 9E AD 1C 00` | Cross pushes7 and calls `0x6539F0` |
| `0x488C60: 66 83 7C 24 08 1B` | PMatchInfo keyboard virtual compares its 16-bit argument with `0x1B` (Escape) |
| `0x488C68: 6A 07`, `0x488C6A: E8 81 AD 1C 00` | Escape independently pushes **the same event7** to **the same helper0x6539F0** |
| `0x6539F0..0x653A09` | Masks event to16 bits, dereferences original owner `this+0x64`, pushes `lParam=0,wParam=7,message=0x400` and calls `0x659650` |
| `0x659650..0x659669` | Resolves owner HWND at `owner+0x04` and calls import `[0x7BD2D8]`, historically typed to Windows `PostMessageA`; returns immediately |

**Source level grade:** exact same-handler Escape/cross event7 and WM_USER `0x400` sender tuple **INDEPENDENTLY SOURCE-VERIFIED THIS TURN**. Previous report also source-types the PMatchInfo cross control as `fmCrossButton` at `+0x17D8` and its three other tabs as event IDs1/2/3. The *receiver's* full application-event7 return, stack removal, focus and positioning after post remains conditional/unverified in this new disassembly; do not equate post success with a complete visible modal close without the receiver and Windows acceptance.

## Current ordinary host (same unchanged post-PR562 code)

`reconstruction/original_game_host.py` blob `89d12efc30f7ba02a7933b2e5fbdf2682fd90051`:

1. `OriginalGameTkHost.__init__` ~line520 registers the **global** root `<Escape>` callback to **`leave_fullscreen`**, not a conditional active-PMatchInfo input receiver. `leave_fullscreen` ~645–655 invokes `_set_fullscreen(False)` when fullscreen; only during startup media does it forward WM_KEYDOWN Escape to the native startup child. No active PMatchInfo, source event7, `0x6539F0` or dialog-owner branch appears.
2. When real right-press opens source-qualified `PMatchInfo` from a captured fixture report, `active_pmatchinfo_art` is retained, rendered and gives the popup ordinary input ownership. `on_click` around 2415–2443 explicitly refuses general popup pointer interaction **except the selected report-script scroll arrow**. The original cross button therefore has no normal source ID7 hit/callback. Even if `active_pmatchinfo_art` is valid, clicking its source cross currently follows the generic `PMatchInfo pointer interaction remains fail-closed` status.
3. There *is* a public/internal `apply_source_accepted_pmatchinfo_exit` (~2266–2275) that drops `active_pmatchinfo_art`, clears context/action and redraws. It is explicitly a **post-source-acceptance helper**, not a keyboard or source control binding. A repository-wide scan of the host finds only its definition, not normal pointer/Escape callers. This helper provides possible integration reuse but cannot be cited as current playable close behavior.
4. Consequently, with a qualified popup active, ordinary **Escape can leave fullscreen but does not close PMatchInfo**, and ordinary **cross button cannot dispatch its original event7**. On the next Escape, fullscreen is already off, so its ordinary callback is an inert break. This is a **CODE-CONFIRMED missing/wrong popup input/return path**, independent of the previously established Inbox `PEAMMessage` *different* Escape result16, and independent of the Squad player right-press finding in the other Recovery488 report.

## Codex-only original-first corrective and acceptance matrix

1. Route keyboard Escape by **actual modal/panel owner first**: with a source-valid `PMatchInfo` active, emit the original **event7 `WM_USER(0x400),wParam7,lParam0` equivalent** under the correct source owner/stack. Only after a qualified receiver/return result may a modern Tk adapter close its popup. Outside PMatchInfo preserve original-context Escape semantics; a blanket `leave_fullscreen` binding is not source-native game UI behavior and must not take precedence over an original modal.
2. Recover cross-button sprite/control owner and **exact pointer rectangle**, native enabled flags and source event handler `0x488B70`; wire accepted childID7 through the same qualified dialog close path as Escape. Do not invent a generic close area or allow closing by clicking any background art. Preserve PMatchInfo tab1–3 and qualified Fixtures right-press report owner.
3. Preserve focus/stack and report-context identity. Test both Escape and cross from all three original tabs; check modal is removed **once**, scripts/scroll state and underlying fixtures remain valid, no second native event is processed after exit, and the input does not escape fullscreen or activate unrelated underlying Squad/Menu/NEXT.
4. Regression outcomes require original source event trace, headless host/Tk 1× and1.5× pointer/key, and a **real Windows11 normal user path** (TeamSelect→Fixtures→captured match report→PMatchInfo→Escape/cross→Fixtures). If no authentic captured report exists yet, fail closed; don't fake a match report to make UI tests pass. Keep source item/progress and proprietary original save semantics separate.
5. Also preserve other dialogs' **distinct** source keyboard effects; specifically `PEAMMessage` Escape→result16 is *not* PMatchInfo's event7, and PPreMatch/PResults must retain their own native modal stack. Cross-screen key handling must not be one global modern shortcut.

**Classification:** PMatchInfo Escape/cross source event **CONFIRMED through NEW private original PE disassembly**; Tk key/popup missing route **CONFIRMED code-level**; actual native receiving window event7 exit behavior **PARTIAL**; physical Windows11 interaction **NOT ACCEPTED/NOT OBSERVED**. Correcting this does not close original Match Info visuals or complete normal career gameplay. **Codex sole implementer, `worker_role=audit_only`, `implementation_allowed=false`; Gate13 OPEN, Gates14–17 and full original-scope verified Windows11 release incomplete.**
