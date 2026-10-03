"""Exact native grid/context lookup, without fabricating saved match reports.

0x46CA15..0x46CA24 calls 0x46CDF0 at (378,235). Grid size is 348x336;
0x46D390 reduces points by 29x14. 0x488C80 follows the signed word at
LeagueMatch+0x40 into the source report list, not into a score/result table.
Only source-captured reports may be supplied to this read-only boundary.
"""
from dataclasses import dataclass

GRID_RECT = (378, 235, 348, 336)
CELL_STEP = (29, 14)
GRID_CONTROL_ID = 0x59
REPORT_APPEND_VA = 0x60BF10
REPORT_CAPTURE_VA = 0x60BE50
REPORT_ALLOCATION_SIZE = 0xF4
REPORT_OWNER_CALLBACK_VA = 0x46E620
REPORT_CONTROL_INPUT_VA = 0x64F960
REPORT_CONTROL_INPUT_SLOT = 0x78
REPORT_LIST_LOAD_VA = 0x60BF90
REPORT_LIST_SAVE_VA = 0x60C020


@dataclass(frozen=True)
class SourceFixtureMatchInfoContext:
    fixture_id: int
    link_word: int
    captured_report: object

    def __post_init__(self):
        if type(self.fixture_id) is not int or self.fixture_id < 0:
            raise ValueError('Source fixture identity must be an integer')
        if type(self.link_word) is not int or not 0 <= self.link_word < 0x8000:
            raise ValueError('Resolved source context requires a nonnegative signed link')
        if self.captured_report is None:
            raise ValueError('Resolved source context cannot have a null report')


def source_report_capture_eligible(
    home_participant_count: int,
    away_participant_count: int,
    *,
    skip_match_calculation: bool,
) -> bool:
    """0x51145B..70 and 0x60BE50's 0x516080 rejection, not a result gate.

    This proves eligibility only. It does NOT create a report or claim that
    NormalMatchResult contains all the fields copied by the native helpers.
    The two calculator fields +0x5A4/+0xB54 are counts, not pointers.
    """
    for count in (home_participant_count, away_participant_count):
        if type(count) is not int or not 0 <= count <= 0xFFFFFFFF:
            raise ValueError('Native participant count must be an unsigned dword')
    if type(skip_match_calculation) is not bool:
        raise ValueError('Native developer switch must be boolean')
    return bool(home_participant_count and away_participant_count
                and not skip_match_calculation)


def source_fixture_report_control_accepts(source_flags: int) -> bool:
    """Native vtable +0x78 pre-owner gate: enabled, not already right-pressed.

    Coordinate routing and the owner's +0x1C pre-acceptance callback must have
    succeeded separately. Do not substitute the left-press method 0x64F7A0.
    """
    if type(source_flags) is not int or not 0 <= source_flags <= 0xFFFFFFFF:
        raise ValueError('Source control flags must be an unsigned dword')
    return bool(source_flags & 2 and not source_flags & 0x20)


def source_fixture_report_hover_accepts(fixture_status: int | None) -> bool:
    """0x46D400 requires a non-null matrix fixture and native +0x44 bit zero.

    This is the independent native hover gate; it does not establish a report
    link. In particular, completion alone must never construct a context.
    """
    if fixture_status is None:
        return False
    if type(fixture_status) is not int or not 0 <= fixture_status <= 0xFFFFFFFF:
        raise ValueError('Native fixture status must be an unsigned dword')
    return bool(fixture_status & 1)


def fixture_cell_at_screen_point(x: int, y: int):
    if type(x) is not int or type(y) is not int:
        raise ValueError('Fixture pointer coordinates must be integers')
    left, top, width, height = GRID_RECT
    if not (left <= x < left + width and top <= y < top + height):
        return None
    return ((x - left) // CELL_STEP[0], (y - top) // CELL_STEP[1])


def resolve_source_match_info_link(link_word: int, captured_reports: tuple):
    """Mirror signed-word lookup; retain the native sentinel/null no-op."""
    if type(link_word) is not int or not 0 <= link_word <= 0xFFFF:
        raise ValueError('Source match-info link must be an unsigned 16-bit word')
    if not isinstance(captured_reports, tuple):
        raise ValueError('Source report-list snapshot must be immutable')
    # 0xFFFF is explicit sentinel. Other negative signed words cannot reach
    # zero before a finite linked chain ends, so also produce no context.
    if link_word >= 0x8000 or link_word >= len(captured_reports):
        return None
    return captured_reports[link_word]
