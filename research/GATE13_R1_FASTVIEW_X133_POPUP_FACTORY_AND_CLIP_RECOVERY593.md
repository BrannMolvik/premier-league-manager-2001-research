# Recovery593: native FastView x133 popup factory and clip

**14 October 2026 KST.** Source investigation WIP, Gate13 through Gate17 OPEN. Base main `98875edfe30486fa4b2c1f4ef59438bc4b96e0bd` after verified PR669. Feature branch `worker/gate13-r1-fastview-popup-clip-source-593`.

Owner-authorized private source: original `footballmanager.exe` 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; original byte identity independently confirmed again on 14 October. Static objdump original PE32 inspection only. No original executable launch, original mouse observation, reconstructed GUI acceptance, or Windows11 release claim.

## Original owner, actual source and effects

Prior merged PR669 source proved x133 child array `screen+0x263C+0x44*row`, native vtable `0x7CB010`, virtual +0x98=`0x52D120` and +0x9C=`0x52D190`. Recovery593 directly rechecked the original disassembly:

- Native `0x52D120` requests 0x18C-byte memory via `0x668140`, and if nonnull passes `[child+0x38]` original list owner into `0x52D1F0`; if allocation fails returns null. This is factory allocation, NOT popup activation, current selection or screen coordinates.
- Native `0x52D1F0` invokes `0x448310` base constructor, retains supplied list pointer at newly allocated popup +0x68, zeroes 25 DWORDs at +0x7C, initializes control fields and children at +0x10C and +0x13C. Neither text choice nor pointer event belongs to this evidence alone.
- Native child virtual+0x9C `0x52D190` reads parent through `[child+0x24]`. Its first value is `[child+0x10]+[parent+0x0C]`, its second `[child+0x0C]+[parent+0x10]`. It reads clip context offsets +0x70 (x origin) and +0x74 (y origin). It caps the first sum only on `origin_x+width>800`, setting `width=800-origin_x`; similarly caps the second only for `origin_y+height>600`, setting `height=600-origin_y`. It passes six arguments `(width,height,origin_x,origin_y,4,1)` to `0x653320`. This routine is a source drawing clip; it does not independently establish native popup hit testing, click acceptance, or option selection. It does not show a negative/left/top clamp.

Read-only strict signed input projection `source_fastview_x133_popup_clip_52d190` added to `reconstruction/original_fastview_tactics_selection.py`, alongside deterministic cases, boundary counterexamples and private original PE instruction-site checks in `reconstruction/test_original_fastview_tactics_selection.py`. These tests have NOT run on this WIP branch and CI is not claimed. Original static objdump checked the factory and clip bodies. No original proprietary binary committed.

## Next exact source task

Source-qualify popup `0x52D1F0` nested child controls, actual pointer and 0x651AC0 source selection index through the x133 modal, then the actual two-sided once-only mode2 edit transaction, original match calculation, PResults, and normal management return. Audit actual Windows 11 GUI separately; original multi-human, countries/leagues, saves and Gates13–17 remain incomplete. Preserve WIP feature branch and milestone batching, no tiny PR/CI for isolated facts.