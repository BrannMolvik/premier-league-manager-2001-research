"""Produce the distinct Gate-17 clean Windows 11 install receipt.

This tool must run on the actual Windows 11 release candidate environment. It
does not build the package and it does not accept a source-tree/dist directory
as installation evidence. Instead it:

1. hashes the exact release archive;
2. safely extracts that archive into a fresh directory outside the Git checkout;
3. validates every extracted payload file against PACKAGE-MANIFEST.json;
4. runs the frozen executable's --package-smoke mode from the extracted install;
5. writes one non-overwriting clean_windows_install.json outside Git.

Hosted packaging CI is useful for constructing the candidate, but this producer
still requires Windows 11 and therefore must not be treated as proof merely
because a windows-latest workflow built the archive.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import zipfile

from gate17_release_readiness import require_windows_11
from gate17_windows_gameplay_receipts import (
    ReleaseArtifactIdentity,
    resolve_release_artifact_identity,
    write_new_receipt,
)


class CleanWindowsInstallReceiptError(RuntimeError):
    """A clean-install receipt could not be produced faithfully."""


PACKAGE_MANIFEST = "PACKAGE-MANIFEST.json"
DEFAULT_EXECUTABLE = "FM2001-Windows11.exe"


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_outside_repo(path: str | Path, repo_root: str | Path, *, label: str) -> Path:
    target = Path(path).resolve()
    root = Path(repo_root).resolve()
    if target == root or target.is_relative_to(root):
        raise CleanWindowsInstallReceiptError(
            f"{label} must be outside the Git/development checkout"
        )
    return target


WINDOWS_RESERVED_BASENAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}


def _safe_member_path(name: str) -> PurePosixPath:
    normalized = str(name).replace("\\", "/")
    pure = PurePosixPath(normalized)
    raw_parts = normalized.split("/")
    if (
        not normalized
        or normalized.startswith("/")
        or re.match(r"^[A-Za-z]:", normalized)
        or not pure.parts
        or any(part in ("", ".", "..") for part in raw_parts)
    ):
        raise CleanWindowsInstallReceiptError(
            f"release archive contains unsafe path: {name!r}"
        )
    for part in pure.parts:
        if ":" in part or part.endswith((" ", ".")):
            raise CleanWindowsInstallReceiptError(
                f"release archive contains unsafe Windows path: {name!r}"
            )
        basename = part.split(".", 1)[0].casefold()
        if basename in WINDOWS_RESERVED_BASENAMES:
            raise CleanWindowsInstallReceiptError(
                f"release archive contains reserved Windows path: {name!r}"
            )
    return pure


def _preflight_archive(archive: Path) -> str:
    seen_casefold: set[str] = set()
    top_levels: set[str] = set()
    with zipfile.ZipFile(archive) as zf:
        infos = zf.infolist()
        if not infos:
            raise CleanWindowsInstallReceiptError("release archive is empty")
        for info in infos:
            pure = _safe_member_path(info.filename)
            key = pure.as_posix().casefold().rstrip("/")
            if key in seen_casefold:
                raise CleanWindowsInstallReceiptError(
                    f"release archive has a Windows path collision: {info.filename}"
                )
            seen_casefold.add(key)
            top_levels.add(pure.parts[0])
            mode = (int(info.external_attr) >> 16) & 0xFFFF
            if mode and stat.S_ISLNK(mode):
                raise CleanWindowsInstallReceiptError(
                    f"release archive must not contain symlinks: {info.filename}"
                )
    if len(top_levels) != 1:
        raise CleanWindowsInstallReceiptError(
            "release archive must contain exactly one top-level package directory"
        )
    return next(iter(top_levels))


def _extract_fresh_archive(
    archive: Path,
    *,
    install_root: Path,
) -> Path:
    if install_root.exists():
        raise CleanWindowsInstallReceiptError(
            f"clean install directory must not already exist: {install_root}"
        )
    top_level = _preflight_archive(archive)
    install_root.mkdir(parents=True)
    try:
        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():
                pure = _safe_member_path(info.filename)
                destination = install_root.joinpath(*pure.parts)
                resolved = destination.resolve()
                if not resolved.is_relative_to(install_root.resolve()):
                    raise CleanWindowsInstallReceiptError(
                        f"archive member escaped clean install root: {info.filename}"
                    )
                if info.is_dir():
                    resolved.mkdir(parents=True, exist_ok=True)
                    continue
                resolved.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info, "r") as source, resolved.open("wb") as sink:
                    shutil.copyfileobj(source, sink)
    except Exception:
        shutil.rmtree(install_root, ignore_errors=True)
        raise
    package_root = install_root / top_level
    if not package_root.is_dir():
        raise CleanWindowsInstallReceiptError(
            "release archive did not materialize its top-level package directory"
        )
    return package_root


def _load_package_manifest(
    package_root: Path,
    *,
    identity: ReleaseArtifactIdentity,
    executable_name: str,
) -> tuple[dict, Path]:
    manifest_path = package_root / PACKAGE_MANIFEST
    if not manifest_path.is_file():
        raise CleanWindowsInstallReceiptError(
            f"installed package is missing {PACKAGE_MANIFEST}"
        )
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CleanWindowsInstallReceiptError(
            f"installed {PACKAGE_MANIFEST} is not readable JSON"
        ) from exc
    if not isinstance(payload, dict) or int(payload.get("schema_version", 0)) != 1:
        raise CleanWindowsInstallReceiptError(
            f"installed {PACKAGE_MANIFEST} must use schema_version 1"
        )
    if payload.get("release_version") != identity.release_version:
        raise CleanWindowsInstallReceiptError(
            "installed package manifest release_version does not match archive identity"
        )
    if payload.get("repository_commit") != identity.repository_commit:
        raise CleanWindowsInstallReceiptError(
            "installed package manifest repository_commit does not match archive identity"
        )
    if payload.get("executable") != executable_name:
        raise CleanWindowsInstallReceiptError(
            "installed package manifest executable does not match requested executable"
        )
    if payload.get("external_original_game_data_bundled") is not False:
        raise CleanWindowsInstallReceiptError(
            "installed candidate unexpectedly claims bundled original game data"
        )
    if payload.get("external_game_data_required_at_runtime") is not True:
        raise CleanWindowsInstallReceiptError(
            "installed candidate must require user-owned original game data"
        )
    return payload, manifest_path


def validate_installed_payload(package_root: Path, manifest: dict) -> dict:
    raw_files = manifest.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise CleanWindowsInstallReceiptError(
            "package manifest must contain a non-empty files list"
        )

    expected: dict[str, tuple[int, str]] = {}
    casefold_paths: set[str] = set()
    for entry in raw_files:
        if not isinstance(entry, dict):
            raise CleanWindowsInstallReceiptError("package manifest file entry is invalid")
        pure = _safe_member_path(str(entry.get("path", "")))
        relative = pure.as_posix()
        folded = relative.casefold()
        if folded in casefold_paths:
            raise CleanWindowsInstallReceiptError(
                f"package manifest has a Windows path collision: {relative}"
            )
        casefold_paths.add(folded)
        size = int(entry.get("size_bytes", -1))
        digest = str(entry.get("sha256", ""))
        if size < 0 or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise CleanWindowsInstallReceiptError(
                f"package manifest has invalid identity for {relative}"
            )
        expected[relative] = (size, digest)

    actual = {
        path.relative_to(package_root).as_posix(): path
        for path in package_root.rglob("*")
        if path.is_file()
    }
    actual_without_manifest = {
        relative: path
        for relative, path in actual.items()
        if relative != PACKAGE_MANIFEST
    }
    if set(actual_without_manifest) != set(expected):
        missing = sorted(set(expected) - set(actual_without_manifest))
        extra = sorted(set(actual_without_manifest) - set(expected))
        raise CleanWindowsInstallReceiptError(
            f"installed payload differs from package manifest: missing={missing}, extra={extra}"
        )

    total_bytes = 0
    for relative, (expected_size, expected_sha) in expected.items():
        path = actual_without_manifest[relative]
        actual_size = int(path.stat().st_size)
        actual_sha = _sha256_file(path)
        if actual_size != expected_size:
            raise CleanWindowsInstallReceiptError(
                f"installed payload size mismatch for {relative}: "
                f"expected {expected_size}, got {actual_size}"
            )
        if actual_sha != expected_sha:
            raise CleanWindowsInstallReceiptError(
                f"installed payload checksum mismatch for {relative}"
            )
        total_bytes += actual_size

    return {
        "validated_payload_file_count": len(expected),
        "validated_payload_bytes": total_bytes,
    }


def run_installed_executable_smoke(
    package_root: Path,
    *,
    executable_name: str,
    timeout_seconds: int = 90,
) -> dict:
    executable = (package_root / executable_name).resolve()
    if not executable.is_file() or executable.stat().st_size <= 0:
        raise CleanWindowsInstallReceiptError(
            f"installed executable is missing or empty: {executable}"
        )
    if not executable.is_relative_to(package_root.resolve()):
        raise CleanWindowsInstallReceiptError(
            "installed executable escaped the extracted package root"
        )
    try:
        result = subprocess.run(
            [str(executable), "--package-smoke"],
            cwd=package_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=int(timeout_seconds),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CleanWindowsInstallReceiptError(
            "installed executable package smoke timed out"
        ) from exc
    except OSError as exc:
        raise CleanWindowsInstallReceiptError(
            "installed executable could not be started"
        ) from exc
    if result.returncode != 0:
        raise CleanWindowsInstallReceiptError(
            "installed executable package smoke failed with exit code "
            f"{result.returncode}:\n{result.stdout[-4000:]}"
        )
    return {
        "installed_executable": executable.name,
        "installed_executable_sha256": _sha256_file(executable),
        "package_smoke_returncode": int(result.returncode),
        "package_smoke_output_tail": result.stdout[-2000:],
    }


def run_clean_windows_install_receipt(
    *,
    release_version: str,
    repository_commit: str,
    release_archive: str | Path,
    install_root: str | Path,
    output_dir: str | Path,
    repo_root: str | Path,
    executable_name: str = DEFAULT_EXECUTABLE,
) -> Path:
    windows = require_windows_11()
    root = Path(repo_root).resolve()
    archive = _require_outside_repo(
        release_archive,
        root,
        label="release archive",
    )
    identity = resolve_release_artifact_identity(
        release_version=release_version,
        repository_commit=repository_commit,
        release_archive=archive,
    )
    install = _require_outside_repo(
        install_root,
        root,
        label="clean install directory",
    )
    output = _require_outside_repo(
        output_dir,
        root,
        label="clean-install receipt directory",
    )
    if (
        output == install
        or output.is_relative_to(install)
        or install.is_relative_to(output)
    ):
        raise CleanWindowsInstallReceiptError(
            "clean-install receipt directory must be disjoint from install tree"
        )
    output.mkdir(parents=True, exist_ok=True)
    target = output / "clean_windows_install.json"
    if target.exists():
        raise CleanWindowsInstallReceiptError(
            f"receipt already exists; do not overwrite evidence: {target}"
        )

    package_root = _extract_fresh_archive(archive, install_root=install)
    manifest, manifest_path = _load_package_manifest(
        package_root,
        identity=identity,
        executable_name=executable_name,
    )
    payload_validation = validate_installed_payload(package_root, manifest)
    smoke = run_installed_executable_smoke(
        package_root,
        executable_name=executable_name,
    )

    receipt = {
        "passed": True,
        "audit_kind": "gate17_clean_windows_install",
        "repository_commit": identity.repository_commit,
        "release_version": identity.release_version,
        "release_archive_sha256": identity.release_archive_sha256,
        "release_archive_size": identity.release_archive_size,
        "windows_11": True,
        "outside_development_environment": True,
        **windows,
        "install_root": str(install),
        "package_root": str(package_root.resolve()),
        "package_manifest_sha256": _sha256_file(manifest_path),
        **payload_validation,
        **smoke,
    }
    try:
        return write_new_receipt(target, receipt)
    except Exception as exc:
        if isinstance(exc, CleanWindowsInstallReceiptError):
            raise
        raise CleanWindowsInstallReceiptError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--install-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--executable-name", default=DEFAULT_EXECUTABLE)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    path = run_clean_windows_install_receipt(
        release_version=args.release_version,
        repository_commit=args.repository_commit,
        release_archive=args.release_archive,
        install_root=args.install_root,
        output_dir=args.output_dir,
        repo_root=repo_root,
        executable_name=args.executable_name,
    )
    print(f"clean_windows_install: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
