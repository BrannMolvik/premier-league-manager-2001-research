# Original-File Fidelity Sweep

## Standing priority

Until Daniel explicitly changes this directive, the autonomous worker's **primary job is correctness auditing**, not feature expansion.

The repository contains substantial reconstructed behavior and presentation, and recent external testing plus retrospective review has shown that some mappings, design assumptions and semantic interpretations were wrong despite passing tests. The worker must therefore systematically compare the current reconstruction against the shipped original files, resources and executable and correct discrepancies before expanding into new functionality.

This is a cross-cutting fidelity sweep. The earliest incomplete roadmap gate remains Gate 13, but the worker should treat every currently implemented surface it touches as provisional until it is tied to reproducible original evidence.

## Core rule

**Do not ask "does our implementation work?" first. Ask "is this what the original actually did?"**

Repository tests are useful only after the original contract is established. A self-consistent reconstruction can still be wrong.

## Required audit dimensions

For each audited subsystem or screen, verify all applicable dimensions directly against original evidence:

### Resource mapping
- exact original file/resource identity;
- correct archive/path/basename selection;
- variant/fallback selection rules;
- byte identity or documented compatibility conversion;
- no substituted asset where an original exists.

### Screen/control mapping
- exact screen/window ownership;
- control count and type;
- parent/child relationships;
- construction/destruction order where observable;
- draw/z-order;
- visibility/enabled/disabled rules;
- state transitions.

### Geometry and design
- native coordinate system;
- exact x/y/width/height;
- anchors/alignment;
- clipping regions;
- source/destination rectangles;
- scaling/aspect behavior;
- fullscreen/window relationships;
- no visually plausible layout accepted without source evidence.

### Text and fonts
- exact source string/template;
- localization source;
- exact font resource and size;
- alignment/style flags;
- colors and conditional color predicates;
- truncation/formatting rules.

### Data mapping
- exact original field ownership and meaning;
- units, signedness, widths and sentinel values;
- indexes/IDs;
- runtime-object mapping;
- initialization/default state;
- mutation/lifecycle rules.

### Navigation/input/timing
- exact button/control action;
- input semantics;
- modal/close behavior;
- transition ownership;
- timing/order;
- loading work that belongs before/after a transition;
- no modern shortcut or convenience behavior unless strictly required for Windows 11 compatibility.

### Simulation/gameplay
- exact producer/consumer chain;
- ordering and RNG consumption;
- condition predicates;
- lifecycle/reset/save behavior;
- no inferred rule promoted because it gives plausible results.

### Audio/video/presentation
- source resource identity;
- decode/conversion semantics;
- geometry/aspect/frame treatment;
- event trigger;
- timing/order;
- volume/channel behavior where recoverable.

## Audit method

For every audited item:

1. Identify the current reconstruction implementation and its claim.
2. Recover the corresponding original owner/caller/resource path.
3. Verify the original contract from reproducible evidence.
4. Compare implementation vs original field-by-field / control-by-control.
5. Classify:
   - EXACT / ORIGINAL-PROVEN
   - COMPATIBILITY-EQUIVALENT
   - PARTIAL
   - WRONG
   - UNKNOWN
6. For WRONG:
   - correct to the original if evidence is complete;
   - otherwise remove/isolate/fail-close the unsupported behavior.
7. For UNKNOWN:
   - persist the exact unresolved source question;
   - do not fill it with a guess.
8. Add regression tests that assert the recovered original contract, not merely current implementation output.
9. Record evidence and result in the audit ledger.

## Audit order

Prioritize by player impact and risk of prior incorrect mapping:

1. **Gate 13 visible front end and all shared club-management screens**
   - main menu / TeamSelect;
   - shared PMenu shell;
   - Squad;
   - tactics/team selection;
   - fixtures/results;
   - league table;
   - player profile;
   - transfers;
   - finances;
   - messages/news;
   - training/scouting;
   - shared header/sidebar/navigation controls.
2. Startup media, fullscreen/windowing and input.
3. Match-detail/PPreMatch/FastView/audio presentation already reconstructed.
4. Recently changed gameplay/data mappings and any older implementation whose source interpretation was never independently rechecked.
5. Remaining reconstructed backend systems in risk order.

Southport is only a convenient reproduction fixture for club screens. Verify shared paths and at least one additional club; never introduce club-specific repairs without evidence.

## Evidence standard

Preferred evidence, strongest first:

- canonical original executable instruction/control-flow evidence;
- exact original resource/data files;
- direct source-valid observation of the original game;
- corroborated prior repository trace with reproducible addresses/hashes.

Not sufficient by itself:

- current reconstruction code;
- passing unit tests;
- screenshots of the reconstruction;
- a worker's previous prose claim;
- modern UI conventions;
- visual plausibility;
- expected football-manager behavior.

Where practical, independently re-check important old traces rather than trusting a single earlier interpretation.

## Expansion freeze

While a meaningful fidelity-audit target exists, do **not** choose new feature expansion merely because it is available.

Allowed:
- source investigation;
- audit tooling;
- corrections;
- exact original asset staging;
- fail-closed removal of unsupported behavior;
- Windows 11 compatibility fixes that preserve proven original semantics;
- tests tied to original evidence.

Deprioritized/frozen:
- new reconstructed screens not needed to audit an existing path;
- Gate-14/15/17 work-ahead chosen only to stay busy;
- Settings/upscaling/visual modernization;
- speculative convenience behavior.

If an audit target is blocked by a genuine private/Windows evidence requirement, move to the next highest-value **existing reconstructed surface to audit**, not automatically to new feature work.

## Living ledger requirement

Maintain a fidelity ledger that lists, at minimum:

- subsystem/screen;
- implementation files;
- original owner/resource/evidence;
- dimensions audited;
- status (EXACT / COMPATIBILITY-EQUIVALENT / PARTIAL / WRONG / UNKNOWN);
- discovered discrepancy;
- corrective commit/PR;
- remaining blocker;
- cross-club/cross-state coverage where applicable.

A surface is not "audited" merely because one control or one happy-path state matched.

## Completion standard

This sweep is not complete until:
- every currently implemented player-visible Gate-13 surface has a documented original-evidence comparison;
- all known shared mappings/designs have been checked across representative states;
- known WRONG items are corrected or fail-closed;
- UNKNOWN items are explicit and do not masquerade as original behavior;
- high-risk backend mappings identified by the retrospective audit have been rechecked;
- the next Windows acceptance build contains only audited or explicitly fail-closed behavior on its tested path.

## Recurring original-game completeness check (10 October 2026)

Apply `research/ORIGINAL_REFERENCE_PLAYABILITY_AUDIT_PROTOCOL.md` in addition to this resource/control-level sweep. Each meaningful audit checkpoint must ask which entire **original user-visible screen, menu action, alternate path, postmatch step, gameplay event phase or persistence route** is absent in the reconstructed player journey. Check original sources frequently, retain source-vs-running-original-vs-Windows-acceptance distinctions, and surface the highest-impact omission to Codex. Do not spend unlimited cycles perfecting small already-known source details while the complete gameplay loop remains unusable. Audit-only privileges unchanged.
