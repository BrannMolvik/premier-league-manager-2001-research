# Gate 13 local input performance correction — 9 October 2026

Original contract: the `PLeagueFixtures` page controls belong only to that
panel (`0x25C`, native dispatcher `46E040`, events39/40); their geometry,
pointer acceptance and frames are unchanged. See the already-qualified
`original_fixtures_pager.py` and Recovery433 audit.

Confirmed reconstruction defect: once Fixtures art is resident, the generic
management motion handler calls `_fixtures_page_controls` on Squad/Tables.
That helper previously rebuilt their full data snapshot before discovering
that the panel has no Fixtures controls. A background call-count probe on
the unmodified host measured0 snapshots for100 Squad checks before loading
pager art, and100 after. This does not establish the total user-visible lag.

Minimum correction: use the presenter's authoritative `selected_child_id`
before building any pager snapshot, matching its existing Fixtures-only
guards. No cache, input queue, timer, simulation or native control semantics
change. Active Fixtures still reads current live data; modal suppression is
preserved. Regressions exercise real motion/draw methods with retained art
on Squad/Tables, plus active Fixtures and modal guards.

Remaining unknown: actual Windows end-to-end latency and other redraw costs.
This correction does not repair selected-row backgrounds, Inbox, alternate
Squad views or the unbound ordinary NEXT path, and does not close Gate13.
