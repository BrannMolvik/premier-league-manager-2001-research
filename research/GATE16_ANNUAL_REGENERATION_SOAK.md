# Gate 16 annual-regeneration destructive soak foundation

_Date: 1 October 2026 KST_

## Scope

Gate 16 is not active and is not complete. This is independent cloud-safe
work-ahead under the deferred-blocker policy while Gate 13 still awaits its
real Windows graphical audit.

The file `reconstruction/gate16_annual_regeneration_soak.py` repeatedly
exercises the already recovered annual primary-season replacement boundary. It
does not pretend that those seasons were played. A caller must provide
completed-season qualification evidence before every rollover.

## Destructive invariants

Each cycle requires:

- a newly constructed Premier League runtime object;
- no prior-season Premier League results after install;
- no prior prepared-match environments after install;
- a nonempty regenerated fixture set;
- stable Premier League fixture count across the soak;
- exactly one scheduler occurrence for every regenerated Premier League
  fixture, with no duplicates or omissions;
- controller CRT state equal to the regeneration's committed `state_after`.

The original destructive test deliberately dirties each old season with a
result and a prepared match environment immediately before the next rollover,
then runs 30 consecutive annual replacements. This targets stale-state
accumulation and replacement bugs. Its synthetic ranking is only bounded
qualification input for the rollover primitive; it is not evidence about
original standings or qualification outcomes.

## Combined regeneration/save-growth soak

Gate 16 also needs evidence that the internal save does not silently preserve
replaced season-owned structures. The extended test therefore combines **12
consecutive annual regenerations with 12 exact internal save/reload
round-trips** using the existing 20-club consecutive-season synthetic database.

For each cycle it:

1. installs one bounded synthetic Premier League ranking solely to satisfy the
   already-recovered rollover precondition;
2. dirties the outgoing season with one result and one prepared-match
   environment;
3. regenerates the next annual primary season;
4. requires exactly 380 new Premier League fixtures, zero carried results and
   zero carried prepared environments;
5. records a structural shape over Premier League fixtures/results, scheduler
   entries, primary matchday/shadow state, Cup owners and procedural-League
   owners;
6. serializes the complete schema-34 human-gameplay snapshot, reloads it through
   the source-signature guard, and requires exact before/after snapshot
   equality plus byte-identical compact JSON after reserialization;
7. requires the season-owned structural shape to remain identical across all
   12 cycles.

The compact JSON includes changing dates and CRT states, so exact payload byte
length is not itself stable. The test allows at most a **4 KiB max-minus-min
payload spread** across the 12 saves. This is intentionally a generous
corruption guard, not an original FM2001 behavior claim. Accumulating another
full Premier League schedule or similar replaced season-owned collection would
exceed that bound by far.

## Evidence boundary

Passing these soaks demonstrates repeated destructive regeneration and
save/reload replacement safety. It does not by itself satisfy the Gate-16
criterion that multiple seasons run automatically on canonical shipped data.

Separate Gate-16 work already covers complete synthetic seasons, multiple
deterministic seeds, repeated save/reload during played seasons, autonomous
transfer churn, and mixed shared-primary competition scheduling. Still required
before Gate 16 can close includes canonical real-data multi-season evidence,
additional independent state-growth risk review, and regression-locking any
new failure discovered.

The earliest incomplete validation gate remains Gate 13.
