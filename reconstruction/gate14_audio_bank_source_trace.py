"""Private checksum-gated discovery of executable-embedded FM2001 .bnk strings.

This tool is intentionally an evidence collector, not an audio semantic mapper.
It accepts only the canonical original executable through OriginalPE32, finds
null-terminated printable ASCII strings whose suffix is .bnk, and records raw
little-endian pointer-byte occurrences to each string VA.

A raw pointer-byte occurrence is NOT a validated x86 reference, loader call,
bank role, sample mapping, menu-music binding, or match-event binding. Those
require later control-flow adjudication against the private original bytes.

No proprietary executable bytes or trace output belong in Git.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from gate13_button_source_trace import (
    OriginalPE32,
    OriginalPETraceError,
    require_private_output_path,
)


BNK_SUFFIX = b".bnk"
MAX_EMBEDDED_STRING_BYTES = 1024


class Gate14AudioBankTraceError(OriginalPETraceError):
    pass


def _printable_ascii(value: int) -> bool:
    return 0x20 <= value <= 0x7E


def embedded_bnk_string_candidates(
    pe: OriginalPE32,
    *,
    max_strings: int = 512,
    max_pointer_candidates: int = 256,
) -> tuple[dict, ...]:
    """Return neutral embedded .bnk string candidates and raw pointer hits."""
    if type(max_strings) is not int or max_strings < 1:
        raise Gate14AudioBankTraceError("max_strings must be positive")
    if type(max_pointer_candidates) is not int or max_pointer_candidates < 1:
        raise Gate14AudioBankTraceError("max_pointer_candidates must be positive")

    found: list[dict] = []
    needle = BNK_SUFFIX + b"\x00"
    for section in pe.sections:
        blob = pe.data[
            section.raw_offset:section.raw_offset + section.file_backed_size
        ]
        lower = blob.lower()
        search_at = 0
        while True:
            suffix_at = lower.find(needle, search_at)
            if suffix_at < 0:
                break
            end = suffix_at + len(BNK_SUFFIX)
            start = suffix_at
            while (
                start > 0
                and end - (start - 1) <= MAX_EMBEDDED_STRING_BYTES
                and _printable_ascii(blob[start - 1])
            ):
                start -= 1

            raw = blob[start:end]
            if (
                raw
                and len(raw) <= MAX_EMBEDDED_STRING_BYTES
                and all(_printable_ascii(value) for value in raw)
                and raw.lower().endswith(BNK_SUFFIX)
            ):
                string_va = pe.image_base + section.virtual_address + start
                found.append(
                    {
                        "string_va": string_va,
                        "section": section.name,
                        "embedded_text": raw.decode("ascii"),
                        "classification": (
                            "embedded_null_terminated_ascii_bnk_candidate_only"
                        ),
                        "raw_pointer_byte_candidates_not_proven_xrefs": (
                            pe.pointer_byte_candidates(
                                string_va,
                                max_matches=max_pointer_candidates,
                            )
                        ),
                    }
                )
                if len(found) >= max_strings:
                    return tuple(found)
            search_at = suffix_at + len(needle)
    return tuple(found)


def audio_bank_trace_report(
    pe: OriginalPE32,
    *,
    max_strings: int = 512,
    max_pointer_candidates: int = 256,
) -> dict:
    candidates = embedded_bnk_string_candidates(
        pe,
        max_strings=max_strings,
        max_pointer_candidates=max_pointer_candidates,
    )
    return {
        "source_sha256": pe.sha256,
        "candidate_count": len(candidates),
        "embedded_bnk_candidates": candidates,
        "bank_semantics_recovered": False,
        "bank_event_bindings_recovered": False,
        "evidence_limit": (
            "Embedded null-terminated .bnk strings and raw pointer-byte "
            "occurrences only. Raw occurrences are not proven x86 xrefs, "
            "loader calls, bank roles, sample indices, menu/login music, or "
            "match-event sound bindings."
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
    parser.add_argument("--max-strings", type=int, default=512)
    parser.add_argument("--max-pointer-candidates", type=int, default=256)
    args = parser.parse_args()

    require_private_output_path(args.output)
    pe = OriginalPE32.parse(args.original_executable.read_bytes())
    report = audio_bank_trace_report(
        pe,
        max_strings=args.max_strings,
        max_pointer_candidates=args.max_pointer_candidates,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Private Gate-14 audio-bank trace saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
