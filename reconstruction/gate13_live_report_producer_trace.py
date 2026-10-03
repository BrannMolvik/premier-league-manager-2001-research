"""Private evidence for missing live compact-list production (not report data)."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from gate13_button_source_trace import (
    OriginalPE32, OriginalPETraceError, require_private_output_path,
    disassemble_window,
)

SOURCE_SHA256 = '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'
LIVE_PRODUCER_WINDOWS = (
    ('calculator constructor', 0x62ABD0, 0x92),
    ('calculator initialization', 0x62AC90, 0x150),
    ('FullTime outcome getter', 0x62AE00, 0x81),
    ('ordinary phase production', 0x62AE90, 0x306),
    ('boundary row normalization', 0x62B3F0, 0x233),
    ('post-row random and status update', 0x62B6D0, 0x90),
    ('native compact-list finalizer', 0x62F7C0, 0x3E1),
    ('calculation to finalizer', 0x62FBC0, 0x2F),
    ('native boundary time correction and ordering', 0x62FBF0, 0x199),
    ('compact record base constructor', 0x6325E0, 0x1A),
    ('FullTime compact record constructor', 0x632660, 0x1C),
    ('ordinary previous-score initialization', 0x510E55, 0x15),
    ('two-leg previous-score override', 0x511120, 0x4C),
    ('chance compact fields', 0x62ECF0, 0x12C),
    ('free-kick compact fields', 0x62EE20, 0x7D),
    ('penalty compact fields', 0x62EEA0, 0x7D),
    ('incident compact fields', 0x62EF20, 0x70),
    ('substitution compact fields', 0x62F000, 0xAC),
    ('open-play constructor argument flow', 0x62C740, 0x600),
    ('report player shirt-number accessor', 0x41E3F0, 0x10),
    ('report selected player output', 0x631110, 0x127),
)


def live_report_producer_trace(pe, *, with_disassembly=False):
    if pe.sha256 != SOURCE_SHA256:
        raise OriginalPETraceError('Live producer trace requires the canonical executable')
    windows = []
    for label, address, size in LIVE_PRODUCER_WINDOWS:
        blob = pe.read(address, size)
        window = {'label': label, 'va': address, 'size': size,
                  'sha256': sha256(blob).hexdigest()}
        if with_disassembly:
            window['linear_disassembly_not_cfg'] = disassemble_window(blob, address)
        windows.append(window)
    return {'source_sha256': pe.sha256, 'windows': windows,
            'scope': 'private analyst evidence, NOT a runtime captured report',
            'runtime_capture_production_complete': False,
            'normal_pmatchinfo_opening_verified': False, 'gate13_closed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--disassemble', action='store_true')
    args = parser.parse_args()
    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = live_report_producer_trace(pe, with_disassembly=args.disassemble)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'Private live-producer evidence saved to {args.output}')


if __name__ == '__main__':
    main()
