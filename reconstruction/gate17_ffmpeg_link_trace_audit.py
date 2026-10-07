"""Fail-closed audit for Gate-17 FFmpeg evidence-only linker traces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shlex


class LinkTraceAuditError(RuntimeError):
    """Raised when the evidence-only relink is not equivalent to the release link."""


TRACE_FLAG = "-Wl,--trace"
TARGETS = ("ffmpeg_g.exe", "ffprobe_g.exe")
_ARCHIVE_RE = re.compile(r"(?<!\S)([^\s]+\.a)(?!\S)")


def _command_tokens(text: str, target: str) -> list[str]:
    matches: list[list[str]] = []
    for line in text.splitlines():
        if target not in line or " -o " not in f" {line} ":
            continue
        try:
            tokens = shlex.split(line, posix=True)
        except ValueError:
            continue
        if target in tokens and "-o" in tokens:
            matches.append(tokens)
    if len(matches) != 1:
        raise LinkTraceAuditError(
            f"expected exactly one final link command for {target}, found {len(matches)}"
        )
    return matches[0]


def _archive_inputs(text: str, target: str) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for line in text.splitlines():
        if target in line and " -o " in f" {line} ":
            continue
        for match in _ARCHIVE_RE.finditer(line):
            value = match.group(1).replace("\\", "/")
            if value not in seen:
                seen.add(value)
                ordered.append(value)
    if not ordered:
        raise LinkTraceAuditError("link trace contained no resolved .a archive inputs")
    return ordered


def _normalize_trace_command(tokens: list[str]) -> list[str]:
    count = tokens.count(TRACE_FLAG)
    if count != 1:
        raise LinkTraceAuditError(
            f"traced link command must contain exactly one {TRACE_FLAG}, found {count}"
        )
    return [token for token in tokens if token != TRACE_FLAG]


def audit_link_traces(
    *,
    release_build_log: Path,
    ffmpeg_trace_log: Path,
    ffprobe_trace_log: Path,
) -> dict:
    release = release_build_log.read_text(encoding="utf-8", errors="replace")
    traces = {
        "ffmpeg_g.exe": ffmpeg_trace_log.read_text(encoding="utf-8", errors="replace"),
        "ffprobe_g.exe": ffprobe_trace_log.read_text(encoding="utf-8", errors="replace"),
    }

    targets: dict[str, dict] = {}
    for target in TARGETS:
        release_command = _command_tokens(release, target)
        trace_command = _command_tokens(traces[target], target)
        normalized_trace = _normalize_trace_command(trace_command)
        if normalized_trace != release_command:
            raise LinkTraceAuditError(
                f"{target} traced relink drifted from release link beyond {TRACE_FLAG}"
            )
        archives = _archive_inputs(traces[target], target)
        targets[target] = {
            "release_command_token_count": len(release_command),
            "trace_only_flag": TRACE_FLAG,
            "trace_command_matches_release_after_removing_trace_flag": True,
            "resolved_archive_count": len(archives),
            "resolved_archives": archives,
        }

    return {
        "schema_version": 1,
        "passed": True,
        "evidence_scope": "resolved final-link/archive inputs for evidence-only relink",
        "targets": targets,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
        "contributor_package_attribution_complete": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-build-log", type=Path, required=True)
    parser.add_argument("--ffmpeg-trace-log", type=Path, required=True)
    parser.add_argument("--ffprobe-trace-log", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    receipt = audit_link_traces(
        release_build_log=args.release_build_log,
        ffmpeg_trace_log=args.ffmpeg_trace_log,
        ffprobe_trace_log=args.ffprobe_trace_log,
    )
    args.output_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.output_receipt.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
