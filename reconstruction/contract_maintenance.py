"""Source-backed FM2001 monthly player-contract maintenance.

This module reconstructs the non-user-club branch of DBRPlayer::0x41ABC0.
The separate user-controlled 0x41BEE0 expiry/event path is intentionally not
collapsed into this routine.
"""

from __future__ import annotations

from datetime import date, timedelta
from dataclasses import dataclass
from enum import Enum

from match_postmatch import MoraleSettings, increase_player_morale
from match_role_rating import best_preferred_role_rating
from player_contract import contract_expiry_from_month_span


CONTRACT_DECISION_WINDOW_DAYS = 30
LOW_RATING_BOUNDARY = 50
LOW_RATING_RELEASE_ROLL = 8
HIGH_RATING_RELEASE_ROLL = 2
RELEASE_MIN_ROSTER_EXCLUSIVE = 18
RELEASE_MIN_TENURE_WEEKS_EXCLUSIVE = 104
RELEASE_MIN_AGE_EXCLUSIVE = 23
AI_RENEWAL_MONTHS = 12


class AiContractMaintenanceOutcome(str, Enum):
    NOT_DUE = "not_due"
    RENEWED = "renewed"
    OUT_OF_CONTRACT = "out_of_contract"


CONTROLLED_OUT_OF_CONTRACT_LEAD_DAYS = 21
CONTROLLED_SUGGESTION_LEAD_DAYS = 112
CONTROLLED_DETACH_GRACE_DAYS = 21
CONTROLLED_SUGGESTION_ROLL_BOUND = 10
CONTROLLED_SUGGESTION_ROLL_SUCCESS = 4
CONTROLLED_SPECIAL_STATE_MIN = 0xFE


class ContractRenewalSuggestionKind(str, Enum):
    ORDINARY = "ordinary"
    BOSMAN = "bosman"


@dataclass(frozen=True)
class ContractRenewalSuggestion:
    """Materialized MPMEAMail payload produced by controlled 0x41BEE0."""

    player_id: int
    queued_on: date
    kind: ContractRenewalSuggestionKind

    @property
    def message_id(self) -> int:
        return 0x1B7 if self.kind is ContractRenewalSuggestionKind.BOSMAN else 0x0E

    @property
    def event_class(self) -> str:
        if self.kind is ContractRenewalSuggestionKind.BOSMAN:
            return "EAMAssManSuggestBosmanPlayerContractRenewalMsub"
        return "EAMAssManSuggestPlayerContractRenewalMsub"

    @property
    def original_key(self) -> str:
        if self.kind is ContractRenewalSuggestionKind.BOSMAN:
            return "AssManSuggestBosmanPlayerContractRenewalM"
        return "AssManSuggestPlayerContractRenewalM"

    @property
    def accepted_action_class(self) -> str:
        return "EAMAmendContractsub"


class ControlledContractMaintenanceOutcome(str, Enum):
    NOT_DUE = "not_due"
    SPECIAL_STATE_DEFERRED = "special_state_deferred"
    PRE_EXPIRY_NO_SUGGESTION = "pre_expiry_no_suggestion"
    SUGGESTION_SUPPRESSED_PENDING_WORKFLOW = "suggestion_suppressed_pending_workflow"
    SUGGEST_ORDINARY_RENEWAL = "suggest_ordinary_renewal"
    SUGGEST_BOSMAN_RENEWAL = "suggest_bosman_renewal"
    EXPIRED_GRACE = "expired_grace"
    DETACHED_OUT_OF_CONTRACT = "detached_out_of_contract"
    NOT_IN_REGISTERED_ROSTER = "not_in_registered_roster"


def completed_club_weeks(player, on_date: date) -> int:
    """Return the 0x419390 completed-week tenure used by 0x41ABC0."""
    joined = player.current_club_join_date
    if joined is None or joined > on_date:
        return 0
    return (on_date - joined).days // 7


def _release_eligibility_passes(player, on_date: date, roster_count: int) -> bool:
    """Reproduce the non-random release gates after 0x41ABC0 selects release."""
    if int(roster_count) <= RELEASE_MIN_ROSTER_EXCLUSIVE:
        return False
    if completed_club_weeks(player, on_date) <= RELEASE_MIN_TENURE_WEEKS_EXCLUSIVE:
        return False

    age = player.age(on_date)
    if age is None or int(age) <= RELEASE_MIN_AGE_EXCLUSIVE:
        return False

    # 0x417580 succeeds only when 0x417460 is false and the two club IDs
    # match. 0x417460 is exactly signed player+0x64 > -1. RuntimePlayer's
    # loan_club_id models the unequal temporary/current-club state.
    if int(player.ai_transfer_block_value_64) > -1:
        return False
    if player.loan_club_id is not None:
        return False
    return True


def run_ai_monthly_contract_maintenance(
    player,
    *,
    on_date: date,
    roster_count: int,
    rng,
) -> AiContractMaintenanceOutcome:
    """Reproduce the non-user branch of DBRPlayer::0x41ABC0.

    More than 30 days before expiry this consumes no RNG. Inside the decision
    window it preserves the exact one/two shared-CRT RNG(100) call pattern.

    A successful release branch sets the source-backed states materialized by
    the clean-room runtime: transfer-listed, Out of contract and +0xC0 = 0.
    The player is not detached from club IDs here because 0x41ABC0 itself does
    not perform the explicit 0x4177C0 free-player detachment.

    Every other due branch renews from the existing expiry by exactly 12
    calendar months through the recovered 0x419190 path and applies the mapped
    0x419210 clears.
    """
    expiry = player.contract_expiry_date
    if expiry is None:
        return AiContractMaintenanceOutcome.NOT_DUE
    if on_date + timedelta(days=CONTRACT_DECISION_WINDOW_DAYS) < expiry:
        return AiContractMaintenanceOutcome.NOT_DUE
    if not hasattr(rng, "randbelow"):
        raise TypeError("rng must provide randbelow(bound)")

    rating = best_preferred_role_rating(
        player.current_raw,
        player.positions,
    )

    first_roll = int(rng.randbelow(100))
    release_candidate = bool(
        first_roll < LOW_RATING_RELEASE_ROLL
        and int(rating) < LOW_RATING_BOUNDARY
    )

    if not release_candidate:
        second_roll = int(rng.randbelow(100))
        release_candidate = bool(
            second_roll < HIGH_RATING_RELEASE_ROLL
            and int(rating) >= LOW_RATING_BOUNDARY
        )

    if release_candidate and _release_eligibility_passes(
        player,
        on_date,
        int(roster_count),
    ):
        # 0x41B530 precedes the bit-7 set on this path.
        player.transfer_listed = True
        player.out_of_contract = True
        # 0x41AC7E zeros the neutral DBRPlayer+0xC0 byte.
        player.startup_month_span = 0
        return AiContractMaintenanceOutcome.OUT_OF_CONTRACT

    player.contract_expiry_date = contract_expiry_from_month_span(
        expiry,
        AI_RENEWAL_MONTHS,
    )
    # 0x419190 converges on 0x419210.
    player.out_of_contract = False
    player.signed_for_other_club = False
    # 0x419190 converges on 0x419210, whose final mapped byte write clears
    # the controlled-renewal suggestion latch at DBRPlayer+0x164 and then
    # applies SignedNewContactMorale through one shared RNG(2).
    player.contract_renewal_suggestion_pending = False
    age = player.age(on_date)
    if age is None:
        raise ValueError(f"player {int(player.index)} has no usable age")
    current_raw = tuple(int(value) for value in player.current_raw)
    if len(current_raw) <= 15:
        raise ValueError(f"player {int(player.index)} has no leadership skill")
    morale_settings = MoraleSettings()
    player.morale = increase_player_morale(
        int(player.morale),
        int(morale_settings.signed_new_contract),
        int(age),
        int(current_raw[15]),
        rng,
        morale_settings,
    )
    return AiContractMaintenanceOutcome.RENEWED


def _controlled_bosman_suggestion(player, on_date: date) -> bool:
    """Reproduce 0x41E5A0 as used by controlled renewal suggestions."""
    age = player.age(on_date)
    return bool(
        age is not None
        and int(age) >= 24
        and int(player.eu_status_code) == 2
    )


def run_controlled_monthly_contract_maintenance(
    player,
    *,
    on_date: date,
    rng,
    in_registered_roster: bool = True,
    pending_contract_workflow: bool = False,
) -> ControlledContractMaintenanceOutcome:
    """Reproduce the ordinary user-controlled portion of DBRPlayer::0x41BEE0.

    The source-backed special path for player+0x138 values 0xFE/0xFF remains
    deliberately deferred. Fresh DBRPlayer construction initializes +0x138 to
    zero, so ordinary reachable clean-room players use the path implemented
    here.

    Pre-expiry:
    - set Out of contract from 21 days before expiry;
    - open the assistant-manager suggestion window at 112 days;
    - when the +0x164 latch is clear, consume exactly one shared RNG(10);
    - only rolls 0..3 continue to the pending-workflow suppression check;
    - successful construction sets +0x164 and returns the exact ordinary/Bosman
      event kind without auto-renewing the contract.

    At/after expiry:
    - only rostered registered-club players are processed;
    - active loans return first;
    - mapped suspension/transfer/out-of-contract/loan-list/status-bit-9 state is
      cleared before the grace test;
    - ordinary players detach only when current_date-21 >= expiry.
    """
    expiry = player.contract_expiry_date
    if expiry is None:
        return ControlledContractMaintenanceOutcome.NOT_DUE

    special_state = int(getattr(player, "contract_special_state_138", 0))
    if special_state >= CONTROLLED_SPECIAL_STATE_MIN:
        return ControlledContractMaintenanceOutcome.SPECIAL_STATE_DEFERRED

    if on_date < expiry:
        if on_date + timedelta(days=CONTROLLED_OUT_OF_CONTRACT_LEAD_DAYS) >= expiry:
            player.out_of_contract = True

        if on_date + timedelta(days=CONTROLLED_SUGGESTION_LEAD_DAYS) < expiry:
            return ControlledContractMaintenanceOutcome.PRE_EXPIRY_NO_SUGGESTION

        if bool(getattr(player, "contract_renewal_suggestion_pending", False)):
            return ControlledContractMaintenanceOutcome.PRE_EXPIRY_NO_SUGGESTION

        if not hasattr(rng, "randbelow"):
            raise TypeError("rng must provide randbelow(bound)")
        roll = int(rng.randbelow(CONTROLLED_SUGGESTION_ROLL_BOUND))
        if roll >= CONTROLLED_SUGGESTION_ROLL_SUCCESS:
            return ControlledContractMaintenanceOutcome.PRE_EXPIRY_NO_SUGGESTION

        # 0x41C6F0 is tested only after the successful RNG(10) branch.
        if bool(pending_contract_workflow):
            return (
                ControlledContractMaintenanceOutcome
                .SUGGESTION_SUPPRESSED_PENDING_WORKFLOW
            )

        player.contract_renewal_suggestion_pending = True
        if _controlled_bosman_suggestion(player, on_date):
            return ControlledContractMaintenanceOutcome.SUGGEST_BOSMAN_RENEWAL
        return ControlledContractMaintenanceOutcome.SUGGEST_ORDINARY_RENEWAL

    if not bool(in_registered_roster):
        return ControlledContractMaintenanceOutcome.NOT_IN_REGISTERED_ROSTER

    # 0x41AA50 returns a loaned player before the common expiry cleanup.
    player.loan_club_id = None

    # Materialized subset of the common status cleanup at 0x41BFB2..0x41BFE6
    # plus 0x41EDF0's proven loan-list clear.
    player.suspended = False
    player.out_of_contract = False
    player.transfer_listed = False
    player.ai_transfer_status_bit_9 = False
    player.loan_listed = False

    if on_date - timedelta(days=CONTROLLED_DETACH_GRACE_DAYS) < expiry:
        return ControlledContractMaintenanceOutcome.EXPIRED_GRACE

    old_club_id = int(player.club_id)
    player.out_of_contract = True
    player.previous_club_id_74 = old_club_id
    # 0x41EF00 removes the player from the club roster separately; GameState
    # owns that container mutation. The DBRPlayer club IDs themselves become -1.
    player.club_id = -1
    player.loan_club_id = None
    return ControlledContractMaintenanceOutcome.DETACHED_OUT_OF_CONTRACT
