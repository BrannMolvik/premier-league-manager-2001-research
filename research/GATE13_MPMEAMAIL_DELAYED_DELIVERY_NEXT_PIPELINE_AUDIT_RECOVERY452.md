# Recovery 452 — scheduled MPMEAMail delivery runs through original NEXT/PResults event processing

_10 October 2026 KST. Continue exact Recovery451 P0-B original inbox source work. Strict independent AUDIT ONLY: the existing Codex implementation owner retains game edits, source assets, saves, CI, merges, Win11 playtests and gate validation._

## Canonical source and identity

- Verified live main at recovery start **`bc1796d2a9534ab4abb94517cb5a721323fe323a`** and `research/CURRENT_STATE.md`: original PMenu, functional inbox, first/reserve formation and NEXT/MATCH normal gameplay outrank cosmetics. `agent-runtime` confirms `worker_role=audit_only`, `implementation_allowed=false`. Current Codex head **`0ae745d1b56f45cade460f03cd893849a2f53b45`** is untouched here.
- Canonical authorized original `footballmanager.exe` 4,714,541 bytes, **SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**, reverified locally using Python; no original game process launched or binary/disassembly committed.
- Original MSVC RTTI independently verified: **`MPMEAMail`** final vtable **`0x7BD564`**, COL `0x7DED48`, descriptor `0x818528` `.?AVMPMEAMail@@`; virtual **`+0x10 → 0x5CFA20`**. Two derived record examples created by manager router: `EAMChairSeasonTicketssub` vft **`0x7BD9B8`** (descriptor `0x818B78`) and `EAMChairSeasonTicketSetsub` vft **`0x7BD95C`** (descriptor `0x818BE8`). Names are original RTTI strings, but their precise interactive captions and financial effects remain untested.
- Reproduction with `objdump -d -M intel`: source `0x41325A..0x413509`, `0x5CFA20..0x5CFA4F`, `0x613EC0..0x613F7B`, `0x43215E..0x43218D`, `0x4A8070..0x4A8089`, `0x5CF990..0x5CF9C6`, native RTTI read via vtable[-4] → COL+0x0C TypeDescriptor.

## A. MPMEAMail provides a scheduled envelope, distinct from delivered per-manager EAM

At source manager router **`0x4132C5..0x41335C`**, one qualified event path:

1. allocates a **12-byte envelope**, builds a **0x50-byte EAM record** using **`0x54F060`**, installs final `EAMChairSeasonTicketssub` vtable `0x7BD9B8` at `0x41331D`;
2. sets **envelope+0x04 = original game date `0x9847FC` + 1** and **envelope+0x08 = record pointer** at `0x413327..0x413333`, installs **`MPMEAMail` vtable `0x7BD564`** at `0x413336`;
3. modifies this record's **`+0x08` low status byte with mask `0x06`**, then adds the *envelope*, not the record, to **global pending list `0x947AA8`** using `0x613EC0` at `0x413349..0x413357`.

Another qualified original branch `0x413363..0x4133D6` constructs a **0x54-byte `EAMChairSeasonTicketSetsub`** record (vft `0x7BD95C`, constructor `0x54F870`), with additional fields at record `+0x4C/+0x50`, and joins the **same envelope/date+1/list insertion** at `0x413330`. These two examples demonstrate subtype-dependent payloads within one scheduled envelope. Do **NOT** claim that all mail delivery is next-day, or that all queued messages carry the same flags/caption.

Importantly, **`0x613EC0`** allocates another 12-byte *list node* and calls **`0x617D70`** to append **the envelope** to the pending owner `0x947AA8`. The queue list node, the `MPMEAMail` envelope, and the underlying EAM message record are three different original objects.

## B. Native scheduled event handler gates actual mailbox routing

**`MPMEAMail::0x5CFA20`**, reached via its own vtable **`+0x10`**, performs:

- reads its underlying **EAM record pointer from envelope+0x08** at `0x5CFA23`;
- calls the **record's virtual `+0x3C`** at `0x5CFA26..0x5CFA28`, and **only if it returns nonzero** proceeds to delivery; what this predicate means at UI level remains unknown;
- on accepted route, **copies envelope+0x04 scheduled date into EAM record+0x04** at `0x5CFA32..0x5CFA35`;
- **pushes the EAM record and calls original manager owner `0x874C10::0x413020`** at `0x5CFA3B..0x5CFA48`. This is the independently traced branch-specific recipient routing and append to **user+0x6B4** from Recovery451.

This is a **source-proven deferred event → message readiness check → date stamp → per-manager dispatch** chain; the queue's mere existence does NOT prove the particular record has been delivered. A virtual predicate returning false skips these mailbox actions on that invocation. The exact record-specific `+0x3C` implementations may differ (for example `EAMChairSeasonTicketssub` `+0x3C=0x651E20`, `EAMChairSeasonTicketSetsub` `+0x3C=0x4093E0`); the original user-facing condition is not asserted.

## C. The real NEXT/PResults loop drains due queued envelopes

Original pending owner method **`0x613EE0`** is explicitly called on **global list `0x947AA8`** with the *current game date* **`0x9847FC`** and numeric flag **1** from both:

- **`0x43215E..0x43216C`** in the management NEXT/results continuation after stepping through original registered-manager work, before restoring the selected manager index at `0x43217B`;
- **`0x4A8070..0x4A8084`** in `PResults` post-simulation event handling, before next source result/staff/date owner updates.

At **`0x613EFA..0x613F07`**, it iterates pending list nodes, checks **`event+0x04 <= caller supplied date`**, and invokes **that event's virtual `+0x10`**. For an `MPMEAMail` entry this dispatch resolves to the EAM-delivery method **`0x5CFA20`** above. When the caller's second flag is nonzero (the two cited calls pass 1), **`0x613F12..0x613F1C`** passes the processed list node and record to original node-removal helper `0x4EA190`; **`0x613F30..`** clears the iteration flag and processes deferred list mutation through `0x614080` if indicated. The exact object destruction semantics belong to `0x4EA190` and are not fully type-closed here.

Then **`0x613F4C..0x613F75`** loops all registered managers **`index=0..0x8755E4−1`**, resolves each user with **`0x413B10`**, reads **user+0x6B4** and calls original **`0x5CF990`** on that mailbox. It examines record virtual `+0x40/+0x44` and performs conditional list operations; these exact per-record maintenance semantics remain UNKNOWN. The original processing is **NOT** limited to refreshing the currently selected manager's visible inbox.

**Classification: EXACT source instruction-level due-date bound, event virtual dispatch, called NEXT/PResults sites, manager routing and mailbox-list follow-up. PARTIAL/UNKNOWN** input consumer timing beyond these two call sites, record readiness semantics, lifecycle/delete consequences, save persistence, 2-club behavior, actual Windows GUI receipts.

## C2. Actual original per-record retention and expired-mail removal — source-verified second step

The manager-wide `0x5CF990` pass at the end of `0x613EE0` is not just a redraw/counter recalculation. Its exact original source control flow is:

1. For each existing 12-byte mailbox node, it calls the **message record's virtual `+0x40`** at `0x5CF99C..0x5CF9A3`. If that returns **nonzero**, the node is kept and the iteration advances to the next node.
2. If **`+0x40` returns zero**, it calls the message record's virtual **`+0x44`** at `0x5CF9AA..0x5CF9AE`, then invokes **`0x42CC30`** for the current node at `0x5CF9B8`. That method unlinks the node via `0x42CBF0`, conditionally invokes record cleanup, and frees the list node. This is a *native mailbox-retention/removal rule*, not a visual-list filter.
3. **Default original EAM record method `0x470CE0`** compares `current_game_date 0x9847FC` with **`record+0x04 + 0x16D`** and returns one exactly when `current_date <= record_date + 365`. Multiple representative concrete classes have virtual `+0x40→0x470CE0`: `EAMYouthPromoteOffer` vft `0x7CE780`, `EAMClubTransferOfferReply` vft `0x7CEFCC`, `EAMAssManMonthlyTrainingReportM` vft `0x7CEF24`, `EAMbcmonthlyincome` vft `0x7D00FC` and `EAMChairSeasonTicketssub` vft `0x7BD9B8`. This supports **365 original date-units** of retention for these specific classes, inclusive of the boundary — not all 609 EAM-prefixed types.
4. A concrete counterexample is **`EAMChairSeasonTicketSetsub`** vft `0x7BD95C`, virtual **`+0x40→0x538530`**, comparing **`current_date <= record_date + 0x15`**, i.e. **21 date-units**. Its virtual `+0x44→0x5D18E0` also differs from those representative classes' common `+0x44→0x667D30`. This is **class-specific retention and lifecycle**, not a global mailbox TTL.
5. The previously proven `MPMEAMail::0x5CFA20` stamps the underlying record `+0x04` from the queued event date when dispatching. That dated record field is the **same `record+0x04` operand** used by these retention methods. Delivery chronology, status bits and cleanup timing therefore interact; don't set every message date to when its inbox screen is first opened.

**CONFIRMED:** class-specific original date-offset eligibility tests and the native mailbox per-manager removal sequence, invoked by `0x613EE0` during actual NEXT and PResults advancement; **UNKNOWN:** original game-calendar mapping for date-units under every calendar family, what specialized cleanup `0x5D18E0` additionally changes, full exception list across 609 RTTI EAM classes and user-visible expired-message behavior. Do not automatically delete all mail after 365 wall-clock days or force a one-size global in-game TTL. This source work does **not** prove an implemented usable inbox or verified Windows11 save/load behavior.

## C3. Original EAMail factory placement is not the same as Squad placement

One more independently bounded original-source pass resolves the **parent-panel layout configuration**, supplementing the previously verified **CMessageList panel-local** rectangle `(233,30,545,160)`.

- The original `PMenu` factory **`0x47B1D0..0x47B220`** constructs the real `PEAMail` object (0x14A0 bytes) with the current user's mailbox and calls its original layout wrapper **`0x47F2B0`** with four literal source parameters **`(0,0x94=148,8,0)`**.
- The wrapper `0x47F2B0..0x47F2D3` calls common **`0x653320`** with six source operands **`x=0,y=148,width=0x320=800,height=0x212=530,aux=8,flags=0`**. Source `0x653320` assigns `panel+0x0C=0`, `panel+0x10=148`, `panel+0x14=800`, `panel+0x18=678` and `panel+0x54=0` from these arguments. These are **verified panel-owner rectangle values**, not guessed based on bitmap similarity.
- The same original PMenu factory sets **`PSquadScreen`** differently: `0x47AF66..0x47AF80` calls `0x653320` with **`x=0,y=0x4F=79,width=800,height=0x208=520,aux=8,flags=0`**. Thus reusing Squad's 79-pixel top offset for EAMail would contradict original per-panel setup.
- Combining native EAMail panel coordinate origin `(0,148)` with the source direct child list local origin `(233,30)` gives a **computed unclipped owner-relative list position `(233,178)`**; owner-local list dimensions remain 545×160 with eight 20-pixel slots. **This is not yet a measured final Windows screen-space hit rectangle** because original owner stacking, clipping and any translations/animations still require source/user-visible validation. Notably the stored panel bottom `678` is beyond a nominal 600-pixel height and should not be silently “corrected” to fit a modern canvas without understanding source clipping/viewport behavior.

**Status:** original factory, source owner-rectangle parameters and relative child layout **EXACT**. Final physical screen offset, clipping and pixel-level original Windows GUI receipt **UNKNOWN**. This closes a concrete original-screen parent-layout mapping while deliberately not overstating full on-screen parity.

## D. Concrete Codex handoff (research only)

1. Do not populate the original inbox simply by reading the global pending queue or running all EAM constructors at panel opening. Preserve **global due-event queue → scheduled MPMEAMail envelope → polymorphic record readiness → record date stamp → owner-specific mailbox routing → sorted/filtered PEAMail view**.
2. Preserve **registered-manager-wide processing**, original list/node identity and append semantics, and direct `PEAMMessage` immediate actions as a distinct path. Do not invent a specific financial/season-ticket action or force all EAM families through one template.
3. Codex should integrate a real normal-click PBg EAMail header (native rect **558,0,40,95**) and PMenu `0x65` child with the source 545×160, eight-slot CMessageList, real 532×18 rows, status icons, native two-step row selection, and functional detail action; test with two different clubs/managers and scheduled/delivered/empty mailbox states.
4. Game original NEXT/MATCH source action must process due events in the correct place in the calendar/multi-manager lifecycle; no generic “advance one day then open mailbox” shortcut.
5. Original implementation and Win11 receipts belong to Codex only. Audit owner must not alter reconstruction source, art, saves, branches or gate status.

**Gate13 OPEN; Gates14–17 and verified original-scope Windows11 release INCOMPLETE.**
