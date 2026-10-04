"""Private evidence for missing live compact-list production (not report data)."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from gate13_button_source_trace import (
    OriginalPE32, OriginalPETraceError, require_private_output_path,
    disassemble_window,
)
from gate13_remaining_field_source_trace import REMAINING_GATE13_FIELDS

SOURCE_SHA256 = '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'
REMAINING_SETUP_WINDOWS = (
    # Known lifecycle neighborhoods only. These windows do not claim that the
    # unresolved writer necessarily lives inside them.
    ('compact club import around +0x130/+0x13C/+0x140', 0x403660, 0x320),
    ('DBRClub constructor around unresolved legacy fields', 0x405A40, 0x1C0),
    ('human-opponent D48 adjustment helper', 0x408170, 0x2A0),
    ('primary/secondary player selector accessor', 0x41E3D0, 0x30),
    ('club player-assignment record initializer', 0x61C460, 0x90),
    ('club player-assignment table initializer', 0x61C9C0, 0x180),
    ('gate attendance/counter/capacity neighborhood', 0x5DB900, 0x120),
)
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
    ('report calendar setup', 0x632550, 0x27),
    ('report calendar conversion', 0x64CCD0, 0xF9),
    ('report caption formatter', 0x5146B0, 0x378),
    ('report caption language binding', 0x64C7A2, 0x32),
    ('report month language bindings', 0x636FEC, 0x197),
    ('report date formatter', 0x64D120, 0x2B8),
    ('report venue owner selection', 0x514220, 0xB0),
    ('report referee setup', 0x510F40, 0x78),
    ('report referee catalog selection', 0x421BA0, 0x90),
    ('report attendance scalar assignment', 0x5DB6FA, 0xCF),
    ('report attendance classification combination', 0x5DBDE0, 0x1A),
)



def bounded_remaining_setup_memory_candidates(pe) -> tuple[dict, ...]:
    """Classify exact unresolved-field operands only inside approved setup windows.

    This is a linear, bounded analyst aid. Access direction and register context
    come from Capstone metadata; neither proves the base object is DBRClub/player
    nor that an instruction is reachable in the fresh-game lifecycle.
    """
    if pe.sha256 != SOURCE_SHA256:
        raise OriginalPETraceError(
            'Bounded remaining-setup access trace requires the canonical executable'
        )
    try:
        from capstone import (
            CS_AC_READ,
            CS_AC_WRITE,
            CS_ARCH_X86,
            CS_MODE_32,
            Cs,
        )
        from capstone.x86 import X86_OP_MEM
    except ImportError as exc:
        raise OriginalPETraceError(
            'Bounded setup access trace requires pip install "capstone>=5,<6"'
        ) from exc

    labels_by_displacement: dict[int, tuple[str, ...]] = {}
    for label, displacement in REMAINING_GATE13_FIELDS:
        existing = labels_by_displacement.get(int(displacement), ())
        labels_by_displacement[int(displacement)] = existing + (str(label),)

    engine = Cs(CS_ARCH_X86, CS_MODE_32)
    engine.detail = True
    engine.skipdata = True
    candidates: list[dict] = []

    for window_label, address, size in REMAINING_SETUP_WINDOWS:
        blob = pe.read(address, size)
        for insn in engine.disasm(blob, address):
            if insn.id == 0:
                continue
            for operand_index, operand in enumerate(insn.operands):
                if operand.type != X86_OP_MEM:
                    continue
                displacement = int(operand.mem.disp)
                field_labels = labels_by_displacement.get(displacement)
                if field_labels is None:
                    continue
                access = int(getattr(operand, 'access', 0))
                reads = bool(access & CS_AC_READ)
                writes = bool(access & CS_AC_WRITE)
                if reads and writes:
                    access_kind = 'read_write'
                elif reads:
                    access_kind = 'read'
                elif writes:
                    access_kind = 'write'
                else:
                    access_kind = 'unknown'

                candidates.append(
                    {
                        'window_label': window_label,
                        'window_va': int(address),
                        'candidate_instruction_va': int(insn.address),
                        'candidate_operand_index': int(operand_index),
                        'candidate_displacement': displacement,
                        'candidate_field_labels': field_labels,
                        'candidate_access': access_kind,
                        'candidate_mnemonic': insn.mnemonic,
                        'candidate_operands': insn.op_str,
                        'candidate_bytes': bytes(insn.bytes).hex(),
                        'base_register': (
                            insn.reg_name(operand.mem.base)
                            if operand.mem.base
                            else None
                        ),
                        'index_register': (
                            insn.reg_name(operand.mem.index)
                            if operand.mem.index
                            else None
                        ),
                        'scale': int(operand.mem.scale),
                        'classification': (
                            'bounded_linear_candidate_not_cfg_or_object_proof'
                        ),
                    }
                )

    return tuple(candidates)


def live_report_producer_trace(
    pe,
    *,
    with_disassembly=False,
    metadata_only=False,
    remaining_setup_only=False,
    classify_remaining_field_accesses=False,
):
    if pe.sha256 != SOURCE_SHA256:
        raise OriginalPETraceError('Live producer trace requires the canonical executable')
    if metadata_only and remaining_setup_only:
        raise ValueError('Choose either metadata-only or remaining-setup-only, not both')
    if classify_remaining_field_accesses and not remaining_setup_only:
        raise ValueError(
            'Remaining-field access classification requires remaining-setup-only'
        )
    windows = []
    selected = (
        REMAINING_SETUP_WINDOWS
        if remaining_setup_only
        else LIVE_PRODUCER_WINDOWS[21:]
        if metadata_only
        else LIVE_PRODUCER_WINDOWS
    )
    for label, address, size in selected:
        blob = pe.read(address, size)
        window = {'label': label, 'va': address, 'size': size,
                  'sha256': sha256(blob).hexdigest()}
        if with_disassembly:
            window['linear_disassembly_not_cfg'] = disassemble_window(blob, address)
        windows.append(window)
    report = {'source_sha256': pe.sha256, 'windows': windows,
              'scope': 'private analyst evidence, NOT a runtime captured report',
              'remaining_setup_trace_complete': False,
            'legacy_capacity_writer_identified': False,
              'runtime_capture_production_complete': False,
              'normal_pmatchinfo_opening_verified': False, 'gate13_closed': False}
    if classify_remaining_field_accesses:
        report['bounded_remaining_field_access_candidates'] = list(
            bounded_remaining_setup_memory_candidates(pe)
        )
        report['bounded_access_semantics_recovered'] = False
        report['bounded_access_evidence_limit'] = (
            'Capstone access direction plus exact displacement/register context '
            'inside source-qualified windows only. Candidate hits do not prove '
            'DBRClub/player object identity, reachable CFG, fresh-game writer '
            'ownership, initialization semantics, or runtime lifecycle.'
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--disassemble', action='store_true')
    parser.add_argument('--metadata-only', action='store_true',
                        help='Skip already recovered compact/stat/goal windows')
    parser.add_argument(
        '--remaining-setup-only',
        action='store_true',
        help='Trace only unresolved Gate-13 setup lifecycle neighborhoods',
    )
    parser.add_argument(
        '--classify-remaining-field-accesses',
        action='store_true',
        help=(
            'Inside --remaining-setup-only, classify exact unresolved-field '
            'memory operands as read/write candidates without semantic promotion'
        ),
    )
    args = parser.parse_args()
    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = live_report_producer_trace(
        pe,
        with_disassembly=args.disassemble,
        metadata_only=args.metadata_only,
        remaining_setup_only=args.remaining_setup_only,
        classify_remaining_field_accesses=args.classify_remaining_field_accesses,
    )
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'Private live-producer evidence saved to {args.output}')


if __name__ == '__main__':
    main()
