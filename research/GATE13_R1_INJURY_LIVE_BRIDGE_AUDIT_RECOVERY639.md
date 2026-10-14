# Gate 13 R1 recovery 639: injury source → live state correctness audit

15 October 2026 KST. Canonical main `5c98135a10c8e5628fb0ab230d62bfa36c2d6922` includes PR738 (exact-head focused Gate13 and asset policy successful); previously merged original `606540` human pending event transfer/retention research remains valid only as source projection. This report audits the **currently executing modern path** rather than treating additional native source adapters as playable work.

## Live implementation compared to original

| Surface | Current running port | Original source status | Verdict |
|---|---|---|---|
| Injury producer | `match_injury_persistence.generate_persistent_match_injury` changes `RuntimePlayer.injured`, recovery date, severity, condition and weight based on modern `date` and RNG | `41A5B0→605F90→606540→60AA20` separately verifies original 12-byte descriptor, native player+24C owner pointer, mutable 9847FC calendar day, source bit/byte updates, conditional human RNG and two distinct native pending event types | **PARTIAL: cannot identify modern injury result with reached native producer** |
| Scheduled injury clear | `clear_expired_persistent_injury` toggles the modern fields on a date predicate | Original pending `7D7760` date, signed due scanner 613EE0→5D7B40→418AD0 clears native player+24C and DWORD+14 bit0 and may invoke 686FE3 free | **WRONG if advertised as executing native 418AD0**; docstring corrected here |
| Global original pending | `GameState.original_pending_transfer_eam` strictly handles only `EAMPlayerAskTransferListsub` | Original `947AA8` additionally holds `7BD564` human injury wrappers and `7D7760` player-expiry event; 613EE0 requires signed day, owner, recipient and deferred 614080 | **MISSING for injury; never coerce to transfer class** |
| Per-registered-user mail | `original_delivered_mailboxes` explicitly supports the transfer class and serializable user list | Native 413020 routes selected 606540 notice via human club+40 key to first matching user+6B4; types30/31 recheck dynamic club lookup on due | **MISSING for injury; cannot invent same recipient as transfer request** |
| Retention and save | Modern transfer queue/mailboxes snapshotted; original injury notice class and original descriptor/raw dates absent | Original user+6B4 native 5CF990 virtual+40 365-day signed wrapped retention and virtual+44 removal; original queues distinct | **MISSING for injury** |
| Presentation | The transfer row content/title has its own source class | No proven original injury notice text/body/icon/row mapping in modern game host | **MISSING, do not reuse transfer text** |

## Source-safe bridge acceptance requirements

1. Verify original `41A5B0` mode/row and RNG results at each actual `605F90` site against live `generate_persistent_match_injury` before changing `GameState`; attach source player IDs, source club/manager ownership and original descriptor status+5. Qualify original `606540` human branch and `60AA20` status/date for the same event without inventing callbacks or aliasing original pointer identities.
2. Design a **portable, validated event identity** for both original pending types and global vs registered-user queue owner. Keep native raw source dates and signed comparisons separate from `datetime.date`; no transient pointer persisted as an address pretending to be valid on resume.
3. Add atomic commit boundary for already-reached source player bytes, `RuntimePlayer` injury state, correct pending events, original calendar and only verified managers. On any exception or source mismatch, preserve RNG, player/queue/mail and snapshot state. Exercise same-day multiple events, deferred drain, wrong club/manager, absent recipient, status0–3, expiry and Save→Load→NEXT roundtrips.
4. Qualify native 413020 first registered user when owner and due-stage 4D recheck match. Registered-user+6B4 receipt must not be produced from mere source candidate; actual modern user mailbox needs consistent owner registry and deterministic persistence. Only render an injury PEAMail row when original source title/body/row resource and readiness virtual are validated.
5. Build the **player-visible normal vertical slice**: actual NEXT→PPreMatch original modes0–3→PResults→management return with both team ownership and source-verified actual match effects. Current `HumanGameplayController.play_original_user_primary_match` intentionally rejects modes0–2, and quick mode3 alone cannot pass Gate13.

## This integration boundary's change

The inaccurate `clear_expired_persistent_injury` docstring implying full native 418AD0 is replaced with an accurate modern-only contract. No unverified new queue, original injury mail or source byte mutation is introduced merely for a green test. The next implementation should add validated state transitions with a source-backed complete producer→consumer test, not another stand-alone class/address lookup.

Gate13 remains OPEN, as do Gates14–17, all original countries/league career support, multi-human acceptance and native Windows11 install/GUI release verification.
