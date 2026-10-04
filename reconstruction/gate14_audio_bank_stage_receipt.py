"""Private receipt validator for exact Gate-14 BNK source staging.

This validator proves only source identity for the four executable-owned BNK
banks. It requires one complete hashed exact-path inventory report and exact
byte agreement with the staged files. It does not infer BNK headers, tables,
sample offsets, codec, rate/channels, sample names, roles, or event bindings.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Mapping

from gate13_button_source_trace import require_private_output_path
from gate13_source_inventory import normalize_member
from gate14_audio_bank_source_paths import (
    AUDIO_BANK_EXACT_PATH_FILE,
    CANONICAL_AUDIO_SOURCE_ARCHIVE_SHA256,
    CANONICAL_AUDIO_SOURCE_ARCHIVE_SIZE,
    validate_audio_bank_exact_path_contract,
)


class Gate14AudioBankStageReceiptError(RuntimeError):
    pass


_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_EXTRACTED_LAYERS = {
    "zip-extracted",
    "iso9660-extracted",
    "disc-image-extracted",
}


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_audio_bank_stage_receipt(
    *,
    repo_root: str | Path,
    inventory_report: str | Path,
    staging_root: str | Path,
) -> dict:
    expected = validate_audio_bank_exact_path_contract(repo_root)
    expected_set = set(expected)

    report_path = Path(inventory_report).resolve()
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Gate14AudioBankStageReceiptError(
            "audio-bank inventory report is not readable JSON"
        ) from exc
    if not isinstance(report, Mapping):
        raise Gate14AudioBankStageReceiptError(
            "audio-bank inventory report root must be an object"
        )
    if report.get("only_explicit") is not True:
        raise Gate14AudioBankStageReceiptError(
            "audio-bank staging requires only_explicit=true"
        )
    if report.get("unresolved_explicit_paths") != []:
        raise Gate14AudioBankStageReceiptError(
            "audio-bank staging report has unresolved exact paths"
        )
    source_sha = report.get("source_sha256")
    source_size = report.get("source_size")
    if not isinstance(source_sha, str) or not _HEX64.fullmatch(source_sha):
        raise Gate14AudioBankStageReceiptError(
            "audio-bank staging report requires a hashed source archive"
        )
    if source_sha != CANONICAL_AUDIO_SOURCE_ARCHIVE_SHA256:
        raise Gate14AudioBankStageReceiptError(
            "audio-bank staging report source SHA-256 is not canonical"
        )
    if source_size != CANONICAL_AUDIO_SOURCE_ARCHIVE_SIZE:
        raise Gate14AudioBankStageReceiptError(
            "audio-bank staging report source size is not canonical"
        )

    raw_explicit = report.get("explicit_paths")
    if not isinstance(raw_explicit, list) or any(
        not isinstance(value, str) for value in raw_explicit
    ):
        raise Gate14AudioBankStageReceiptError(
            "audio-bank staging report explicit_paths is invalid"
        )
    explicit = {normalize_member(value) for value in raw_explicit}
    if {path.casefold() for path in explicit} != {
        path.casefold() for path in expected_set
    }:
        raise Gate14AudioBankStageReceiptError(
            "audio-bank staging report exact-path set differs from contract"
        )

    raw_candidates = report.get("candidates")
    if not isinstance(raw_candidates, list):
        raise Gate14AudioBankStageReceiptError(
            "audio-bank staging report candidates is invalid"
        )

    by_key: dict[str, Mapping[str, object]] = {}
    canonical_by_key = {path.casefold(): path for path in expected}
    for item in raw_candidates:
        if not isinstance(item, Mapping) or not isinstance(item.get("path"), str):
            continue
        normalized = normalize_member(str(item["path"]))
        key = normalized.casefold()
        if key not in canonical_by_key:
            continue
        if key in by_key:
            raise Gate14AudioBankStageReceiptError(
                f"duplicate extracted candidate for {canonical_by_key[key]}"
            )
        by_key[key] = item
    if set(by_key) != set(canonical_by_key):
        missing = sorted(
            canonical_by_key[key]
            for key in set(canonical_by_key) - set(by_key)
        )
        raise Gate14AudioBankStageReceiptError(
            f"audio-bank staging report is missing candidates: {missing}"
        )

    stage = Path(staging_root).resolve()
    banks: list[dict] = []
    for source_path in expected:
        key = source_path.casefold()
        item = by_key[key]
        if item.get("candidate_reason") != "explicit-path":
            raise Gate14AudioBankStageReceiptError(
                f"{source_path} is not an explicit-path candidate"
            )
        if item.get("source_layer") not in _ALLOWED_EXTRACTED_LAYERS:
            raise Gate14AudioBankStageReceiptError(
                f"{source_path} does not prove extracted source bytes"
            )
        candidate_sha = item.get("sha256")
        candidate_size = item.get("size")
        if (
            not isinstance(candidate_sha, str)
            or not _HEX64.fullmatch(candidate_sha)
            or type(candidate_size) is not int
            or candidate_size <= 0
        ):
            raise Gate14AudioBankStageReceiptError(
                f"{source_path} candidate identity is incomplete"
            )

        staged = stage.joinpath(*source_path.split("/")).resolve()
        try:
            staged.relative_to(stage)
        except ValueError as exc:
            raise Gate14AudioBankStageReceiptError(
                f"staged path escapes staging root: {source_path}"
            ) from exc
        if not staged.is_file():
            # Case-preserving source extraction may retain a different spelling
            # of the final basename. Resolve only within the exact parent dir.
            parent = staged.parent
            matches = (
                [
                    candidate
                    for candidate in parent.iterdir()
                    if candidate.is_file()
                    and candidate.name.casefold() == staged.name.casefold()
                ]
                if parent.is_dir()
                else []
            )
            if len(matches) != 1:
                raise Gate14AudioBankStageReceiptError(
                    f"staged audio bank is missing: {source_path}"
                )
            staged = matches[0]

        actual_size = staged.stat().st_size
        actual_sha = _sha256_file(staged)
        if actual_size != candidate_size or actual_sha != candidate_sha:
            raise Gate14AudioBankStageReceiptError(
                f"staged audio bank differs from inventory: {source_path}"
            )
        banks.append(
            {
                "source_path": source_path,
                "sha256": actual_sha,
                "size_bytes": actual_size,
                "source_layer": item.get("source_layer"),
            }
        )

    return {
        "schema_version": 1,
        "passed": True,
        "source_sha256": source_sha,
        "source_size": source_size,
        "exact_path_contract": str(AUDIO_BANK_EXACT_PATH_FILE),
        "bank_count": len(banks),
        "banks": banks,
        "ready_for_private_format_analysis": True,
        "bank_header_layout_recovered": False,
        "sample_table_layout_recovered": False,
        "sample_offsets_recovered": False,
        "sample_codec_recovered": False,
        "sample_rate_channels_recovered": False,
        "modern_sample_decode_ready": False,
        "event_binding_recovered": False,
        "evidence_limit": (
            "This receipt proves exact selected BNK source bytes only. It does "
            "not prove any BNK header/table/offset/codec/rate/channel/sample "
            "semantics, modern decode, bank role, or event binding."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument("--inventory-report", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    require_private_output_path(args.output, repository_root=args.repo_root)
    receipt = validate_audio_bank_stage_receipt(
        repo_root=args.repo_root,
        inventory_report=args.inventory_report,
        staging_root=args.staging_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Private Gate-14 audio-bank staging receipt saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
