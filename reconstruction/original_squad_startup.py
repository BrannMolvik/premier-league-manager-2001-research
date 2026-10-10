"""Explicit 404110(mode=1) / temporary-category-2 lineup selection core.

This is the original pre-human first-season producer, not prototype autofill.
Its live 409500/407DF0 context must be qualified before the normal host calls
it. In particular, missing reconstructed secondary state is NOT native null.
No runtime selection, manager formation or save state is mutated here.
"""
from dataclasses import dataclass, replace

from match_lineup import AiLineupCoreResult, select_ai_lineup_core, BENCH_GROUP_ORDER, lineup_group_for_role
from match_role_rating import best_preferred_role_rating
from match_calculator import form_multiplier


FIRST_SEASON_SUBSTITUTE_QUOTA = 2  # Literal push at 40427B.


@dataclass(frozen=True)
class OriginalFirstSeasonSquadSelection:
    formation_id: int
    lineup: AiLineupCoreResult

    @property
    def complete(self) -> bool:
        return not self.lineup.unfilled_slot_indices


def select_first_season_primary_squad(roster, *, formation_id, non_eu_limit):
    """Select after explicitly retained native context, without committing.

    404282 temporarily sets team category 2. 409D44 uses only 418130's
    player+14 low-two-bit availability predicate; bit 2 and Non-EU contract
    expiry are NOT the ordinary 418050 filter at this stage. 409CF7 disables
    restricted-player counting/retry, not the candidate-limit comparison.
    """
    if type(formation_id) is not int or not 0 <= formation_id < 21:
        raise ValueError('First-season native formation context is required')
    if type(non_eu_limit) is not int or not 0 <= non_eu_limit <= 255:
        raise ValueError('First-season native restriction context is required')
    roster = tuple(roster)
    if len(roster) > 40:
        raise ValueError('First-season roster exceeds the native 40-word array')
    # Never silently convert a missing native flag into false.
    for player in roster:
        if any(type(getattr(player, flag, None)) is not bool
               for flag in ('injured', 'suspended', 'non_eu')):
            raise ValueError('First-season native player flag inputs are missing')
    lineup = select_ai_lineup_core(
        roster, formation_id, 0,
        eligible=lambda p: not (p.injured or p.suspended),
        non_eu_limit=non_eu_limit, count_non_eu=False,
    )
    if lineup.unfilled_slot_indices:
        # Native incomplete-XI early return precedes the commit/bench region.
        return OriginalFirstSeasonSquadSelection(formation_id, lineup)
    by_id = {p.player_index: p for p in roster}
    last = by_id[lineup.starters[-1].player_index]
    # 40A393/40A545/40A62A/40A8A9 read the retained last-XI pointer
    # at esp+7C, NOT the candidate just used for the category test. Every
    # candidate therefore has the same ranked-pass score; strict-greater
    # ties retain the first eligible roster member. Preserve this native
    # byte behavior rather than "correcting" it to best candidate ability.
    retained_score = int(best_preferred_role_rating(last.skills, last.preferred_positions)
                         * form_multiplier(last.form_state))
    selected = {p.player_index for p in lineup.starters}
    bench = []
    def eligible(p):
        return (p.player_index not in selected and not (p.injured or p.suspended)
                and (not p.non_eu or non_eu_limit > 0))
    if retained_score > 0:
        for group in BENCH_GROUP_ORDER:
            if len(bench) == FIRST_SEASON_SUBSTITUTE_QUOTA:
                break
            candidate = next((p for p in roster if eligible(p)
                              and lineup_group_for_role(p.preferred_positions[0]) == group), None)
            if candidate is not None:
                bench.append(candidate.player_index)
                selected.add(candidate.player_index)
    for p in roster:
        if len(bench) == FIRST_SEASON_SUBSTITUTE_QUOTA:
            break
        if eligible(p) and lineup_group_for_role(p.preferred_positions[0]) != 3:
            bench.append(p.player_index)
            selected.add(p.player_index)
    lineup = replace(lineup, substitutes=tuple(bench))
    return OriginalFirstSeasonSquadSelection(formation_id, lineup)
