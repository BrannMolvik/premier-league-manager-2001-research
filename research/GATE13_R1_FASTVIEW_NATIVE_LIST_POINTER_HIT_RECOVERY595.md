# Recovery595: actual original FastView popup native option list pointer scan

**Date:** 14 October 2026 KST. Gate13 ACTIVE; Gates14–17 OPEN. Current-main base `8bf52b9bd16943b5773c0c349d2ada5b44869492` after reviewed green [PR671](https://github.com/BrannMolvik/premier-league-manager-2001-research/pull/671), Gate13 exact-head run `38437991935` SUCCESS **1205 tests / 80 expected skips**, asset `38437991881` SUCCESS.

Same owner-authorized private original footballmanager.exe SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, 4,714,541 bytes, inspected STATICALLY ONLY, original program never executed, no original binary committed.

## Genuine nested list input owner and original hit precedence

The original popup constructs its nested list vtable `0x7BFD5C` through native 0x449300→0x446740→0x6510F0; see Recovery593/595 source report. Its actual **virtual+0x6C method is 0x6516F0** (exact original vtable DWORD independently verified). The original function calls base `0x64F7A0` with second callback argument zero, then iterates the N native row descriptors in allocation order, each exactly 0x30 bytes, and tests raw pointer coordinates in a half-open rectangle:

- x must be ≥ `[native_row+0x08]` and strictly less than `[native_row+0x10]`.
- y must be ≥ `[native_row+0x0C]` and strictly less than `[native_row+0x14]`.
- On the **first matching** descriptor only, original 0x65174A invokes that native row object's **virtual+0x6C** with the original pointer and second input argument and immediately returns. The row's original vtable `0x7D8118` virtual+0x6C is `0x650F00`. If none match, source returns EAX0. Overlapping descriptors prefer first, not last. x==right or y==bottom is outside.

Independent original PE check of **18/18 exact original machine-code sites** and vtable entry confirmed those comparisons, stride and dispatch. New pure `source_fastview_popup_first_native_row_hit_6516f0` and test cases model the read-only first match on caller-supplied signed DWORD coordinates and authentic native rectangles, reject invalid inputs, avoid assuming source row origin/width. Not an event sent to a physical GUI.

## The important distinction: hit does not automatically mean selection

At original row virtual+0x6C `0x650F00`, disassembly first calls generic 0x650C30; separately it checks child+0x2C rich option pointer, parent-owner option enable bit (`[option+0x64]->+0x48 & 0x10`), and pointer x/y against a second row content rectangle. On passing it invokes native 0x651660 with the existing `option+0x68` source index. However original `0x651660` forwards native item vft+0x10 callbacks with **both explicit callback arguments zero**. The rich option vft+0x10 `0x653A10` requires a NONZERO callback argument before posting actual WM_USER selected index. Therefore this path does **not by itself** prove a click committed a dropdown selection; likely additional pointer event gating/dispatch is elsewhere. Do not conflate current first-hit helper with user click or create fake `y // 15` click handler.

Other examined original native source: `0x653480` adjusts incoming pointer by controller x/y, loops enabled child rects and calls child vft+0x6C with a second argument 1; `0x650C30` executes 0x64F7A0 then optional `0x653480`. Need trace native owner graph/registration to ensure this producer reaches rich option 0x653A10 with a nonzero flag and identify selected index/once-only order.

**Next:** original 0x650F00 / 0x650C30 / 0x653480 flags and per-child dispatch through `0x651660`, actual rich row input callback nonzero, then integrate live original mode2 two-sided edits/match/PResults/management return and physical Windows11 GUI acceptance. Real default countries, multi-human, saves and Gates13–17 remain OPEN. Branch has source/tests/report WIP and no PR/CI yet.