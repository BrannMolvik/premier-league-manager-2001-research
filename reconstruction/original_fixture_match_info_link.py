"""Exact native grid/context lookup, without fabricating saved match reports.

0x46CA15..0x46CA24 calls 0x46CDF0 at (378,235). Grid size is 348x336;
0x46D390 reduces points by 29x14. 0x488C80 follows the signed word at
LeagueMatch+0x40 into the source report list, not into a score/result table.
Only source-captured reports may be supplied to this read-only boundary.
"""
GRID_RECT = (378, 235, 348, 336)
CELL_STEP = (29, 14)
GRID_CONTROL_ID = 0x59
REPORT_APPEND_VA = 0x60BF10
REPORT_CAPTURE_VA = 0x60BE50
REPORT_ALLOCATION_SIZE = 0xF4


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
