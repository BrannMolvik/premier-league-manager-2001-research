"""Build a deterministic Gate-17 Windows release-candidate archive.

This script consumes an already-frozen one-directory application. It never
copies the user-owned FM2001 installation data into the candidate. The
provenance-tracked original_assets tree may be bundled because those files are
already intentional repository assets governed by the asset policy.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import zipfile
from hashlib import sha256
from pathlib import Path


class PackageCandidateError(RuntimeError):
    pass


FORBIDDEN_EXTERNAL_GAME_DATA = {
    "footbal.exe",
    "footballmanager.exe",
    "master.dat",
    "static.dat",
    "core.str",
}

REQUIRED_BUNDLED_FILES = (
    "original_assets/MANIFEST.md",
    "original_assets/README.md",
    "original_assets/source/English.str",
    "original_assets/source/FM2001_Art/Generic/main_menu/main_menu_bground.444",
    "original_assets/source/FM2001_Art/Generic/menu_popup/menu_anim.444",
    "original_assets/source/FM2001_Art/Generic/match_report/info_popup.444",
    "original_assets/source/Fonts/Zurich_XCn_BT_16pixel.fnt",
)

ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_commit(value: str) -> str:
    value = str(value)
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise PackageCandidateError("repository commit must be a lowercase 40-character SHA")
    return value


def _safe_version(value: str) -> str:
    value = str(value).strip()
    if not value or re.fullmatch(r"[A-Za-z0-9._-]+", value) is None:
        raise PackageCandidateError("release version must use only letters, digits, dot, underscore or dash")
    return value


def require_output_outside_repo(output_dir: str | Path, repo_root: str | Path) -> Path:
    output = Path(output_dir).resolve()
    repo = Path(repo_root).resolve()
    if output == repo or output.is_relative_to(repo):
        raise PackageCandidateError("release output must remain outside the Git repository")
    output.mkdir(parents=True, exist_ok=True)
    return output


def _payload_files(root: Path) -> tuple[Path, ...]:
    return tuple(sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(root).as_posix().casefold()))


def _resolve_bundled_file(root: Path, relative: str) -> Path:
    """Resolve PyInstaller data in legacy beside-exe or v6 _internal layout."""
    direct = root / Path(relative)
    internal = root / "_internal" / Path(relative)
    matches = [path for path in (direct, internal) if path.is_file()]
    if len(matches) != 1:
        raise PackageCandidateError(
            f"required bundled asset must resolve exactly once: {relative}"
        )
    return matches[0]


def validate_distribution(dist_root: str | Path, executable_name: str) -> tuple[Path, ...]:
    root = Path(dist_root).resolve()
    if not root.is_dir():
        raise PackageCandidateError(f"frozen distribution does not exist: {root}")
    executable = root / executable_name
    if not executable.is_file() or executable.stat().st_size <= 0:
        raise PackageCandidateError(f"packaged executable is missing or empty: {executable}")
    for relative in REQUIRED_BUNDLED_FILES:
        path = _resolve_bundled_file(root, relative)
        if path.stat().st_size <= 0:
            raise PackageCandidateError(f"required bundled asset is empty: {relative}")
    files = _payload_files(root)
    forbidden = [
        p.relative_to(root).as_posix()
        for p in files
        if p.name.casefold() in FORBIDDEN_EXTERNAL_GAME_DATA
    ]
    if forbidden:
        raise PackageCandidateError(
            "candidate must not redistribute user-owned FM2001 installation data: "
            + ", ".join(forbidden)
        )
    return files


def _file_entries(root: Path) -> list[dict]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size_bytes": int(path.stat().st_size),
            "sha256": _sha256_file(path),
        }
        for path in _payload_files(root)
    ]


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_release_readme(path: Path, release_version: str, repository_commit: str) -> None:
    path.write_text(
        "\n".join((
            "FM2001 Windows 11 modernization release candidate",
            f"Version: {release_version}",
            f"Repository commit: {repository_commit}",
            "",
            "This package contains the reconstructed runtime and provenance-tracked",
            "original_assets committed under the repository asset policy.",
            "",
            "It intentionally does NOT contain the original FM2001 installation data.",
            "At launch, pass the path to your own installed game folder or select it",
            "when prompted. That folder must provide the original files required by",
            "the runtime, including Master.dat, Static.dat and FOOTBAL.EXE.",
            "",
            "The generic development notebook remains available only with --prototype-ui.",
            "Gate 17 clean-install verification is a separate external audit and is",
            "not implied by the existence of this release candidate.",
            "",
        )),
        encoding="utf-8",
    )


def _deterministic_zip(source_root: Path, archive: Path, top_level: str) -> None:
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in _payload_files(source_root):
            relative = path.relative_to(source_root).as_posix()
            info = zipfile.ZipInfo(f"{top_level}/{relative}", date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_release_candidate(
    *,
    dist_root: str | Path,
    output_dir: str | Path,
    repo_root: str | Path,
    release_version: str,
    repository_commit: str,
    executable_name: str = "FM2001-Windows11.exe",
) -> dict:
    version = _safe_version(release_version)
    commit = _require_commit(repository_commit)
    output = require_output_outside_repo(output_dir, repo_root)
    if any(output.iterdir()):
        raise PackageCandidateError("release output directory must be empty")
    validate_distribution(dist_root, executable_name)

    top_level = f"FM2001-Windows11-{version}"
    archive = output / f"{top_level}.zip"
    sidecar = output / f"{top_level}.release.json"

    with tempfile.TemporaryDirectory(prefix="fm2001-package-", dir=output) as temp:
        staged = Path(temp) / top_level
        shutil.copytree(Path(dist_root).resolve(), staged)
        _write_release_readme(staged / "README-RELEASE.txt", version, commit)
        manifest = {
            "schema_version": 1,
            "release_version": version,
            "repository_commit": commit,
            "external_original_game_data_bundled": False,
            "external_game_data_required_at_runtime": True,
            "executable": executable_name,
            "files": _file_entries(staged),
        }
        _write_json(staged / "PACKAGE-MANIFEST.json", manifest)
        _deterministic_zip(staged, archive, top_level)

    release = {
        "schema_version": 1,
        "release_version": version,
        "repository_commit": commit,
        "archive_path": archive.name,
        "archive_sha256": _sha256_file(archive),
        "archive_size_bytes": int(archive.stat().st_size),
        "external_original_game_data_bundled": False,
        "external_game_data_required_at_runtime": True,
    }
    _write_json(sidecar, release)
    return {"archive": archive, "manifest": sidecar, **release}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--executable-name", default="FM2001-Windows11.exe")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    result = build_release_candidate(
        dist_root=args.dist_root,
        output_dir=args.output_dir,
        repo_root=repo_root,
        release_version=args.release_version,
        repository_commit=args.repository_commit,
        executable_name=args.executable_name,
    )
    print(json.dumps({k: str(v) if isinstance(v, Path) else v for k, v in result.items()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
