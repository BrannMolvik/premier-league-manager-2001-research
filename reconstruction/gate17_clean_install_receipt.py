"""Create the distinct Gate-17 clean Windows 11 installation receipt.

This tool must be run on the actual Windows 11 release candidate machine.
It verifies one exact release archive, extracts it into a fresh location outside
the repository/development tree, executes the packaged executable from that
installed location in --package-smoke mode, and only then writes the
clean_windows_install receipt outside Git.

Hosted Windows packaging CI is useful build evidence but is not a substitute
for this external Windows 11 receipt.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import zipfile
from hashlib import sha256
from pathlib import Path, PurePosixPath

from gate17_release_readiness import require_windows_11


class CleanInstallReceiptError(RuntimeError):
    """The release candidate did not satisfy the clean-install contract."""


FORBIDDEN_EXTERNAL_GAME_DATA = {
    "footbal.exe",
    "footballmanager.exe",
    "master.dat",
    "static.dat",
    "core.str",
}


def require_external_windows_11() -> dict:
    """Require a real Windows 11 run outside hosted/automated CI."""
    if os.environ.get("GITHUB_ACTIONS", "").casefold() == "true":
        raise CleanInstallReceiptError(
            "clean Windows install receipt cannot be produced by GitHub Actions"
        )
    if os.environ.get("CI", "").casefold() in ("1", "true", "yes"):
        raise CleanInstallReceiptError(
            "clean Windows install receipt cannot be produced inside CI"
        )
    return require_windows_11()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_commit(value: str) -> str:
    value = str(value)
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise CleanInstallReceiptError(
            "repository_commit must be a lowercase 40-character Git SHA"
        )
    return value


def _require_release_version(value: str) -> str:
    value = str(value).strip()
    if not value:
        raise CleanInstallReceiptError("release_version must be non-empty")
    return value


def _outside(path: str | Path, root: str | Path, *, label: str) -> Path:
    target = Path(path).resolve()
    base = Path(root).resolve()
    if target == base or target.is_relative_to(base):
        raise CleanInstallReceiptError(
            f"{label} must be outside the development repository"
        )
    return target


def _require_fresh_directory(
    install_dir: str | Path,
    *,
    repo_root: str | Path,
) -> Path:
    target = _outside(
        install_dir,
        repo_root,
        label="clean install directory",
    )
    repo = Path(repo_root).resolve()
    if repo.is_relative_to(target):
        raise CleanInstallReceiptError(
            "clean install directory must not contain the development repository"
        )
    if target.exists():
        if not target.is_dir():
            raise CleanInstallReceiptError(
                "clean install target exists and is not a directory"
            )
        if any(target.iterdir()):
            raise CleanInstallReceiptError(
                "clean install directory must be new or empty"
            )
    else:
        target.mkdir(parents=True)
    return target


def _safe_zip_member(name: str) -> PurePosixPath:
    path = PurePosixPath(str(name).replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise CleanInstallReceiptError(
            f"release archive contains unsafe path: {name}"
        )
    if ":" in path.parts[0]:
        raise CleanInstallReceiptError(
            f"release archive contains drive-prefixed path: {name}"
        )
    return path


def validate_embedded_package_identity(
    archive: str | Path,
    *,
    release_version: str,
    repository_commit: str,
    executable_name: str,
) -> dict:
    """Require the archive's embedded package manifest to match this audit."""
    archive = Path(archive).resolve()
    try:
        with zipfile.ZipFile(archive) as bundle:
            matches = [
                item
                for item in bundle.infolist()
                if not item.is_dir()
                and PurePosixPath(item.filename.replace("\\", "/")).name
                == "PACKAGE-MANIFEST.json"
            ]
            if len(matches) != 1:
                raise CleanInstallReceiptError(
                    "release archive must contain exactly one PACKAGE-MANIFEST.json"
                )
            try:
                payload = json.loads(bundle.read(matches[0]).decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise CleanInstallReceiptError(
                    "embedded PACKAGE-MANIFEST.json is not valid UTF-8 JSON"
                ) from exc
    except zipfile.BadZipFile as exc:
        raise CleanInstallReceiptError("release archive is not a valid ZIP") from exc

    if not isinstance(payload, dict) or int(payload.get("schema_version", 0)) != 1:
        raise CleanInstallReceiptError("embedded package manifest schema is invalid")
    if payload.get("release_version") != release_version:
        raise CleanInstallReceiptError(
            "embedded package manifest belongs to a different release version"
        )
    if payload.get("repository_commit") != repository_commit:
        raise CleanInstallReceiptError(
            "embedded package manifest belongs to a different repository commit"
        )
    if payload.get("executable") != executable_name:
        raise CleanInstallReceiptError(
            "embedded package manifest names a different executable"
        )
    if payload.get("external_original_game_data_bundled") is not False:
        raise CleanInstallReceiptError(
            "embedded package manifest does not preserve original-data exclusion"
        )
    if payload.get("external_game_data_required_at_runtime") is not True:
        raise CleanInstallReceiptError(
            "embedded package manifest does not require external game data"
        )
    return payload


def extract_release_archive(
    archive: str | Path,
    install_dir: str | Path,
) -> tuple[Path, ...]:
    archive = Path(archive).resolve()
    target = Path(install_dir).resolve()
    extracted: list[Path] = []
    try:
        with zipfile.ZipFile(archive) as bundle:
            entries = [item for item in bundle.infolist() if not item.is_dir()]
            if not entries:
                raise CleanInstallReceiptError("release archive contains no files")

            # Validate the entire payload before the first write. A rejected ZIP
            # therefore cannot leave a partially extracted directory that looks
            # like a clean install.
            planned: list[tuple[zipfile.ZipInfo, PurePosixPath]] = []
            seen: set[str] = set()
            for item in entries:
                relative = _safe_zip_member(item.filename)
                normalized = relative.as_posix().casefold()
                if normalized in seen:
                    raise CleanInstallReceiptError(
                        f"release archive contains duplicate path: {item.filename}"
                    )
                seen.add(normalized)
                if relative.name.casefold() in FORBIDDEN_EXTERNAL_GAME_DATA:
                    raise CleanInstallReceiptError(
                        "release archive contains excluded original game data: "
                        + item.filename
                    )
                planned.append((item, relative))

            for item, relative in planned:
                destination = target.joinpath(*relative.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(item, "r") as source, destination.open("wb") as sink:
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        sink.write(chunk)
                extracted.append(destination)
    except zipfile.BadZipFile as exc:
        raise CleanInstallReceiptError("release archive is not a valid ZIP") from exc
    return tuple(extracted)


def resolve_installed_executable(
    install_dir: str | Path,
    executable_name: str = "FM2001-Windows11.exe",
) -> Path:
    root = Path(install_dir).resolve()
    matches = tuple(root.rglob(executable_name))
    if len(matches) != 1:
        raise CleanInstallReceiptError(
            f"installed executable must resolve exactly once; found {len(matches)}"
        )
    executable = matches[0]
    if not executable.is_file() or executable.stat().st_size <= 0:
        raise CleanInstallReceiptError("installed executable is missing or empty")
    return executable


def run_installed_package_smoke(
    executable: str | Path,
    *,
    timeout_seconds: int = 60,
) -> dict:
    executable = Path(executable).resolve()
    try:
        completed = subprocess.run(
            [str(executable), "--package-smoke"],
            cwd=executable.parent,
            capture_output=True,
            text=True,
            timeout=int(timeout_seconds),
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CleanInstallReceiptError(
            "installed release executable could not complete package smoke"
        ) from exc
    if completed.returncode != 0:
        raise CleanInstallReceiptError(
            "installed release package smoke failed with exit code "
            f"{completed.returncode}: {completed.stderr.strip()}"
        )
    stdout_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if not stdout_lines:
        raise CleanInstallReceiptError("installed package smoke produced no JSON output")
    try:
        payload = json.loads(stdout_lines[-1])
    except json.JSONDecodeError as exc:
        raise CleanInstallReceiptError(
            "installed package smoke did not end with JSON"
        ) from exc
    if not isinstance(payload, dict) or payload.get("passed") is not True:
        raise CleanInstallReceiptError(
            "installed package smoke did not declare passed=true"
        )
    if payload.get("external_game_data_required") is not True:
        raise CleanInstallReceiptError(
            "installed package smoke lost the external-game-data boundary"
        )
    return payload


def require_smoke_paths_inside_install(smoke: dict, install_dir: Path) -> dict:
    """Prove the frozen smoke resolved runtime resources from the clean install."""
    root = Path(install_dir).resolve()
    checked: dict[str, str] = {}
    for field in ("application_root", "source_root", "provenance_manifest"):
        raw = smoke.get(field)
        if not isinstance(raw, str) or not raw.strip():
            raise CleanInstallReceiptError(
                f"installed package smoke is missing {field}"
            )
        path = Path(raw).resolve()
        if path == root or not path.is_relative_to(root):
            raise CleanInstallReceiptError(
                f"installed package smoke {field} is outside the clean install"
            )
        checked[field] = str(path)
    return checked


def write_clean_install_receipt(
    *,
    release_archive: str | Path,
    release_version: str,
    repository_commit: str,
    install_dir: str | Path,
    output_path: str | Path,
    repo_root: str | Path,
    executable_name: str = "FM2001-Windows11.exe",
    timeout_seconds: int = 60,
) -> Path:
    windows = require_external_windows_11()
    version = _require_release_version(release_version)
    commit = _require_commit(repository_commit)
    archive = _outside(
        release_archive,
        repo_root,
        label="release archive",
    )
    if not archive.is_file() or archive.stat().st_size <= 0:
        raise CleanInstallReceiptError("release archive is missing or empty")
    archive_sha = _sha256_file(archive)
    archive_size = int(archive.stat().st_size)
    package_manifest = validate_embedded_package_identity(
        archive,
        release_version=version,
        repository_commit=commit,
        executable_name=executable_name,
    )

    target = _require_fresh_directory(install_dir, repo_root=repo_root)
    receipt = _outside(
        output_path,
        repo_root,
        label="clean-install receipt",
    )
    if receipt.exists():
        raise CleanInstallReceiptError(
            "clean-install receipt already exists; do not overwrite evidence"
        )
    receipt.parent.mkdir(parents=True, exist_ok=True)

    extract_release_archive(archive, target)
    executable = resolve_installed_executable(target, executable_name)
    smoke = run_installed_package_smoke(
        executable,
        timeout_seconds=timeout_seconds,
    )
    smoke_paths = require_smoke_paths_inside_install(smoke, target)

    payload = {
        "passed": True,
        "audit_kind": "gate17_clean_windows_install",
        "windows_11": True,
        "outside_development_environment": True,
        "repository_commit": commit,
        "release_version": version,
        "release_archive_sha256": archive_sha,
        "release_archive_size": archive_size,
        "installed_executable_sha256": _sha256_file(executable),
        "installed_executable_relative_path": executable.relative_to(target).as_posix(),
        "embedded_package_manifest_verified": True,
        "embedded_package_file_count": len(package_manifest.get("files", ())),
        "installed_package_smoke_paths": smoke_paths,
        "installed_package_smoke": smoke,
        **windows,
    }
    # Required truth flags must not be overwritten by platform metadata.
    payload["windows_11"] = True
    payload["outside_development_environment"] = True
    receipt.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--install-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--executable-name", default="FM2001-Windows11.exe")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    receipt = write_clean_install_receipt(
        release_archive=args.release_archive,
        release_version=args.release_version,
        repository_commit=args.repository_commit,
        install_dir=args.install_dir,
        output_path=args.output,
        repo_root=repo_root,
        executable_name=args.executable_name,
        timeout_seconds=args.timeout_seconds,
    )
    print(receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
