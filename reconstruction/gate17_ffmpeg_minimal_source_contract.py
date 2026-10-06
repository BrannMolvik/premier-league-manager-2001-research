"""Fail-closed source/provenance contract for a minimal Gate-17 FFmpeg helper."""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Mapping

from startup_fmv_presentation import ORIGINAL_STARTUP_FMV_PRESENTATION


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
    if minimal.get("license_file") != "COPYING.LGPLv2.1":
        raise MinimalFfmpegSourceContractError(
            "minimal helper license-file identity must remain COPYING.LGPLv2.1"
        )
    args = minimal.get("configure_args")
    if not isinstance(args, list) or any(type(arg) is not str for arg in args):
        raise MinimalFfmpegSourceContractError("minimal configure_args must be a string list")
    if "--disable-everything" not in args or "--disable-autodetect" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must disable everything and autodetection"
        )
    forbidden_license_flags = [
        flag for flag in ("--enable-gpl", "--enable-nonfree", "--enable-version3")
        if flag in args
    ]
    if forbidden_license_flags:
        raise MinimalFfmpegSourceContractError(
            "minimal helper unexpectedly elevates its license mode: "
            + ", ".join(forbidden_license_flags)
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
    if "--enable-d3d11va" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must explicitly re-enable D3D11VA for the pinned Media Foundation encoder source"
        )
    if minimal.get("required_windows_platform_components") != [
        "mediafoundation",
        "d3d11va",
        "w32threads",
    ]:
        raise MinimalFfmpegSourceContractError(
            "minimal helper Windows platform-component contract drifted"
        )
    if "--enable-w32threads" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must explicitly re-enable native Windows threads"
        )
    if "--extra-ldflags=-static" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must statically link the MinGW/UCRT toolchain runtime"
        )
    expected_toolchain_linkage = {
        "strategy": "static",
        "configure_arg": "--extra-ldflags=-static",
        "dynamic_runtime_dlls_forbidden": [
            "libgcc_s*.dll",
            "libstdc++-6.dll",
            "libwinpthread-1.dll",
            "libssp-0.dll",
            "msys-2.0.dll",
        ],
        "provenance_boundary": (
            "The MinGW-w64/UCRT toolchain runtime is build infrastructure, not an "
            "FFmpeg --enable-lib* component. Static linkage removes a separate "
            "runtime-DLL deployment dependency, but source_material_complete stays "
            "false until required toolchain redistribution/source-license materials "
            "are accounted for."
        ),
    }
    if minimal.get("toolchain_runtime_linkage") != expected_toolchain_linkage:
        raise MinimalFfmpegSourceContractError(
            "minimal helper toolchain-runtime linkage contract drifted"
        )
    if "--enable-demuxer=ea" not in args:
        raise MinimalFfmpegSourceContractError("minimal helper must enable the EA demuxer")
    if "--enable-demuxer=mov" not in args or minimal.get("required_derivative_input_demuxer") != "mov":
        raise MinimalFfmpegSourceContractError(
            "minimal helper must retain the MOV/MP4 input demuxer for derivative verification"
        )
    encoder_arg = next((arg for arg in args if arg.startswith("--enable-encoder=")), None)
    if encoder_arg is None:
        raise MinimalFfmpegSourceContractError("minimal helper has no encoder enable list")
    enabled_encoders = set(encoder_arg.split("=", 1)[1].split(","))
    required_encoders = {"h264_mf", "aac", "wrapped_avframe", "pcm_s16le"}
    if not required_encoders.issubset(enabled_encoders):
        raise MinimalFfmpegSourceContractError(
            "minimal helper must enable h264_mf/AAC plus null-muxer "
            "wrapped_avframe/pcm_s16le verification encoders"
        )
    if "--enable-filter=aresample" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must retain internal aresample for AAC sample-format conversion"
        )
    if "--enable-filter=scale" not in args:
        raise MinimalFfmpegSourceContractError(
            "minimal helper must retain the scale filter for the recovered startup presentation"
        )
    if minimal.get("required_internal_video_conversion") != {
        "filter": "scale",
        "expression": ORIGINAL_STARTUP_FMV_PRESENTATION.ffmpeg_filter,
        "dependency": "swscale",
        "reason": (
            "Canonical FM2001 startup conversion bakes the source-proven 2x horizontal "
            "nearest-neighbor treatment into each derivative."
        ),
    }:
        raise MinimalFfmpegSourceContractError(
            "internal video conversion contract drifted"
        )
    if minimal.get("required_protocols") != ["file", "pipe"]:
        raise MinimalFfmpegSourceContractError(
            "minimal helper protocol metadata must remain file+pipe"
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

    audio_conversion = minimal.get("required_internal_audio_conversion")
    if audio_conversion != {
        "filter": "aresample",
        "reason": "EA audio decoders may produce integer PCM while the native AAC encoder accepts FLTP.",
    }:
        raise MinimalFfmpegSourceContractError(
            "internal audio conversion contract drifted"
        )

    plumbing = minimal.get("required_runtime_validation_plumbing")
    if plumbing != {
        "protocols": ["file", "pipe"],
        "muxers": ["mp4", "null"],
        "null_muxer_default_encoders": ["wrapped_avframe", "pcm_s16le"],
        "reason": (
            "Runtime startup cache uses -progress pipe:1 and -f null decode "
            "verification; pinned FFmpeg nullenc.c defaults to wrapped_avframe "
            "video and pcm_s16le audio."
        ),
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
