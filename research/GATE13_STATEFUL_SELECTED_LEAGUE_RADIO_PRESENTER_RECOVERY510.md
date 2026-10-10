# Recovery510: transactional native event seam for selected League Fixtures

11 October 2026 KST. Based on main `49841fb13889f7178b1550170e6cb3b506096807`, after audited/merged #575. **Gate13 OPEN**.

## Grounded input/data boundary

Original `PLeagueFixtures::0x46E040` event IDs 1..8 choose the country and 9..14 choose one of up to six constructed League radios. Recovery506 has the original constructor control rectangles, but **does not prove** native fmRadioTextSm pointer hit-test/acceptance, ownership, caption/pixel fidelity or the current Tk host's normal GUI click routing. Recovery507 established the original eight country-index defaults, with only the managed country's index overwritten at startup. Recovery508/509 supply source-strict selected-League ranking and original 373-head primary fixture calendar/results for qualified non-Premier Leagues. Original Premier League0 retains a different source producer and MUST NOT be silently translated to another division.

## Implemented

`original_management_presenter.py` now has an explicit **non-pointer**, source-accepted `source_accepted_league_fixtures_radio_event(event_id)` route. It resolves the canonical manager/current source selector context on first use, applies the already-verified native event-index machine, builds the exact selected original non-PL source grid and presenter snapshot, then atomically updates the per-country selected indices and resets the fixture page to zero. Invalid/nonconstructed radios, unsupported Premier0 selection, missing source or incomplete 373-head data cannot mutate the currently committed selection. Snapshot, source paging and existing grid/report reads use the committed selection; freshly constructed PMenu navigation resets it. The original current-manager fixture path remains untouched until a validated radio transition.

Five focused tests use the real Recovery509 fixture-source bridge (only an unrelated navigation/shell test backend is stubbed). They verify Southport349 Conference7→English Division1 competition2, actual recorded score/date, no forged PMatchInfo numeric IDs, failure atomicity for unsupported countries/PL0/hidden radios, and reset on panel reconstruction. CI tests should be checked at the exact PR head before merger.

## Not demonstrated

This does not connect or permit real GUI mouse clicks, native hit acceptance, sprites/captions, original Premier0 alternate-selection data, full League Tables country/division/current-form controls, the protected Codex R1 match lifecycle, or a Windows11 player click-through. A source-exact native control event/child ownership trace is required **before** GUI pointer integration. Do not claim Gate13, Gates14–17 or verified release complete.
