"""Private checksum-gated trace for FM2001 BNK loading/playback format.

Executable ownership is already source-backed for four core banks and their
playback paths. Actual modern playback remains blocked because the BNK sample
table/header/codec structure has not been source-closed.

This tool packages only the already-proven loader and playback neighborhoods for
private analysis. It does not infer a file signature, sample count, offsets,
codec, channels, sample rate, sample names, music semantics, or event mapping.
Generated executable bytes/disassembly must remain private.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    disassemble_window,
    require_private_output_path,
)
from gate14_audio_bank_ownership import (
    ADVICE_PLAYBACK_VA,
    AUDIO_INIT_MENUS_GAME_VA,
    BANK_LOADER_VA,
    GENERIC_SFX_CALLBACK_VA,
    MAIN_AUDIO_BANK_INIT_VA,
    MENUS_PLAYBACK_VA,
    PLAYER_CALLS_LOADER_VA,
    ADVICE_LOADER_VA,
)


class Gate14AudioBankFormatTraceError(OriginalPETraceError):
    pass


BANK_FORMAT_TRACE_WINDOWS = (
    ("shared BNK loader", BANK_LOADER_VA, 0x180),
    ("menus/game bank initialization", AUDIO_INIT_MENUS_GAME_VA, 0x100),
    ("playercalls bank initialization", PLAYER_CALLS_LOADER_VA, 0xC0),
    ("Advice bank initialization", ADVICE_LOADER_VA, 0xC0),
    ("main audio-bank initialization", MAIN_AUDIO_BANK_INIT_VA, 0x180),
    ("menus bank playback helper", MENUS_PLAYBACK_VA, 0x100),
    ("generic runtime SFX callback", GENERIC_SFX_CALLBACK_VA, 0x140),
    ("Advice bank playback helper", ADVICE_PLAYBACK_VA, 0x90),
)


def audio_bank_format_trace_report(
    pe: OriginalPE32,
    *,
    windows=None,
    with_disassembly: bool = True,
) -> dict:
    """Collect bounded BNK loader/playback evidence without format promotion."""
    if type(with_disassembly) is not bool:
        raise Gate14AudioBankFormatTraceError("with_disassembly must be boolean")
    if windows is None:
        windows = BANK_FORMAT_TRACE_WINDOWS

    inspected = []
    for item in tuple(windows):
        if not isinstance(item, tuple) or len(item) != 3:
            raise Gate14AudioBankFormatTraceError(
                "BNK trace windows must be (label, start_va, requested_size)"
            )
        label, start_va, requested_size = item
        if (
            not isinstance(label, str)
            or not label
            or type(start_va) is not int
            or type(requested_size) is not int
            or requested_size <= 0
        ):
            raise Gate14AudioBankFormatTraceError("invalid BNK trace window")
        section, _ = pe.section_for_va(start_va)
        if section.name != ".text":
            raise Gate14AudioBankFormatTraceError(
                f"{label}: expected source-qualified code in .text"
            )
        raw = pe.bounded_window(start_va, requested_size)
        inspected.append(
            {
                "label": label,
                "start_va": start_va,
                "requested_size": requested_size,
                "actual_window_bytes": len(raw),
                "section": section.name,
                "raw_hex": raw.hex(),
                "linear_disassembly_only": (
                    tuple(disassemble_window(raw, start_va))
                    if with_disassembly
                    else None
                ),
                "classification": "bounded_bnk_loader_window_not_cfg_or_format_proof",
            }
        )

    return {
        "source_sha256": pe.sha256,
        "windows": tuple(inspected),
        "bank_loader_va": BANK_LOADER_VA,
        "bank_ownership_recovered": True,
        "playback_entrypoints_recovered": True,
        "bank_header_layout_recovered": False,
        "sample_table_layout_recovered": False,
        "sample_offsets_recovered": False,
        "sample_codec_recovered": False,
        "sample_rate_channels_recovered": False,
        "sample_names_recovered": False,
        "modern_sample_decode_ready": False,
        "bank_role_semantics_recovered": False,
        "event_binding_recovered": False,
        "evidence_limit": (
            "Bank ownership and selected playback entrypoints are source-backed. "
            "These bounded windows do not prove BNK field meanings, sample table "
            "layout, codec parameters, exact sample semantics, or modern decode."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Private JSON evidence path outside the Git repository",
    )
    parser.add_argument("--no-disassembly", action="store_true")
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = audio_bank_format_trace_report(
        pe,
        with_disassembly=not args.no_disassembly,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 BNK format trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
