"""Complete typed 0x60BE50 capture; no score/result-to-context fallback.

This is a modern internal representation, not the original padded 0xF4 image.
Unwritten native allocation bytes are deliberately excluded. Setup metadata
must be retained by its producer; this module cannot manufacture it.
"""
from dataclasses import dataclass

from original_fixture_report_capture import (
    NativeCapturedScalar, NativeCapturedPossession, NativeCapturedGoal,
    NATIVE_CAPTURE_SCALAR_COPIES, LiveReportCompletionScalars,
    NATIVE_CAPTURE_HELPER_SCALAR_COPIES,
    capture_finalized_native_goals,
)
from original_fixture_report_packing import (
    pack_live_native_match_script, pack_live_participant_statistics,
)
from match_postmatch import FinalizedSideParticipantStatistics, FinalizedParticipantStatistics
from native_compact_match import NativeCompactRecord


def report_language_from_database(database):
    """Retain exact loaded language bytes, never English month defaults."""
    table = getattr(database, 'english', None)
    values = getattr(table, 'values', ())
    if len(values) <= 21855:
        return None
    try:
        return (values[21855].encode('cp1252'),
                tuple(values[i].encode('cp1252') for i in range(19718, 19730)))
    except (AttributeError, UnicodeError):
        return None


def format_report_caption(language, competition_caption, played_on):
    """0x5146B0 / 0x64D150 ordinary caption, from source strings only.

    Other language grammars stay unsupported, not heuristically translated.
    The native abbreviated month consumes three BYTES, not Unicode letters.
    """
    if language is None or type(competition_caption) is not str:
        return None
    template, months = language
    if template != b'%C %D{%D %M %Yf}' or len(months) != 12:
        return None
    completion = LiveReportCompletionScalars.from_calculation(played_on, (0, 0))
    year, month, day = completion.calendar
    try:
        name = competition_caption.encode('cp1252')
    except UnicodeError:
        return None
    text = name + b' ' + str(day).encode('ascii') + b' ' + months[month - 1][:3] + b' ' + str(year + 1900).encode('ascii')
    if not name or b'\0' in text or not 0 < len(text) < 64 or len(months[month - 1]) < 3:
        return None
    return text


@dataclass(frozen=True)
class LiveReportSetupFragment:
    """Known setup outputs only; deliberately not accepted as ReportMetadata."""
    caption: bytes | None
    venue_id: int
    environment_copies: tuple[NativeCapturedScalar, ...]


def _uint(value, maximum, label):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f'Invalid {label}')


@dataclass(frozen=True)
class ReportParticipantMetadata:
    player_id: int
    shirt_number: int
    booked_bit: int
    normalized_initial_condition_bit: int

    def __post_init__(self):
        _uint(self.player_id, 0xFFFF, 'report player ID')
        _uint(self.shirt_number, 0x3F, 'report shirt number')
        _uint(self.booked_bit, 1, 'report booking bit')
        _uint(self.normalized_initial_condition_bit, 1, 'initial history bit')


@dataclass(frozen=True)
class ReportMetadata:
    scalar_copies: tuple[NativeCapturedScalar, ...]
    helper_copies: tuple[NativeCapturedScalar, ...]
    caption: bytes
    venue_id: int
    team_ids: tuple[int, int]
    tactics_words: tuple[int, int]
    participants: tuple[tuple[ReportParticipantMetadata, ...], ...]
    # None is the source ordinary non-aggregate context, NOT a guessed score.
    previous_scores: tuple[int, int] | None

    def __post_init__(self):
        expected = NATIVE_CAPTURE_SCALAR_COPIES
        if (type(self.scalar_copies) is not tuple or len(self.scalar_copies) != len(expected)
                or any(type(s) is not NativeCapturedScalar
                       or type(s.value) is not bytes
                       or (s.report_offset, s.calculator_offset, len(s.value)) != e
                       for s, e in zip(self.scalar_copies, expected))):
            raise ValueError('Every required calculator scalar copy must be present in source order')
        expected_helpers = NATIVE_CAPTURE_HELPER_SCALAR_COPIES[:3]
        if (type(self.helper_copies) is not tuple or len(self.helper_copies) != 3
                or any(type(s) is not NativeCapturedScalar or type(s.value) is not bytes
                       or (s.report_offset, s.calculator_offset, len(s.value)) != e
                       for s, e in zip(self.helper_copies, expected_helpers))):
            raise ValueError('All three producer-written +0xFEC helper dwords are mandatory')
        if type(self.caption) is not bytes or b'\0' in self.caption or not 0 < len(self.caption) < 64:
            raise ValueError('Caption requires bounded producer-written text, not padded memory')
        self.caption.decode('cp1252')
        _uint(self.venue_id, 0xFFFF, 'report venue ID')
        for pair, maximum, label in ((self.team_ids, 0xFFFF, 'team identities'),
                                      (self.tactics_words, 0x3FFFF, 'written tactics bits')):
            if type(pair) is not tuple or len(pair) != 2:
                raise ValueError(f'Invalid {label}')
            for value in pair:
                _uint(value, maximum, label)
        if self.team_ids[0] == self.team_ids[1]:
            raise ValueError('Report requires distinct fixture participants')
        if (type(self.participants) is not tuple or len(self.participants) != 2
                or any(type(side) is not tuple or not 11 <= len(side) <= 18
                       or any(type(p) is not ReportParticipantMetadata for p in side)
                       or len({p.player_id for p in side}) != len(side)
                       for side in self.participants)):
            raise ValueError('Complete bounded ordered participant metadata is mandatory')
        if self.previous_scores is not None:
            if type(self.previous_scores) is not tuple or len(self.previous_scores) != 2:
                raise ValueError('Invalid previous-leg context')
            for value in self.previous_scores:
                _uint(value, 15, 'previous score nibble')


@dataclass(frozen=True)
class CompleteFixtureReport:
    fixture_id: int
    metadata: ReportMetadata
    completion: LiveReportCompletionScalars
    statistics: tuple[FinalizedSideParticipantStatistics, ...]
    selected_player_id: int
    possession: NativeCapturedPossession
    goals: tuple[tuple[NativeCapturedGoal, ...], ...]
    script: bytes

    def __post_init__(self):
        _uint(self.fixture_id, 0x7FFFFFFF, 'fixture ID')
        if type(self.metadata) is not ReportMetadata or type(self.completion) is not LiveReportCompletionScalars:
            raise ValueError('Complete producer metadata/calendar/accumulators are mandatory')
        if (type(self.statistics) is not tuple or len(self.statistics) != 2
                or any(type(side) is not FinalizedSideParticipantStatistics for side in self.statistics)):
            raise ValueError('Complete live statistics are mandatory')
        ids = set()
        for side, participants in zip(self.statistics, self.metadata.participants):
            if side.player_ids != tuple(p.player_id for p in participants):
                raise ValueError('Captured participant ownership/order differs from finalizer output')
            ids.update(side.player_ids)
            pack_live_participant_statistics(side.statistics)
        if type(self.selected_player_id) is not int or (
                self.selected_player_id != -1 and self.selected_player_id not in ids):
            raise ValueError('Selected-player output must belong to the captured participants')
        if (type(self.possession) is not NativeCapturedPossession
                or type(self.possession.triplets) is not bytes or len(self.possession.triplets) not in (6, 12)
                or type(self.possession.averages) is not bytes or len(self.possession.averages) != 3):
            raise ValueError('Complete captured possession is mandatory')
        if type(self.goals) is not tuple or len(self.goals) != 2:
            raise ValueError('Both finalized native goal arrays are mandatory')
        for index, goals in enumerate(self.goals):
            # Native allocation uses the low score nibble. Do not silently
            # truncate a mismatch or synthesize its missing goal records.
            if type(goals) is not tuple or len(goals) != (self.completion.scores[index] & 15):
                raise ValueError('Native goal allocation/production is incomplete')
            for goal in goals:
                if type(goal) is not NativeCapturedGoal:
                    raise ValueError('Invalid native goal')
                _uint(goal.player_index, len(self.statistics[index].player_ids) - 1, 'goal participant')
                _uint(goal.minute, 255, 'goal time')
                _uint(goal.inversion, 1, 'goal flag')
        if type(self.script) is not bytes or len(self.script) < 2:
            raise ValueError('Complete native packed script is mandatory')
        if not 2 <= (int.from_bytes(self.script[:2], 'little') & 0x3FF) <= 0x3FF:
            raise ValueError('Packed script count cannot omit native boundaries')


def assemble_complete_fixture_report(fixture_id, result, metadata, statistics, selected_player_id):
    """Return None for absent inputs; malformed supplied inputs reject.

    No owner is changed here. The caller publishes only after all helpers and
    identity checks succeed. This consumes live finalization, never result.score.
    """
    required = (metadata, statistics, selected_player_id, result.native_completion_scalars,
                result.captured_possession, result.native_compact_events)
    if any(value is None for value in required):
        return None
    records = result.native_compact_events
    if (type(records) is not tuple or any(type(r) is not NativeCompactRecord for r in records)
            or not any(r.kind == 6 for r in records) or not any(r.kind == 7 for r in records)
            or tuple(r.minute for r in records) != tuple(sorted(r.minute for r in records))
            or any(r.kind == 7 and r.field(0x24) not in (0, 1, 2) for r in records)):
        raise ValueError('Complete finalized ordered native boundaries are mandatory')
    return CompleteFixtureReport(fixture_id, metadata, result.native_completion_scalars,
                                 statistics, selected_player_id, result.captured_possession,
                                 capture_finalized_native_goals(records),
                                 pack_live_native_match_script(records))


def validate_report_owner(reports, links, fixtures):
    if type(reports) is not tuple or type(links) is not dict or len(reports) > 0x8000:
        raise ValueError('Invalid ordered captured-report owner')
    expected = {}
    for index, report in enumerate(reports):
        if type(report) is not CompleteFixtureReport or report.fixture_id in expected:
            raise ValueError('Report owner requires complete unique fixture captures')
        fixture = fixtures.get(report.fixture_id)
        if fixture is None or report.metadata.team_ids != (fixture.home_club_id, fixture.away_club_id):
            raise ValueError('Report identity does not belong to its original fixture')
        expected[report.fixture_id] = index
    if (any(type(k) is not int or type(v) is not int for k, v in links.items())
            or links != expected):
        raise ValueError('Fixture links must reference their exact ordered report owner')


def snapshot_report(report):
    """Modern explicit save projection; never an original padded memory dump."""
    if type(report) is not CompleteFixtureReport:
        raise ValueError('Only complete captures can be saved')
    m = report.metadata
    return {
        'fixture_id': report.fixture_id,
        'metadata': {
            'scalars': [s.value.hex() for s in m.scalar_copies],
            'helpers': [s.value.hex() for s in m.helper_copies],
            'caption': m.caption.hex(), 'venue_id': m.venue_id,
            'team_ids': list(m.team_ids), 'tactics_words': list(m.tactics_words),
            'participants': [[[p.player_id, p.shirt_number, p.booked_bit,
                               p.normalized_initial_condition_bit] for p in side]
                             for side in m.participants],
            'previous_scores': None if m.previous_scores is None else list(m.previous_scores),
        },
        'calendar': list(report.completion.calendar), 'scores': list(report.completion.scores),
        'statistics': [[list(side.player_ids),
                        [[s.player_index, s.rating, s.skill_flags.hex()] for s in side.statistics]]
                       for side in report.statistics],
        'selected_player_id': report.selected_player_id,
        'possession': [report.possession.triplets.hex(), report.possession.averages.hex()],
        'goals': [[[g.player_index, g.minute, g.inversion] for g in side] for side in report.goals],
        'script': report.script.hex(),
    }


def restore_report(value):
    """Restore every required field without coercing integers or filling holes."""
    try:
        m = value['metadata']
        def scalars(raw, expected):
            if type(raw) is not list or len(raw) != len(expected):
                raise ValueError('Incomplete saved scalar set')
            return tuple(NativeCapturedScalar(d, s, bytes.fromhex(v))
                         for v, (d, s, _) in zip(raw, expected))
        metadata = ReportMetadata(
            scalars(m['scalars'], NATIVE_CAPTURE_SCALAR_COPIES),
            scalars(m['helpers'], NATIVE_CAPTURE_HELPER_SCALAR_COPIES[:3]),
            bytes.fromhex(m['caption']), m['venue_id'], tuple(m['team_ids']),
            tuple(m['tactics_words']),
            tuple(tuple(ReportParticipantMetadata(*p) for p in side) for side in m['participants']),
            None if m['previous_scores'] is None else tuple(m['previous_scores']))
        return CompleteFixtureReport(
            value['fixture_id'], metadata,
            LiveReportCompletionScalars(tuple(value['calendar']), tuple(value['scores'])),
            tuple(FinalizedSideParticipantStatistics(tuple(ids), tuple(
                FinalizedParticipantStatistics(index, rating, bytes.fromhex(flags))
                for index, rating, flags in statistics)) for ids, statistics in value['statistics']),
            value['selected_player_id'], NativeCapturedPossession(*(
                bytes.fromhex(v) for v in value['possession'])),
            tuple(tuple(NativeCapturedGoal(*g) for g in side) for side in value['goals']),
            bytes.fromhex(value['script']))
    except (KeyError, TypeError, IndexError, UnicodeError) as exc:
        raise ValueError('Incomplete or malformed saved captured report') from exc
