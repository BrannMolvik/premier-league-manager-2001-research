# Recovery 451 — original mailbox delivery, pending queue and immediate EAM modal are different operations

_10 October 2026 KST. Independent P0-B original-file fidelity audit only. No game implementation, Codex write, original asset/save change, CI, Windows executable launch, release, merge or gate closure._

## Source and provenance

Checked latest main `12e85867431892edf3088cbc8dfc2d709b3b1675`, binding `research/CURRENT_STATE.md` and runtime `audit_only/implementation_allowed=false` first. Codex implementation branch head `0ae745d1b56f45cade460f03cd893849a2f53b45`, untouched. Authorized original `footballmanager.exe`, **4,714,541 bytes**, rehashed **SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. Private source reproduction: `objdump -d -M intel` ranges `0x424E12..0x424E56`, `0x617D70..0x617DA8`, `0x472680..0x47276D`, `0x413020..0x413509`, `0x613EC0..0x613EDE`, `0x4175C0..0x4176A0`, `0x551BB0..0x551C50`, `0x470E90..0x470FA2`. Never commit original executable/disassembly.

## A. Per-manager inbox is a 12-byte header with append-ordered doubly linked 12-byte nodes

1. Original user constructor **`0x424E2E`** allocates 12-byte mailbox header, initializes dwords +0/+4/+8 to zero at `0x424E3A..0x424E42` and stores the pointer as **`user+0x6B4`** at `0x424E4B`.
2. Original **`0x617D70`** appends an *already allocated* 12-byte node to a list's **tail**. For nonempty list, it sets old_tail+0x04=new_node, new_node+0x04=0, new_node+0x08=old_tail, header+0x08=new_node; empty list sets header+0x04 and +0x08 to new_node, and zeroes its next/previous. **header+0x04=head**, **header+0x08=tail**, **node+0x00=EAM record**, **node+0x04=next**, **node+0x08=previous**. This is append order, not a globally sorted array.
3. Native **`PEAMail::0x472680`** traverses *current user's* mailbox head from user+0x6B4→header+0x04, follows node+0x04 and reads node+0x00 EAM polymorphic pointers. It builds **separate PEAMail+0x68 filtered/ordered display array**, whose count is +0x6C. Screen sorting must not mutate owner insertion order. Actual sorting details and live message chronology are separately source-audited in Recovery439.

## B. Separate pending queue and recipient-manager routing

The manager-owner's **`0x413020`** iterates linked registered managers at manager-owner+0x9CC, inspects event virtual +0x0C/+0x10/+0x14 plus per-user club/schedule fields, and conditionally allocates new **12-byte nodes** for a particular recipient's **user+0x6B4**. Three verified mailbox append call chains:

| Original routing range | Recipient mailbox selection | Concrete append |
| --- | --- | --- |
| `0x413413..0x41342A` | read current recipient user+0x6B4 from iterator | `0x41342A→0x617D70` |
| `0x413436..0x41344D` | dereference manager user, read +0x6B4 | `0x41344D→0x617D70` |
| `0x4134ED..0x413504` | dereference iterator user, read +0x6B4 | `0x413504→0x617D70` |

At **`0x413349..0x413357`**, however, source adds a separate record to **global `0x947AA8`** using `0x613EC0`: that helper allocates a 12-byte node and uses **`0x617D70` on this different list owner**. Merely queuing there does **not** mean the record has already arrived in a user's mailbox. The global queue may contain events with non-mail consequences; source does not establish a “mail only” queue or imply that all users see the same message.

**Source distinction:** EAM record production, global pending event append, per-manager mailbox append, per-panel filtering/order are independent operations. Class names and raw counts alone cannot establish delivered inbox content or persistence.

## C. Representative EAM-named object is directly presented as an immediate modal, without mailbox append in this path

Original **`0x4175C0..0x41769F`** allocates 0x50-byte record `0x4175D9`, constructs **base `EAMYouthPromoteOffer`** via `0x551BB0` at `0x417637`, then installs **final vtable `0x7BDA8C`** at `0x41763C`. Recovered original RTTI descriptor: **`.?AVEAMYouthPromoteOffersub@@`** — NOT the base `EAMYouthPromoteOffer` vtable `0x7CE780` identified in Recovery450.

At `0x41764F` it immediately invokes **`0x470E90(record)`**, which constructs 0xD08-byte native **`PEAMMessage`** via `0x472CD0`, lays it out at original 710×420, pushes modal stack via `0x5EB540`, retrieves native result through `0x532650`, removes modal via `0x5EB920` and returns result. The caller checks **result==5** at `0x417657..0x41765A`, taking distinct original record-specific continuation/cleanup branches. **No user+0x6B4/0x617D70 mailbox append occurs in this bounded caller+modal path.** The existence of an EAM RTTI class is thus not proof that this particular instance ever appears in mailbox rows. It does not exclude other producer sites creating related mail records.

**Classification:** EXPLICIT original bytes close this representative immediate-message/modal path, list initialization, append semantics, manager-routing and separate pending queue. **UNKNOWN:** result5 semantic caption, original virtual event codes' human-readable labels, precise temporal delivery of other EAM families, save/load, cross-club mailbox contents and live Windows11 UI acceptance.

## D. Codex implementation-owner handoff and gate

Current main and Codex still have no native EAMail header click or integrated inbox; only source-bound menu action identity exists. Codex **must** represent per-manager mailbox independently from pending queue and direct modal notifications, preserve record identity & append order independently from display sorting and 8-slot/20px/532×18 native row UI (Recovery450), use source-proven per-class vtable equivalent actions/status rather than generic fake EAM rows, and test across **two managers/clubs** with empty and populated mailboxes using the normal game mouse path. Save/load persistence and exact physical row/auxiliary event dispatch remain unverified. The audit worker may only update research and evidence, not implement, build a Windows release, or close Gate13.

**Gate13 OPEN; Gates14–17 and verified original-scope Windows11 release INCOMPLETE.**
