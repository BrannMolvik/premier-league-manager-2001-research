# Recovery591: native FastView edit replay visitor implementation map

Original executable: owner-verified extracted footballmanager.exe SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. 4,714,541 bytes. Local STATIC source inspection ONLY, no original execution or Windows11 GUI acceptance. Baseline current main after verified merged PR667: ec95394177d88d060724f391edfe6645c3b4ad89. Active gate13; Gates14–17 OPEN.

After PR667 established eight authentic original staged edit subclasses and corrected the count visitor to replacement-only, the next dependent source investigation of ORIGINAL replay visitor 0x7D8014 traced all eight virtual methods at +4..+0x20 against actual PE .rdata and code. 8/8 exact visitor pointers and 7/7 independently chosen instruction signatures were verified locally:

| Native staged record visitor slot | Actual replay routine | Source effect boundary |
|---|---|---|
| +0x04 (replacement class vtable 0x7D7F90) | 0x634B00 | Conditional replacement/chain replay with scratch flags +8/+9; mutates side buffer under matching case |
| +0x08 | 0x634AB0 | Append original record pointer to native temporary queue |
| +0x0C | 0x634AB0 | Append original record pointer to native temporary queue |
| +0x10 | 0x634990 | Conditional source-record replay, specific semantic effect not yet complete |
| +0x14 | 0x634920 | Conditional source-record replay, specific semantic effect not yet complete |
| +0x18 | 0x634AB0 | Append original record pointer to native temporary queue |
| +0x1C | 0x634AB0 | Append original record pointer to native temporary queue |
| +0x20 | 0x634AB0 | Append original record pointer to native temporary queue |

**Do not classify 0x634AB0 as a do-nothing handler:** original 0x634AB0 allocates a 12-byte native linked node at 0x668140, appends it into visitor+0x14's list, copies the original record pointer into the new node+8 and increments list+8. The source count visitor's 0x6596D0 no-op applies to a DIFFERENT visitor vtable, not this replay visitor.

The original 0x634B00 matching branch tests previous queued replacement +8 (destination) against the requested source player at current replay visitor+0x0C (0x634B82..0x634B89). When equal it can create a new original 0x6335D0 replacement from the prior source toward the requested destination, modify live source side bytes/DWORDs at 0x634C1D..0x634CF4 and set scratch +9=1. Other callback alternatives and multi-record skip count have not been fully reproduced. Original 0x634DF0 returns scratch +9, which is OR-accumulated by 0x633020's owner. This has real state effects, so calling 0x633020 a pure permission check is incorrect.

New WIP branch worker/gate13-r1-fastview-replay-visitor-semantics-591 contains only read-only original type->visitor method projection and normal/opt-in-original PE tests, with private source provenance. This WIP does NOT implement edits, modal, match, PResults or return and has NO PR/CI or Win11 GUI verification. Do NOT merge a tiny PR merely because these static instructions were traced.

Exact next step: original 0x634920 and 0x634990 full record-specific visitor semantics and 0x634B00 preceding +4 iteration/status +8/+9 replay branches; connect with 0x633020 temporary-list ownership and native once-only event producer 0x651AC0. Once complete, integrate original FastView mode2 live modal, true two-sided match writeback, PResults and management return. Retain full league/country, 2–6 humans, Save/Load, Gates13–17 release requirements.