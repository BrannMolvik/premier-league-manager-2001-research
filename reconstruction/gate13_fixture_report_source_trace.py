"""Reproducible private-only capture/ownership/input trace for Gate 13.

The report is analyst evidence, never a gameplay report or a completed closure
audit. It neither imports licensed bytes into Git nor downloads original data.
"""
import argparse
import json
from pathlib import Path
import struct

from gate13_button_source_trace import (
    OriginalPE32, OriginalPETraceError, disassemble_window, require_private_output_path,
)
from original_fixture_report_capture import NATIVE_CAPTURE_SCALAR_COPIES


FIXTURE_REPORT_WINDOWS = (
    ('native mouse registration', 0x531CC3, 0x4B),
    ('WM_RBUTTONDOWN callback', 0x5320B0, 0x96),
    ('application right press', 0x5326C0, 0x23),
    ('right press layer dispatch', 0x653D80, 0xF8),
    ('right press child dispatch', 0x653600, 0x90),
    ('generic right press acceptance', 0x64F960, 0xC0),
    ('owner pre-acceptance', 0x42DE00, 0x8),
    ('League Fixtures right press callback', 0x46E620, 0x21),
    ('grid report lookup', 0x46D390, 0x70),
    ('grid hover completed bit', 0x46D400, 0x70),
    ('match report lookup and popup', 0x488C80, 0x160),
    ('calculator capture participant counts', 0x51145B, 0x2D),
    ('developer skip getter', 0x516080, 0x6),
    ('capture helper sequence', 0x60BE50, 0xC0),
    ('capture scalar and helper copies', 0x60B7F0, 0xE0),
    ('capture participants', 0x60B8D0, 0x1B0),
    ('capture score and goal allocation', 0x60BA80, 0x140),
    ('capture possession triplets', 0x60BBC0, 0xF0),
    ('capture participant statistics', 0x60BCB0, 0xE0),
    ('capture goal events', 0x60BD90, 0x90),
    ('capture script', 0x60BE20, 0x30),
    ('capture success link writer', 0x60BF10, 0x80),
    ('ordered list append', 0x617D70, 0x60),
    ('ordered report list load', 0x60BF90, 0x90),
    ('ordered report list save', 0x60C020, 0x37),
    ('report serializer', 0x60B240, 0x230),
    ('report deserializer', 0x60B470, 0x380),
    ('season report owner clear', 0x4F9849, 0x2B),
)


def fixture_report_trace_report(pe: OriginalPE32, *, with_disassembly=False):
    slots = (
        ('PLeagueGrid right press', 0x7C23D0, 0x78, 0x64F960),
        ('PLeagueGrid hover', 0x7C23D0, 0x50, 0x46D400),
        ('PLeagueFixtures pre-acceptance', 0x7C24B8, 0x1C, 0x42DE00),
        ('PLeagueFixtures right press', 0x7C24B8, 0x20, 0x46E620),
        ('LeagueMatch identity', 0x7C4C24, 0x18, 0x6559A0),
    )
    for name, table, slot, expected in slots:
        actual = struct.unpack('<I', pe.read(table + slot, 4))[0]
        if actual != expected:
            raise OriginalPETraceError(f'Native fixture slot calibration failed: {name}')
    windows = []
    for label, va, size in FIXTURE_REPORT_WINDOWS:
        blob = pe.read(va, size)
        window = {'label': label, 'va': va, 'size': len(blob)}
        if with_disassembly:
            window['linear_disassembly_not_cfg'] = disassemble_window(blob, va)
        windows.append(window)
    return {
        'source_sha256': pe.sha256,
        'scope': 'private native evidence; NOT a complete runtime report projection',
        'native_pointer_message': 0x204,
        'capture_count_offsets': [0x5A4, 0xB54],
        'skip_match_calculation_global': 0x877558,
        'owner_global': 0x8755F8,
        'match_link_word_offset': 0x40,
        'scalar_copies': [list(copy) for copy in NATIVE_CAPTURE_SCALAR_COPIES],
        'calibrated_slots': [list(slot) for slot in slots],
        'windows': windows,
        'runtime_capture_production_complete': False,
        'gate13_closed': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--disassemble', action='store_true')
    args = parser.parse_args()
    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = fixture_report_trace_report(pe, with_disassembly=args.disassemble)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'Private fixture-report evidence saved to {args.output}')


if __name__ == '__main__':
    main()
