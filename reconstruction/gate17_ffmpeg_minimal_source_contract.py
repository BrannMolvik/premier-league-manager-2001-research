"""Fail-closed source/provenance contract for a minimal Gate-17 FFmpeg helper."""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Mapping


class MinimalFfmpegSourceContractError(RuntimeError):
    pass


CONTRACT_PATH = Path("third_party/ffmpeg-lgpl-candidate/SOURCE-CONTRACT.json")
PINNED_BTB_BUILD_COMMIT = "9acad4a9ef1583096af7836cc1e9c8cbcb4d3950"
PINNED_FFMPEG_COMMIT = "46d8f462eeb87ee1f704d8c44a0ee24fca471ad1"
PINNED_ARCHIVE_SHA256 = "3fc85bae9f9643a03d15c2d2de12fb017dcd9fdabe819bfb1a94f54fea108714"
REQUIRED_DERIVATIVE_DECODERS = {"h264", "aac"}
REQUIRED_EA_CODEC_SUPERSET = {
    "eatgq",
    "adpcm_ea",
    "adpcm_ea_r1",
    "adpcm_ea_r2",
    "adpcm_ea_r3",
    "adpcm_ima_ea_eacs",
    "adpcm_ima_ea_sead",
    "adpcm_psx",
    "pcm_mulaw",
    "pcm_s16le",
    "pcm_s16le_planar",
    "pcm_s8",
    "mp3",
}


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise MinimalFfmpegSourceContractError(f"{label} must be an object")
    return value


def _bool(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise MinimalFfmpegSourceContractError(f"{label} must be boolean")
    return value


def _sha(value: object, label: str) -> str:
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value) is None:
        raise MinimalFfmpegSourceContractError(f"{label} must be a lowercase Git/SHA-256 identity")
    return value


def load_contract(repo_root: str | Path) -> tuple[dict, Path]:
    root = Path(repo_root).resolve()
    path = (root / CONTRACT_PATH).resolve()
    if not path.is_relative_to(root):
        raise MinimalFfmpegSourceContractError("source contract escaped repository root")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MinimalFfmpegSourceContractError("source contract is unreadable") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise MinimalFfmpegSourceContractError("unsupported source-contract schema")
    return payload, path


def audit_source_contract(repo_root: str | Path) -> dict:
    payload, path = load_contract(repo_root)
    broad = _mapping(payload.get("verified_broad_candidate"), "verified_broad_candidate")
    minimal = _mapping(payload.get("minimal_helper_target"), "minimal_helper_target")

    if _sha(broad.get("btbn_build_repo_commit"), "BtbN commit") != PINNED_BTB_BUILD_COMMIT:
        raise MinimalFfmpegSourceContractError("BtbN build commit drifted")
    if _sha(broad.get("ffmpeg_source_commit"), "FFmpeg commit") != PINNED_FFMPEG_COMMIT:
        raise MinimalFfmpegSourceContractError("broad candidate FFmpeg source commit drifted")
    if _sha(broad.get("archive_sha256"), "candidate archive SHA-256") != PINNED_ARCHIVE_SHA256:
        raise MinimalFfmpegSourceContractError("candidate archive SHA-256 drifted")
    if broad.get("btbn_build_arguments") != ["win64", "lgpl", "9.0"]:
        raise MinimalFfmpegSourceContractError("BtbN build arguments drifted")
    if broad.get("packaged_ffmpeg_license_file") != "COPYING.LGPLv3":
        raise MinimalFfmpegSourceContractError("broad candidate license-file identity drifted")
    if _bool(broad.get("external_dependency_surface_minimal"), "broad minimal flag"):
        raise MinimalFfmpegSourceContractError(
            "verified BtbN candidate must not be relabeled as minimal"
        )
    if _bool(broad.get("production_migration_ready"), "broad migration-ready flag"):
        raise MinimalFfmpegSourceContractError(
            "verified broad candidate cannot be production-ready under this contract"
        )

    if _sha(minimal.get("source_commit"), "minimal FFmpeg source commit") != PINNED_FFMPEG_COMMIT:
        raise MinimalFfmpegSourceContractError("minimal helper source commit drifted")
    args = minimal.get("configure_args")
    if not isinstance(args, list) or any(type(arg) is not str for arg in args):
        raise MinimalFfmpegSourceContractError("minimal configure_args must be a string list")
    if "--disable-everything" not in args or "--disable-autodetect" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must disable everything and autodetection"
        )
    external_flags = [arg for arg in args if arg.startswith("--enable-lib")]
    if external_flags:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must not enable third-party libraries: " + ", ".join(external_flags)
        )
    if "--enable-mediafoundation" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must explicitly re-enable Windows Media Foundation"
        )
    if "--enable-w32threads" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must explicitly re-enable native Windows threads"
        )
    if "--enable-demuxer=ea" not in args:
        raise MinimalFfmpegSourceContractError("minimal helper must enable the EA demuxer")
    if "--enable-encoder=h264_mf,aac" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must enable h264_mf and native AAC"
        )
    if "--enable-muxer=mp4" not in args or "--enable-protocol=file,pipe" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must retain file/pipe I/O and the actual mp4 muxer"
        )
    if "--enable-muxer=null" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must retain the null muxer for runtime decode verification"
        )
    if "--enable-muxer=mov" in args and "--enable-muxer=mp4" not in args:
        raise MinimalFfmpegSourceContractError(
            "mov-only output is insufficient for extension-selected .mp4 derivatives"
        )

    codecs = minimal.get("ea_demuxer_codec_superset")
    if not isinstance(codecs, list) or set(codecs) != REQUIRED_EA_CODEC_SUPERSET:
        raise MinimalFfmpegSourceContractError(
            "EA decoder superset must match the source-derived bounded set"
        )
    decoder_arg = next((arg for arg in args if arg.startswith("--enable-decoder=")), None)
    if decoder_arg is None:
        raise MinimalFfmpegSourceContractError("minimal helper has no decoder enable list")
    enabled_decoders = set(decoder_arg.split("=", 1)[1].split(","))
    if not REQUIRED_EA_CODEC_SUPERSET.issubset(enabled_decoders):
        raise MinimalFfmpegSourceContractError(
            "minimal helper decoder list omits a source-derived EA possibility"
        )
    if not REQUIRED_DERIVATIVE_DECODERS.issubset(enabled_decoders):
        raise MinimalFfmpegSourceContractError(
            "minimal helper must retain H.264/AAC derivative validation decoders"
        )
    if minimal.get("required_derivative_validation_decoders") != ["h264", "aac"]:
        raise MinimalFfmpegSourceContractError(
            "derivative validation decoder contract drifted"
        )

    plumbing = minimal.get("required_runtime_validation_plumbing")
    if plumbing != {
        "protocols": ["file", "pipe"],
        "muxers": ["mp4", "null"],
        "reason": "Runtime startup cache uses -progress pipe:1 and -f null decode verification.",
    }:
        raise MinimalFfmpegSourceContractError(
            "runtime validation plumbing contract drifted"
        )

    proof_flags = (
        "build_verified",
        "synthetic_roundtrip_verified",
        "exact_original_tgq_verified",
        "external_windows11_playback_verified",
        "source_material_complete",
    )
    proof = {field: _bool(minimal.get(field), f"minimal_helper_target.{field}") for field in proof_flags}
    ready = _bool(minimal.get("production_migration_ready"), "minimal production-ready flag")
    if ready and not all(proof.values()):
        raise MinimalFfmpegSourceContractError(
            "minimal helper cannot be production-ready before every proof/material flag passes"
        )

    return {
        "contract_path": CONTRACT_PATH.as_posix(),
        "broad_candidate_pinned": True,
        "broad_candidate_minimal": False,
        "minimal_helper_external_library_flags": [],
        "minimal_helper_ea_codec_superset_count": len(REQUIRED_EA_CODEC_SUPERSET),
        "minimal_helper_proofs": proof,
        "minimal_helper_production_migration_ready": ready,
        "legal_compliance_claimed": False,
    }
