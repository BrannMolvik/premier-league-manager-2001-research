# Original League comparator integrated into the Premier League table backend

_Status: source-backed comparator integrated; original Gate-13 League table UI
is still incomplete. Synthetic CI is not original-byte visual validation._

## Exact existing original-source evidence

Previously recovered canonical executable comparator `0x4F45E0`, also
recorded in `research/EXECUTABLE_ANALYSIS.md` and already used by
`reconstruction/procedural_league_state.py`, orders League rows by:

1. descending points;
2. ascending games played;
3. descending goal difference;
4. descending goals scored;
5. ascending goals conceded;
6. original DBRClub **short-name CP1252 bytes**, lexical ascending.

The old standalone `PremierLeagueState.table()` implementation omitted
played and goals-conceded comparisons and used club ID as the final
tie-breaker; thus it could display and feed ranking-sensitive management
decisions differently from the recovered original comparator even though
the runtime already has the necessary score and canonical club-name data.

## Implementation and fidelity limits

`competition_state.PremierLeagueState` now centralizes the five
source-recovered numeric fields and accepts an explicit byte-valued
`club_name_key`. A supplied resolver must provide actual CP1252
short-name bytes for **every** participating club. The sorter rejects
indistinguishable complete source keys rather than guessing the original
CRT qsort's equal-key permutation. The legacy no-resolver API remains
compatible for synthetic callers, with a documented deterministic
club-ID fallback **only on numeric ties**.

Completed ranking publication remains conservative: it requires all
fixtures to be recorded. If numeric keys are all distinct, exact
ranking needs no source names; if numeric keys tie, it requires
distinct complete source name bytes and refuses to publish otherwise.

`GameState.premier_league_table()` resolves canonical runtime
`DBRClub.short_name` through strict CP1252 encoding and passes
the byte key to the recovered comparator. Existing original
Premier League standings presentation, match/AI ordering and financial
objective/table-placement paths now consume that same bridge. If a
lightweight synthetic club lacks source names, has an unrepresentable
name, or has truly equal complete keys, GameState retains only the
documented deterministic display fallback; it must not be labelled
exact original ranking.

The bridge is preparation for the eventual source-backed original
Gate-13 manager and table screens. It does **not** draw original
FM2001 table art, invent icon/text placement, identify native
button hover/pressed states, or pass a Windows 11 GUI audit.

## Targeted and full-suite validation

Synthetic tests cover six-field source ordering, numeric played
precedence over goal difference, source byte vs club ID/Unicode
ordering, complete-season exact ranking publication, ambiguous
full-key refusal, and graceful GameState fallback for missing
source names. GitHub full reconstruction CI is scoped to PRs
touching the new table code/tests and its gameplay integration.
The same 21 opt-in original-byte tests remain intentionally
skipped on hosted runners until the existing licensed original
ZIP/executable can actually be accessed by a working private
execution environment.
