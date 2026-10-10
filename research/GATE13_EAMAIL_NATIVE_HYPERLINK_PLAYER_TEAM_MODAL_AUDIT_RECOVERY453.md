# Recovery 453 — native EAMail clickable text and player/team information modal routes

_10 October 2026 KST. Source-first Gate-13 P0-B original gameplay navigation audit, continuing exact Recovery452. **STRICT AUDIT ONLY**. No reconstructed game code, Codex branch, original binaries/assets, saves, CI, merges, or gate states changed._

## Checkpoint and reproducibility

- Live starting `main` HEAD: **`d5de9e20e9e0991f0e05ea43977ab8ebb35b966e`**; current `research/CURRENT_STATE.md` prioritizes the ordinary original menu/inbox/first-team/NEXT functional journey, not surface-only effects. Agent runtime requires `worker_role=audit_only`, `implementation_allowed=false`.
- Latest Codex implementation head: **`0ae745d1b56f45cade460f03cd893849a2f53b45`**, unchanged during this audit.
- Canonical authorized privately held original `footballmanager.exe`, **4,714,541 bytes**, reverified SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. Reproduce with `objdump -d -M intel` original source ranges `0x471C60..0x471D11`, `0x5CF7B0..0x5CF807`, `0x604900..0x604BC6`, `0x605DC0..0x605ECE`, `0x605EE0..0x605F35`, `0x559610..0x559638`, `0x585F00..0x585F25`, `0x5B6000..0x5B600F`. Class RTTI addresses are verified from actual original `.rdata`, not clean-room names.

## A. Native row text controls are actionable hyperlinks, not merely generic row selection

Recovery450 source-verified that each **532×18** `PMessageRow` has local child text controls **ID2 at (38,0,215,16)** and **ID3 at (256,0,215,16)**. They do **not** simply repeat the background ID1 select/reactivate route.

Original **`PMessageRow` vtable `0x7C266C`**, virtual **`+0x20→0x471C60`**, branches on child event ID stored at **`event_control+0x20`**:
- **ID2 → `0x471C9C`** reads row `+0x490` byte (link code) and the polymorphic message record's embedded **`+0x1C`** value, then calls **`0x5CF7B0(&message+0x1C, code, &out_kind)`** at `0x471CAE`.
- **ID3 → `0x471C86`** reads row `+0x5C0` byte and invokes **the message record's virtual `+0x34`** at `0x471C97`, returning an object index/id and a by-reference `out_kind`. Different concrete message classes supply different method bodies (below).
- After either source operation, if return is **-1**, the handler performs **no info-panel dispatch** (`0x471CB3`). Otherwise `out_kind≠0` dispatches through original **`0x605DC0`**, whereas `out_kind=0` dispatches through **`0x604900`**. The original code also handles negative/default team-reference value through global `0x874B94`, rather than treating all indices as ordinary valid positive record identifiers.

**Key categorical correction:** Recovery450 had deliberately left IDs2/3 as unspecified auxiliary actions. Native code now proves they are **cross-navigation link actions to original information dialogs**, *not* generic inbox delete/reply/accept buttons. Their mere existence does not imply every record populates a link target: native -1 and some record virtuals explicitly disable it.

## B. Source link codes 'P' versus 'C' and exact reference extraction

The original **`0x5CF7B0`** called for row child ID2 checks the byte-valued code:

| Original byte | Native return/output behavior | Downstream target |
| --- | --- | --- |
| **`0x50` ('P')** | writes `out_kind=1`, returns **`[record+0x1C+0x04]`** via `0x5CF7C1..0x5CF7CE` | Player info route `0x605DC0` |
| **`0x43` ('C')** | writes `out_kind=0`; examines embedded ref `+0x00` kind. For kinds **1/2/17** uses a distinct stored reference/lookup from `+0x04/+0x08`, otherwise uses `+0x04` | Team/club info route `0x604900` |
| **all others** | returns `-1`; does not manufacture a valid link | No information screen |

Specifically, for `C`: `embedded+0x00==1` treats `embedded+0x04` as an index, uses `global 0x875628` with 0x40-byte stride and reads record `+0x24`; kinds 2 and 17 return embedded `+0x08`; other kinds return embedded `+0x04`. This is a source-specific polymorphic reference conversion, not merely interpreting a static integer club ID.

The code 'C' and 'P' correspond **by directly observed downstream class RTTI** to team and player information; do not confuse this with the unrelated source manager-to-mail delivery routing or `PEAMMessage` modal detail.

## C. Both destinations are real original modal panels with distinct class RTTI

| Native routing function | Original panel class and RTTI | Modal creation/geometry and return |
| --- | --- | --- |
| **`0x605DC0`** | **`PPlayerInfo2K`**, final vtable **`0x7C48D4`**, COL **`0x7E50D8`**, TypeDescriptor **`0x81D3D8`**, `.?AVPPlayerInfo2K@@` | resolves original selected player index through `0x417270`, creates **0x4AA0-byte** panel via `0x491330`; `0x605E80..0x605E92` calls source layout `0x653320` with **760×500** and dynamic/edge-bounded origin; pushes native panel via `0x5EB540`, waits for original modal result `0x532650`, removes via `0x5EB920` |
| **`0x604900`** | **`PTeamInfo2K`**, final vtable **`0x7D7AF4`**, COL **`0x7F9B00`**, TypeDescriptor **`0x839F70`**, `.?AVPTeamInfo2K@@` | accepts original team pointer, checks original source predicates `0x403FC0/0x403640` before construction, allocates **0x4FB8-byte** object, sets class final vtable at `0x604B4B`, uses `0x605EE0` source layout **760×500** with dynamic/edge-bounded origin, and invokes same `0x5EB540→0x532650→0x5EB920` native modal stack cycle |

The original player info path is **not** the same as a generic Player Card widget. It has its own complex `PPlayerInfo2K` presentation state and modal lifecycle. The team path is a distinct large `PTeamInfo2K` object. The native factory may reject null/invalid objects rather than create a placeholder screen. The exact final window coordinates, dialog pixels/fonts and source-correct return focus remain **UNKNOWN** pending Windows-source GUI acceptance.

## D. Concrete sample record-specific callback behavior, not every message is actionable

Source inspection of **message record virtual `+0x34`** through original class vtables from Recovery450 shows:
- `EAMYouthPromoteOffer` vft `0x7CE780+0x34→0x585F00`: accepts **only link code 'P'**, writes `out_kind=1`, returns record **`+0x44`** (player selection field); any other code returns -1 and `out_kind=0`.
- `EAMClubTransferOfferReply` vft `0x7CEFCC+0x34→0x559610`: accepts **only 'P'**, writes `out_kind=1`, returns record **`+0x1C44`** (different derived record layout); all other codes reject.
- `EAMAssManMonthlyTrainingReportM` and `EAMbcmonthlyincome` vft `+0x34→0x5B6000`: always `out_kind=0`, return **-1**, so their **ID3** row text is not a valid info-navigation link at this callback.
  
This source-level method ownership refines action coverage: **ID3 may open a player link for certain messages but does nothing for others**. It is *not* an automatic second action/accept button on all inbox messages.

## E. Codex implementation handoff and Gate13 acceptance boundary

The newest Codex host still lacks a native `PEAMail` panel and source input path, so no original EAMail-row link can currently open these modal information panels. Preserve:
1. original source PBg EAMail header rect(558,0,40,95) and PMenu action0x65 with original list/detail;
2. first-select vs second activation on original background ID1; child **ID2/3 links to the correct source typed player/team modal**, respecting `-1` as no action, per-class virtual handlers and structured club references;
3. original `PPlayerInfo2K` and `PTeamInfo2K` separate source result/lifecycle, rather than a fabricated generic info popup;
4. ordinary native-look pointer/keyboard hit tests, correct modal return/focus, correct manager/club/player context and two-manager/club original Windows11 visual/playability receipts.

This is a **new confirmed user-visible navigation gap** within the existing complete P0 original gameplay mission. No Windows 11 executable acceptance, implementation, original assets, CI or gate closure has been done.

**Gate13 OPEN; Gates14–17 and verified original-scope Windows11 release INCOMPLETE.**
