# Gate 15 fidelity-sweep readiness audit

_Date: 3 October 2026 KST_

## Status

**Work-ahead audit only. Do not mark Gate 15 complete yet.**

Gate 13 remains the earliest incomplete validation gate and Gate 14 still has
unresolved original match-presentation/audio work. Gate 15 may therefore be
prepared out of order under the deferred-blocker policy, but it must not be
declared passed until the earlier prerequisites close and this audit is
reconciled against the then-current `research/FIDELITY_GAPS.md`.

The Gate-15 roadmap criterion is not "every difference must be reverse
engineered." It is:

1. every known deviation is fixed, proven irrelevant, or explicitly
   accepted/documented; and
2. no deterministic fallback is described as original behavior without
   evidence.

This audit separates **release-blocking unbounded claims** from **bounded,
fail-closed compatibility limitations**. "Acceptable as a documented
limitation" below means the project can satisfy Gate 15 without pretending the
behavior is original; it does not mean the difference disappears.

## Current source-execution blocker

The authorized original-source archive remains known and provenance-locked, but
the current ChatGPT execution allocation cannot start either shell/container or
Python processes and raises `caas.internal.errors.ClientError` before process
start. Fresh private disassembly is therefore unavailable in this worker.

Repository-persisted evidence remains usable. Any item that needs a new
instruction trace is left fail-closed rather than inferred.

## Fidelity items

| Fidelity item | Current disposition | Gate-15 readiness judgment |
| --- | --- | --- |
| Secondary startup exact tie permutation and bucket shape | The runtime replays the independently recorded aggregate 262-node / 45-bucket / 217-shuffle-draw boundary and preserves the proven post-secondary CRT checkpoint, but does not claim an invented per-date mode-1 bucket vector or equal-key native permutation. | **Bounded documented limitation.** The aggregate fallback is explicitly labeled and deterministic. Keep it in release limitations unless the exact secondary bucket vector is later source-locked. |
| Fully indistinguishable Premier League table qsort ties | Numeric fields and CP1252 short-name comparator are exact. If complete source keys are identical, exact gameplay ranking publication is withheld; lightweight display-only callers use an explicitly documented deterministic fallback. | **Bounded fail-closed limitation.** No fallback is represented as original. Canonical starting Leagues have no duplicate short names, but later-season exact-key equality is not assumed impossible. |
| Original PLM2001 save compatibility | The modernization uses a versioned internal save format with verified save/reload continuation; original legacy-save import/export is not implemented. | **Explicitly acceptable modernization limitation** unless original-save compatibility is promoted to a separate release requirement. Gate 8 deliberately tracked it separately from reliable internal save/load. It must remain named in final release limitations. |
| Player-negotiation residual branches | Ordinary accepted, low-wage, counter-offer, already-signed, recently-joined, conclusion and completion paths are implemented. Unmapped `0x422803` reason/status and invalid-duration revision branches stop in explicit deferred outcomes instead of fabricating policy. | **Bounded functional limitation.** Safe for Gate-15 acceptance only if final release notes state that uncommon original negotiation refusal/revision branches remain unsupported. Prefer source closure if execution access returns. |
| Due `MPMTransferPlayer` same-day ordering | Modern runtime currently executes due transfers after the date's fixture block. Persisted evidence proves `0x613EE0` is first inside `0x4A8070`, but does not preserve the outer call relation between that daily coordinator and same-day match execution. | **Blocked source question, explicitly approximated.** Do not promote the modern ordering to an original claim. Can be accepted only as a named same-day availability limitation if fresh source execution remains unavailable at final fidelity audit. |
| Match-day / recurring commercial income | Ordinary Premier League gate receipts are live. English Cup policy/RNG primitives are source-backed. Recovery 187 adds the exact special controlled-participant category-1/category-2 accounting helper and neutral `0x5DBCD0` paired-XI numeric primitive; full live Cup attachment still depends on source-locking the alternate modifier caller/applicability. Fresh concession income remains disabled because its generator does not activate records. | **Not yet preferred for acceptance while a small source caller boundary remains.** If private execution remains unavailable, final audit may accept the missing live Cup-special attachment as a documented finance limitation, but must not call it original or infer "revenue sharing." |
| Finance/board residuals | Ordinary Balance/cash, transfers, Premier League gate receipts, payroll, objectives and job security are integrated. Legacy chairman-budget events are proven irrelevant to the ordinary shipped fresh-game path. Exact support-staff amount materialization, broader Cup/facility behavior and some EA-facing labels remain incomplete. | **Mixed.** Legacy budget events are resolved/irrelevant. Neutral category labels are documentation-only. Support-staff amount and broader Cup finance remain real bounded cash-flow limitations and should stay named unless source-closed. |
| Original front-end presentation | Owned by Gate 13. Schema 8 repository contract exists, while real-Windows schema 8 validation and several fail-closed native interaction/pixel boundaries remain open. | **Prerequisite blocker.** Gate 15 cannot use acceptance language to bypass Gate 13's own completion criteria. |
| UI fidelity | Owned by Gate 13; representative source-backed management route exists but still has unresolved native interaction/pixel boundaries. | **Prerequisite blocker.** Resolve/audit with Gate 13 first. |
| FastView/3D and original audio/match presentation | Owned by Gate 14. Semantic match-event shell and resource resolver groundwork exist, but exact source paths/placement, orientation, audio binding and recognizably original match presentation remain open. | **Prerequisite blocker.** Resolve/audit with Gate 14 first. |

## No-false-original audit

The currently bounded fallbacks satisfy Gate 15's second criterion in design:

- source-indistinguishable League-table ties withhold exact gameplay ranking
  rather than publishing club-ID order as original;
- secondary-startup aggregate replay is labeled aggregate-only;
- unresolved transfer-negotiation branches return explicit deferred states;
- due-transfer same-day ordering remains documented as a reconstruction
  approximation;
- Cup-special accounting uses neutral source terms and does not infer a
  business-policy label;
- unsupported presentation pixels/actions are withheld rather than replaced and
  described as original.

This must be rechecked against the final code/docs immediately before Gate 15
is closed.

## Gate-15 closure path after Gates 13-14

When Gate 13 and Gate 14 have passed:

1. refresh `research/FIDELITY_GAPS.md` against current code;
2. source-close any newly practical small gaps;
3. for every remaining item, move it to either:
   - fixed/resolved,
   - proven irrelevant/superseded, or
   - an explicit **accepted release limitation** with observable effect and
     fail-closed/fallback behavior stated;
4. verify no code/doc comment calls a deterministic fallback original behavior;
5. rerun the full reconstruction suite and repository asset policy;
6. mark Gate 15 complete only after that final reconciliation.

## Gate 16/17 consequence

Gate 16 already has strong work-ahead evidence, including two canonical
three-cycle shipped-data receipts, but remains prevalidated until Gates 13-15
close. Gate 17 must carry every intentionally accepted Gate-15 limitation into
the final non-pre-release `research/RELEASE_LIMITATIONS.md`; the release audit
must not erase them merely to pass.
