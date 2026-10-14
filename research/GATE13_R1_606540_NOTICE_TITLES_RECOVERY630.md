# Gate 13 R1: 606540 human injury notices, original +0x18 title source (Recovery 630)

15 October 2026 KST. **Unmerged feature-branch source proof**, not native runtime/Inbox acceptance.
Canonical base main: `5c98135a10c8e5628fb0ab230d62bfa36c2d6922`.
Build on `research/GATE13_R1_INJURY_LIVE_BRIDGE_AUDIT_RECOVERY639.md` and merged native 606540 constructor / 7BD564 / 413020 / user+6B4 / 5CF990 source projections. The original is authoritative.

## Private original evidence, independently read

- Original disc-root `footballmanager.exe`: exact 4,714,541-byte PE, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, fetched privately from owner-provided Google Drive file id `1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q`. **Statically read only. No original program launch.**
- Original `EnglishEAM.str`: exact 298,747 bytes, SHA-256 `98387ef673e87a02cf2cab7349770a4415f29fd381877b603922302c3e3f174f`, private extracted root Drive file id `1l1kH5j1GTLLQZpZzzvFKMOx384mzq0rX`.
- Original `EnglishEAM.idx`: exact 5,754 bytes, SHA-256 `bd0e2b804f1ce85011509ff828cdc70f2409509537ec61a012d1fa0175932367`, file id `11XjOAadbWE72RITu3W-cTqW_bp3rtomt`.
- Exact resource parser: `reconstruction/ea_language_strings.py` (1,609 STR strings, 2,877 IDX entries). Original `0x50D5A7→0x5B65A0→0x64E320` places 2,877 IDX-selected pointers in descending DWORD slots beginning `0x87AC28`; IDX ordinal `n` addresses global `0x87AC28−4*n`. All actual title vtables are sourced from `original_native_606540_human_mail_route._CONSTRUCTORS`, not an assumed modern category.
- For **all 15** original 606540 concrete notice vtables, independently inspected PE DWORD `[vtable+0x18]`, title callback's direct reference to the expected pointer-slot address, resource IDX ordinal and actual STR ID/text. Local private read-only verification of 15/15 passed. No native callback was run.

## Full constructor → native title callback → IDX/STR contract

| Constructor | Concrete vtable | Virtual+0x0C tag | Virtual+0x18 callback | IDX ordinal | STR ID |
| --- | --- | ---: | --- | ---: | ---: |
| `58AA70` | `7D1CE0` | 243 | `58AB00` | 1803 | 1153 |
| `58AD80` | `7D1D34` | 244 | `58AE10` | 1808 | 1153 |
| `58B090` | `7D1D88` | 245 | `58B130` | 1813 | 1158 |
| `58B360` | `7D1DDC` | 246 | `58B3F0` | 1818 | 1153 |
| `58B670` | `7D1E30` | 247 | `58B700` | 1823 | 1153 |
| `58B980` | `7D1E84` | 248 | `58BA20` | 1828 | 1158 |
| `58BB90` | `7D1ED8` | 249 | `58BC20` | 1833 | 1153 |
| `58BEA0` | `7D1F2C` | 250 | `58BF30` | 1838 | 1153 |
| `58C1B0` | `7D1F80` | 251 | `58C250` | 1843 | 1158 |
| `59F8E0` | `7D422C` | 359 | `59F970` | 2383 | 1153 |
| `59FBF0` | `7D4280` | 360 | `59FC90` | 2388 | 1158 |
| `59FEC0` | `7D42D4` | 361 | `59FF50` | 2393 | 1153 |
| `5A01D0` | `7D4328` | 362 | `5A0260` | 2398 | 1153 |
| `5A04E0` | `7D437C` | 363 | `5A0570` | 2403 | 1153 |
| `5A07F0` | `7D43D0` | 364 | `5A0890` | 2408 | 1158 |

The original STR 1153 title is `Ankle injury to {PLAYERNAME:1}`. The exact original STR 1158 is `Ankle injury`. **These are localized source templates, not yet fully interpolated/visible row text.** The returned native tagged player name is not a trivial Python string replacement: original token processing, required owner identity, and user-screen readiness remain separately unqualified.

## Negative evidence / what is NOT done

- Original title source proves class-specific `+0x18` text **only**, not `+0x1C` body content or its 0/1/2 alternatives, original formatting, notice read flags, or icon.
- Static exploration shows fifteen distinct `+0x1C` callbacks and several different STR messages. Do **not** reuse transfer mail content or a generic injury body; independently qualify native status/type/variant branch before binding a body.
- Original 606540 constructor and 7BD564 global pending wrapper, 5CFA20 due call, 413020 first matching user routing and 5CF990 retained per-user list remain **source-projected**; *no observed original native heap operations, entire queue execution, live portable world event or registered user receipt*. Existing `GameState.original_pending_transfer_eam` and `original_delivered_mailboxes` only cover transfer events. This title mapping cannot authorize insertion into them or a rendered human Inbox.
- Modern persistent injury `RuntimePlayer` state/date in `match_injury_persistence.py` is **not the original native +24C descriptor**, 9847FC unsigned raw calendar or the original 7D7760 cleanup. Keep native 32-bit signed date/owner independent from modern `datetime.date`.
- Original all-mode NEXT→PPreMatch→PResults→management return and Gates 13–17 physical Windows 11 game acceptance are still **OPEN**.

## Implemented source-bounded change and continuation

Feature branch adds `ORIGINAL_606540_TITLE_ROUTES` and strict, read-only
`VerifiedOriginalEAMailLanguage.original_606540_notice_subject_template(due_receipt)`, requiring a typed original source receipt with exact constructor, vtable, tag, IDX identity and original STR text. New counterexample tests reject mismatched/forged owner selectors and modified source bytes; private PE check uses optional `FM2001_ORIGINAL_EXECUTABLE`, not CI-bundled copyrighted files.

**Next executable task:** source-verify each `vtable+0x1C` class-specific body choice with actual input dispatch and original STR IDX; then bridge complete 41A5B0→605F90→606540→60AA20 source producer to atomic persistent player/global pending/registered-user event GameState, with first-matching-user/required due recheck, native signed-date semantics, safe Save→Load, multi-event/rollback tests and actual original-player Inbox renderer. No PR/CI for this subpart alone per `WORKER_MILESTONE_BATCHING_POLICY.md`: accumulate a coherent source-backed integration before exact-head review.
