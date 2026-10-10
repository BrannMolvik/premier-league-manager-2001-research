# Original-game reference and complete-playability audit protocol

**User direction, 10 October 2026:** Further strengthen the automatic worker's original-game checks. The shipped FM2001 is the reference, not the current reconstruction, prior reconstruction tests or guesses. **Audit whole original features and playable journeys, not isolated visual/source details.** This applies to retrospective audits, Codex handoffs and new findings. The user's later 11 October authorization narrowly lifts the audit-only restriction for isolated, source-proven fixes under `research/WORKER_SCOPED_SOURCE_FIX_AUTHORIZATION.md`.

## Original-reference checkpoint cadence

1. At the start of **each substantial new audit target**, identify the exact canonical original executable/resource/data evidence, its identity/hash and reproducible source owner/caller. Re-open the original trace when a claim depends on it, when implementation has changed, or when a contradiction appears. Reuse a valid unchanged hash/trace; do not waste time re-hashing unchanged bytes just to claim activity.
2. Before calling any behavior original-proven, trace the **entry -> actual click/selection -> gates -> state mutations -> modal/nested screen -> return -> future effects/save**. Inspect siblings, conditional branches and alternate menu entrypoints. Check the *original factory/control inventory* to find entire missing screen families, button actions and states, not merely wrong pixels.
3. After every substantive Codex gameplay merge/milestone, compare the recovered original journey with the **new main code and real ordinary player workflow**, not a detached backend helper. Explicitly retire older reports that are superseded by a change. Passing CI proves code tests/build; it does not prove original visible behavior.
4. At **each meaningful worker checkpoint**, consult the breadth inventory below: have original gameplay screens, menus, actions or recurring event phases disappeared from the reconstruction? Prefer a high-impact missing ordinary player workflow over another small isolated layout detail or endless subroutine trace. This is a frequent *original reference* check, not a request for additional commits or CI.
5. If separately authorized and safely possible, observe the running original game in a source-valid environment; log the environment, input sequence and results independently. **Reading/disassembling the original executable is not playing/observing the original game.** Never claim runtime observation without running it. Do not launch the original executable or mutate original saves without separate authorization. Original assets/disassembly remain private.

## Omission-prevention feature inventory

For each row, record exact original evidence/owner, original inputs and effects, original alternatives, current main counterpart, what is absent or incorrect, status, and test needed. Items listed here are *audit targets*, not claims of full original semantics.

- Startup video/audio/aspect, original PStartMenu: New, Load, Continue, Exit, and proper state ownership.
- TeamSelect, club/country choice, genuine new career, original 2–6 human managers and user rotation.
- Shared PBg header, PMenu complete child-action/navigation map, direct entry variants, overlays, exit/return, menu responsiveness.
- Squad first/reserve, row/drag restrictions, 1ST & RES / 1ST FORM / RES FORM, eleven pitch slots, saved named formation team sheets, calculator lineup and persistence.
- Original tactics, player/team info, transfers/contracts/staff, training/scouting, finance/commercial, fixtures/results, tables, news and Inbox.
- Original inbox **producer -> pending queue -> eligible recipient -> delivered per-user mailbox -> visible row/detail -> action/return -> expiry/save**. Do not show pending events as delivered messages.
- Original NEXT: roster guards, calendar/event selection and ordering, primary **and secondary** calendars, daily transfer windows/training/commercial, postponements, competitions, dismissals, end-season, multiuser.
- PPreMatch original selectable modes (3D / Highlights / FastView / Quick) and mode-specific setup, true match calculation, PResults progress, post-match callbacks and original conditional management return.
- Original Save and Load UI controls and slot operations, fresh-process re-entry, saved/resumed season, all original users where supported.
- Broader original gameplay scope across multiple clubs, competitions, countries and original visual/audio/match systems, not only Southport or one Quick Match proof.

## Evidence and classification matrix

For each audited feature, do not skip these fields:
- **Original identity:** original executable hash + address/function and/or original resource/observation, with source/caller/control context.
- **User journey:** entry, all material controls, state prerequisites, alternate/disabled cases, effect, exit/return and later persistence.
- **Port implementation:** exact file/ref and ordinary GUI action; source coverage inventory of omitted children and behaviors.
- **Status separately:** SOURCE-VERIFIED, OBSERVED-IN-ORIGINAL, INTEGRATION-VERIFIED and VISIBLE-ACCEPTED. Label implementation EXACT / COMPATIBILITY-EQUIVALENT / PARTIAL / WRONG / MISSING / UNKNOWN. Don't infer one status from another.
- **Player impact:** precise P0/P1 consequence, including absent sections. Distinguish *confirmed code gap* from conditional hypothetical bad match or save.
- **Codex handoff:** minimum source-justified vertical slice, concrete normal Windows11 mouse acceptance scenario, negative/alternate tests and no fabricated missing logic.

An original fully functional management screen cannot be considered restored if major original actions are only drawn or entirely absent. A functioning backend match engine is not a playable NEXT path without PPreMatch, result and return. Preserve unresolved behavior as UNKNOWN and avoid invented substitute features. Update `research/ORIGINAL_FILE_FIDELITY_LEDGER.md` or a linked auditable report with each meaningful result, source references and an explicit completeness row.

## Roles and boundaries

As of 11 October, the automatic worker is an original-game completeness auditor **and primary implementer of verified high-impact missing functionality** outside Codex's active R1 ownership. It may work on substantial source-proven features, execute tests, and perform qualifying routine worker PR merges under `research/WORKER_SCOPED_SOURCE_FIX_AUTHORIZATION.md`, including original-based PR CI where local execution fails. Complex, insufficiently proven or shared state integration belongs to Codex only when needed. No unapproved original executable run, guessed features, hidden original bytes, direct game commits to main, unsound self-merges, premature Gate13 closure or false Win11 acceptance. Both roles retain full original scope through Gate17.
