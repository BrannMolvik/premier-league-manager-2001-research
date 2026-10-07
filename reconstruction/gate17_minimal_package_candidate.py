"""Build and audit a non-production Windows package using the exact minimal FFmpeg helper."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile
from typing import Mapping

from startup_media_profile_marker import (
    PACKAGED_STARTUP_MEDIA_PROFILE_RELATIVE_PATH,
    candidate_profile_marker_payload,
    validate_candidate_profile_marker,
)


class MinimalPackageCandidateError(RuntimeError):
    """Raised when the minimal-helper package candidate drifts or self-promotes."""


CANDIDATE_EXECUTABLE_NAME = "FM2001-Windows11-MinimalFFmpegCandidate.exe"
CANDIDATE_TOP_LEVEL_PREFIX = "FM2001-Windows11-MinimalFFmpegCandidate"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
EXPECTED_SOURCE_COMMIT = "46d8f462eeb87ee1f704d8c44a0ee24fca471ad1"
BUILD_PROOF_RELATIVE_PATH = Path("runtime_tools") / "minimal-ffmpeg-build-proof.json"
ROUNDTRIP_PROOF_RELATIVE_PATH = (
    Path("runtime_tools") / "minimal-ffmpeg-roundtrip-proof.json"
)
SOURCE_LICENSE_RELATIVE_PATH = Path("runtime_tools") / "COPYING.LGPLv2.1"

CANDIDATE_REQUIRED_BUNDLED_FILES = (
    "original_assets/MANIFEST.md",
    "original_assets/README.md",
    "original_assets/converted/pstartmenu-v1/manifest.json",
    "original_assets/converted/pstartmenu-v1/payload.bin.xz",
    "original_assets/source/English.str",
    "original_assets/source/FM2001_Art/Generic/main_menu/main_menu_bground.444",
    "original_assets/source/FM2001_Art/Generic/menu_popup/menu_anim.444",
    "original_assets/source/FM2001_Art/Generic/match_report/info_popup.444",
    "original_assets/source/Fonts/Zurich_XCn_BT_16pixel.fnt",
    "original_assets/source/Fonts/Zurich_BdXCn_BT_20pixel.fnt",
    "runtime_tools/ffmpeg.exe",
    PACKAGED_STARTUP_MEDIA_PROFILE_RELATIVE_PATH.as_posix(),
    BUILD_PROOF_RELATIVE_PATH.as_posix(),
    ROUNDTRIP_PROOF_RELATIVE_PATH.as_posix(),
    SOURCE_LICENSE_RELATIVE_PATH.as_posix(),
)

FORBIDDEN_EXTERNAL_GAME_DATA = {
    "footbal.exe",
    "footballmanager.exe",
    "master.dat",
    "static.dat",
    "core.str",
}


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise MinimalPackageCandidateError(f"{label} is missing: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MinimalPackageCandidateError(f"{label} is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise MinimalPackageCandidateError(f"{label} root must be an object")
    return payload


def _require_commit(value: object, *, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise MinimalPackageCandidateError(
            f"{label} must be a complete lowercase Git commit SHA"
        )
    return value


def _safe_version(value: str) -> str:
    value = str(value).strip()
    if not value or re.fullmatch(r"[A-Za-z0-9._-]+", value) is None:
        raise MinimalPackageCandidateError(
            "candidate version must use only letters, digits, dot, underscore or dash"
        )
    return value


def _require_false(payload: Mapping[str, object], fields: tuple[str, ...], label: str) -> None:
    for field in fields:
        if payload.get(field) is not False:
            raise MinimalPackageCandidateError(
                f"{label} requires {field}=false"
            )


def validate_candidate_proofs(
    *,
    ffmpeg_executable: str | Path,
    build_proof: str | Path,
    roundtrip_proof: str | Path,
) -> dict:
    ffmpeg = Path(ffmpeg_executable)
    if not ffmpeg.is_file() or ffmpeg.stat().st_size <= 0:
        raise MinimalPackageCandidateError(f"minimal ffmpeg.exe is missing: {ffmpeg}")
    build_path = Path(build_proof)
    roundtrip_path = Path(roundtrip_proof)
    build = _load_json(build_path, "minimal build proof")
    roundtrip = _load_json(roundtrip_path, "minimal roundtrip proof")

    if (
        build.get("schema_version") != 1
        or build.get("audit_kind") != "gate17_minimal_ffmpeg_build"
        or build.get("passed") is not True
        or build.get("build_verified") is not True
        or build.get("synthetic_roundtrip_verified") is not False
    ):
        raise MinimalPackageCandidateError("minimal build proof is not a valid build receipt")
    _require_false(
        build,
        (
            "exact_original_tgq_verified",
            "external_windows11_playback_verified",
            "source_material_complete",
            "production_migration_ready",
            "legal_compliance_claimed",
        ),
        "minimal build proof",
    )
    source_commit = _require_commit(build.get("source_commit"), label="build source_commit")
    if source_commit != EXPECTED_SOURCE_COMMIT:
        raise MinimalPackageCandidateError("minimal build proof source commit drifted")
    ffmpeg_sha = _sha256_file(ffmpeg)
    if build.get("ffmpeg_sha256") != ffmpeg_sha:
        raise MinimalPackageCandidateError(
            "minimal ffmpeg.exe differs from build proof"
        )

    build_sha = _sha256_file(build_path)
    if (
        roundtrip.get("schema_version") != 1
        or roundtrip.get("audit_kind") != "gate17_minimal_ffmpeg_synthetic_roundtrip"
        or roundtrip.get("passed") is not True
        or roundtrip.get("build_verified") is not True
        or roundtrip.get("synthetic_roundtrip_verified") is not True
    ):
        raise MinimalPackageCandidateError(
            "minimal roundtrip proof is not a valid synthetic receipt"
        )
    _require_false(
        roundtrip,
        (
            "exact_original_tgq_verified",
            "external_windows11_playback_verified",
            "source_material_complete",
            "production_migration_ready",
            "legal_compliance_claimed",
        ),
        "minimal roundtrip proof",
    )
    if roundtrip.get("build_proof_sha256") != build_sha:
        raise MinimalPackageCandidateError(
            "minimal roundtrip proof is bound to a different build proof"
        )
    if roundtrip.get("build_proof_ffmpeg_sha256") != ffmpeg_sha:
        raise MinimalPackageCandidateError(
            "minimal roundtrip proof is bound to a different ffmpeg.exe"
        )
    if roundtrip.get("canonical_video_encoder") != "h264_mf":
        raise MinimalPackageCandidateError("minimal roundtrip video encoder drifted")
    if roundtrip.get("canonical_audio_encoder") != "aac":
        raise MinimalPackageCandidateError("minimal roundtrip audio encoder drifted")

    return {
        "source_commit": source_commit,
        "ffmpeg_sha256": ffmpeg_sha,
        "build_proof_sha256": build_sha,
        "roundtrip_proof_sha256": _sha256_file(roundtrip_path),
    }


def create_candidate_profile_marker(
    *,
    ffmpeg_executable: str | Path,
    build_proof: str | Path,
    roundtrip_proof: str | Path,
    output_marker: str | Path,
) -> dict:
    identity = validate_candidate_proofs(
        ffmpeg_executable=ffmpeg_executable,
        build_proof=build_proof,
        roundtrip_proof=roundtrip_proof,
    )
    payload = candidate_profile_marker_payload(**identity)
    output = Path(output_marker)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return payload


def _resolve_bundled_file(root: Path, relative: str) -> Path:
    direct = root / Path(relative)
    internal = root / "_internal" / Path(relative)
    matches = [path for path in (direct, internal) if path.is_file()]
    if len(matches) != 1:
        raise MinimalPackageCandidateError(
            f"candidate bundled file must resolve exactly once: {relative}"
        )
    return matches[0]


def _payload_files(root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            (path for path in root.rglob("*") if path.is_file()),
            key=lambda path: path.relative_to(root).as_posix().casefold(),
        )
    )


def audit_candidate_distribution(dist_root: str | Path) -> dict:
    root = Path(dist_root).resolve()
    if not root.is_dir():
        raise MinimalPackageCandidateError(
            f"candidate distribution does not exist: {root}"
        )
    executable = root / CANDIDATE_EXECUTABLE_NAME
    if not executable.is_file() or executable.stat().st_size <= 0:
        raise MinimalPackageCandidateError(
            f"candidate executable is missing or empty: {executable}"
        )

    resolved = {
        relative: _resolve_bundled_file(root, relative)
        for relative in CANDIDATE_REQUIRED_BUNDLED_FILES
    }
    for relative, path in resolved.items():
        if path.stat().st_size <= 0:
            raise MinimalPackageCandidateError(
                f"candidate bundled file is empty: {relative}"
            )

    ffmpeg = resolved["runtime_tools/ffmpeg.exe"]
    marker_path = resolved[PACKAGED_STARTUP_MEDIA_PROFILE_RELATIVE_PATH.as_posix()]
    build_path = resolved[BUILD_PROOF_RELATIVE_PATH.as_posix()]
    roundtrip_path = resolved[ROUNDTRIP_PROOF_RELATIVE_PATH.as_posix()]
    license_path = resolved[SOURCE_LICENSE_RELATIVE_PATH.as_posix()]

    marker = validate_candidate_profile_marker(marker_path, ffmpeg)
    proof_identity = validate_candidate_proofs(
        ffmpeg_executable=ffmpeg,
        build_proof=build_path,
        roundtrip_proof=roundtrip_path,
    )
    if marker["build_proof_sha256"] != proof_identity["build_proof_sha256"]:
        raise MinimalPackageCandidateError(
            "packaged build proof differs from candidate marker"
        )
    if marker["roundtrip_proof_sha256"] != proof_identity["roundtrip_proof_sha256"]:
        raise MinimalPackageCandidateError(
            "packaged roundtrip proof differs from candidate marker"
        )

    build = _load_json(build_path, "packaged minimal build proof")
    if build.get("source_license_file") != "COPYING.LGPLv2.1":
        raise MinimalPackageCandidateError(
            "minimal package source-license filename drifted"
        )
    if build.get("source_license_sha256") != _sha256_file(license_path):
        raise MinimalPackageCandidateError(
            "packaged source-license text differs from build proof"
        )

    files = _payload_files(root)
    forbidden = [
        path.relative_to(root).as_posix()
        for path in files
        if path.name.casefold() in FORBIDDEN_EXTERNAL_GAME_DATA
    ]
    if forbidden:
        raise MinimalPackageCandidateError(
            "candidate must not redistribute user-owned FM2001 installation data: "
            + ", ".join(forbidden)
        )

    old_provider = [
        path.relative_to(root).as_posix()
        for path in files
        if "third_party/ffmpeg/" in path.relative_to(root).as_posix().replace("\\", "/")
        or path.name == "ffmpeg.provenance.json"
    ]
    if old_provider:
        raise MinimalPackageCandidateError(
            "minimal-helper candidate must not carry old provider provenance: "
            + ", ".join(old_provider)
        )

    return {
        "schema_version": 1,
        "audit_kind": "gate17_minimal_ffmpeg_package_distribution",
        "passed": True,
        "executable": CANDIDATE_EXECUTABLE_NAME,
        "file_count": len(files),
        "source_commit": proof_identity["source_commit"],
        "ffmpeg_sha256": proof_identity["ffmpeg_sha256"],
        "build_proof_sha256": proof_identity["build_proof_sha256"],
        "roundtrip_proof_sha256": proof_identity["roundtrip_proof_sha256"],
        "source_license_sha256": _sha256_file(license_path),
        "startup_media_video_encoder": marker["profile"]["video_encoder"],
        "build_verified": True,
        "synthetic_roundtrip_verified": True,
        "exact_original_tgq_verified": False,
        "external_windows11_playback_verified": False,
        "source_material_complete": False,
        "production_migration_ready": False,
        "production_runtime_switched": False,
        "legal_compliance_claimed": False,
    }


def _require_output_outside_repo(output_dir: Path, repo_root: Path) -> Path:
    output = output_dir.resolve()
    repo = repo_root.resolve()
    if output == repo or output.is_relative_to(repo):
        raise MinimalPackageCandidateError(
            "candidate output must remain outside the Git repository"
        )
    output.mkdir(parents=True, exist_ok=True)
    return output


def _file_entries(root: Path) -> list[dict]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        for path in _payload_files(root)
    ]


def _deterministic_zip(source_root: Path, archive: Path, top_level: str) -> None:
    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:
        for path in _payload_files(source_root):
            relative = path.relative_to(source_root).as_posix()
            info = zipfile.ZipInfo(
                f"{top_level}/{relative}",
                date_time=ZIP_TIMESTAMP,
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def build_minimal_package_candidate(
    *,
    dist_root: str | Path,
    output_dir: str | Path,
    repo_root: str | Path,
    release_version: str,
    repository_commit: str,
) -> dict:
    audit = audit_candidate_distribution(dist_root)
    commit = _require_commit(repository_commit, label="repository_commit")
    version = _safe_version(release_version)
    output = _require_output_outside_repo(Path(output_dir), Path(repo_root))
    if any(output.iterdir()):
        raise MinimalPackageCandidateError(
            "candidate output directory must be empty"
        )

    top_level = f"{CANDIDATE_TOP_LEVEL_PREFIX}-{version}"
    archive = output / f"{top_level}.zip"
    sidecar = output / f"{top_level}.candidate.json"

    with tempfile.TemporaryDirectory(
        prefix="fm2001-minimal-candidate-",
        dir=output,
    ) as temp:
        staged = Path(temp) / top_level
        shutil.copytree(Path(dist_root).resolve(), staged)
        readme = staged / "README-MINIMAL-FFMPEG-CANDIDATE.txt"
        readme.write_text(
            "\n".join(
                (
                    "FM2001 Windows 11 minimal-FFmpeg package candidate",
                    f"Version: {version}",
                    f"Repository commit: {commit}",
                    "",
                    "This is a Gate-17 validation artifact, not the production release.",
                    "It selects the h264_mf startup-media conversion profile only because",
                    "the bundled runtime_tools/startup-media-profile.json is present.",
                    "The ordinary production package remains unchanged.",
                    "",
                    "Exact original-TGQ Windows conversion has not yet been verified.",
                    "External Windows 11 visible/audible playback has not yet been verified.",
                    "Source-material completeness and legal compliance are not claimed.",
                    "",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        manifest = {
            "schema_version": 1,
            "audit_kind": "gate17_minimal_ffmpeg_package_candidate",
            "release_version": version,
            "repository_commit": commit,
            **audit,
            "candidate_only": True,
            "external_original_game_data_bundled": False,
            "external_game_data_required_at_runtime": True,
            "files": _file_entries(staged),
        }
        (staged / "PACKAGE-CANDIDATE-MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        _deterministic_zip(staged, archive, top_level)

    receipt = {
        "schema_version": 1,
        "audit_kind": "gate17_minimal_ffmpeg_package_candidate_archive",
        "passed": True,
        "release_version": version,
        "repository_commit": commit,
        "archive": archive.name,
        "archive_sha256": _sha256_file(archive),
        "archive_size_bytes": archive.stat().st_size,
        "ffmpeg_sha256": audit["ffmpeg_sha256"],
        "build_proof_sha256": audit["build_proof_sha256"],
        "roundtrip_proof_sha256": audit["roundtrip_proof_sha256"],
        "candidate_only": True,
        "exact_original_tgq_verified": False,
        "external_windows11_playback_verified": False,
        "source_material_complete": False,
        "production_migration_ready": False,
        "production_runtime_switched": False,
        "legal_compliance_claimed": False,
    }
    sidecar.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"archive": archive, "receipt": sidecar, **receipt}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    marker = sub.add_parser("marker")
    marker.add_argument("--ffmpeg", type=Path, required=True)
    marker.add_argument("--build-proof", type=Path, required=True)
    marker.add_argument("--roundtrip-proof", type=Path, required=True)
    marker.add_argument("--output", type=Path, required=True)

    package = sub.add_parser("package")
    package.add_argument("--dist-root", type=Path, required=True)
    package.add_argument("--output-dir", type=Path, required=True)
    package.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    package.add_argument("--release-version", required=True)
    package.add_argument("--repository-commit", required=True)

    args = parser.parse_args()
    if args.command == "marker":
        result = create_candidate_profile_marker(
            ffmpeg_executable=args.ffmpeg,
            build_proof=args.build_proof,
            roundtrip_proof=args.roundtrip_proof,
            output_marker=args.output,
        )
    else:
        result = build_minimal_package_candidate(
            dist_root=args.dist_root,
            output_dir=args.output_dir,
            repo_root=args.repo_root,
            release_version=args.release_version,
            repository_commit=args.repository_commit,
        )
        result = {
            key: str(value) if isinstance(value, Path) else value
            for key, value in result.items()
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
