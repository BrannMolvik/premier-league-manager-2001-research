"""Build a provenance-bounded FM2001 Windows 11 release candidate.

The package contains the modern frozen runtime plus original assets that were
intentionally imported under original_assets/ and already pass repository asset
policy. It deliberately does not bundle the user's original FM2001 database,
FOOTBAL.EXE, disc images, extraction dumps, or private audit receipts.

The release archive and its SHA-256 manifest are written outside the Git
checkout. The packaged executable is smoke-tested with --help before archiving.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

from gate17_release_readiness import require_windows_11


PYINSTALLER_VERSION = "6.22.3"
APP_NAME = "FM2001-Windows11"
FORBIDDEN_RELEASE_NAMES = frozenset(
    {
        "FOOTBAL.EXE",
        "Master.dat",
        "Static.dat",
    }
)
FORBIDDEN_DISC_SUFFIXES = frozenset(
    {
        ".bin",
        ".cue",
        ".iso",
        ".mdf",
        ".mds",
        ".nrg",
    }
)


class WindowsPackageError(RuntimeError):
    """A release candidate package violates the Gate-17 build boundary."""


@dataclass(frozen=True)
class ReleasePackageManifest:
    schema_version: int
    release_version: str
    repository_commit: str
    archive_name: str
    archive_sha256: str
    archive_size_bytes: int
    app_name: str
    pyinstaller_version: str
    bundled_original_asset_file_count: int


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(command: list[str], *, cwd: Path, label: str, timeout: int = 600) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise WindowsPackageError(
            f"{label} failed with exit code {result.returncode}:\n"
            + result.stdout[-5000:]
        )
    return result.stdout


def _git(repo_root: Path, *args: str) -> str:
    return _run(
        ["git", *args],
        cwd=repo_root,
        label="git " + " ".join(args),
        timeout=60,
    ).strip()


def require_clean_release_commit(
    repo_root: str | Path,
    expected_commit: str,
) -> str:
    root = Path(repo_root).resolve()
    expected = str(expected_commit)
    if re.fullmatch(r"[0-9a-f]{40}", expected) is None:
        raise WindowsPackageError(
            "repository_commit must be a lowercase 40-character Git SHA"
        )
    actual = _git(root, "rev-parse", "HEAD")
    if actual != expected:
        raise WindowsPackageError(
            f"release checkout is {actual}, expected {expected}"
        )
    status = _git(root, "status", "--porcelain")
    if status:
        raise WindowsPackageError(
            "release checkout must be clean before packaging"
        )
    return actual


def require_output_directory_outside_repo(
    output_dir: str | Path,
    repo_root: str | Path,
) -> Path:
    output = Path(output_dir).resolve()
    root = Path(repo_root).resolve()
    if output.is_relative_to(root):
        raise WindowsPackageError(
            "release package output must be outside the Git repository"
        )
    output.mkdir(parents=True, exist_ok=True)
    return output


def require_pyinstaller_version() -> str:
    try:
        version = importlib.metadata.version("pyinstaller")
    except importlib.metadata.PackageNotFoundError as exc:
        raise WindowsPackageError(
            f"PyInstaller {PYINSTALLER_VERSION} is required"
        ) from exc
    if version != PYINSTALLER_VERSION:
        raise WindowsPackageError(
            f"PyInstaller {PYINSTALLER_VERSION} is required, found {version}"
        )
    return version


def _safe_release_version(value: str) -> str:
    value = str(value).strip()
    if not value:
        raise WindowsPackageError("release_version must be non-empty")
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    if not safe:
        raise WindowsPackageError("release_version has no filename-safe content")
    return safe


def count_bundled_original_assets(repo_root: str | Path) -> int:
    source = Path(repo_root).resolve() / "original_assets"
    if not source.is_dir():
        raise WindowsPackageError("original_assets directory is missing")
    files = tuple(path for path in source.rglob("*") if path.is_file())
    if not files:
        raise WindowsPackageError("original_assets contains no files")
    return len(files)


def validate_package_contents(package_dir: str | Path) -> dict:
    root = Path(package_dir).resolve()
    if not root.is_dir():
        raise WindowsPackageError(f"package directory is missing: {root}")
    files = tuple(path for path in root.rglob("*") if path.is_file())
    if not files:
        raise WindowsPackageError("package directory is empty")

    forbidden_names = [
        path for path in files
        if path.name in FORBIDDEN_RELEASE_NAMES
    ]
    if forbidden_names:
        raise WindowsPackageError(
            "release candidate contains original game data/executable: "
            + ", ".join(str(path.relative_to(root)) for path in forbidden_names)
        )
    forbidden_disc = [
        path for path in files
        if path.suffix.lower() in FORBIDDEN_DISC_SUFFIXES
    ]
    if forbidden_disc:
        raise WindowsPackageError(
            "release candidate contains raw disc-image material: "
            + ", ".join(str(path.relative_to(root)) for path in forbidden_disc)
        )

    exe = root / f"{APP_NAME}.exe"
    if not exe.is_file() or exe.stat().st_size <= 0:
        raise WindowsPackageError(
            f"packaged executable is missing: {exe.name}"
        )
    asset_manifest = root / "_internal" / "original_assets" / "MANIFEST.md"
    if not asset_manifest.is_file():
        # PyInstaller layout may put data beside the executable when configured
        # with a different contents directory; accept that exact alternate.
        asset_manifest = root / "original_assets" / "MANIFEST.md"
    if not asset_manifest.is_file():
        raise WindowsPackageError(
            "packaged provenance manifest original_assets/MANIFEST.md is missing"
        )

    return {
        "file_count": len(files),
        "executable": str(exe),
        "asset_manifest": str(asset_manifest),
    }


def write_package_build_info(
    package_dir: str | Path,
    *,
    release_version: str,
    repository_commit: str,
    pyinstaller_version: str,
) -> Path:
    root = Path(package_dir)
    path = root / "BUILD_INFO.json"
    if path.exists():
        raise WindowsPackageError("BUILD_INFO.json already exists")
    payload = {
        "schema_version": 1,
        "release_version": str(release_version),
        "repository_commit": str(repository_commit),
        "app_name": APP_NAME,
        "pyinstaller_version": str(pyinstaller_version),
        "original_game_data_bundled": False,
        "original_game_data_requirement": (
            "User supplies an authorized FM2001 installation containing "
            "Master.dat and FOOTBAL.EXE."
        ),
    }
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def write_release_readme(package_dir: str | Path) -> Path:
    path = Path(package_dir) / "README-WINDOWS11.txt"
    if path.exists():
        raise WindowsPackageError("README-WINDOWS11.txt already exists")
    path.write_text(
        "FM2001 Windows 11 modernization\n"
        "================================\n\n"
        "This candidate contains the modern compatibility runtime and the "
        "provenance-tracked original presentation assets intentionally "
        "imported by the project.\n\n"
        "It does NOT include Master.dat, Static.dat, FOOTBAL.EXE, raw disc "
        "images, or a complete copy of the original game. On first launch, "
        "select your authorized original FM2001 installation when prompted.\n\n"
        "Known limitations are tracked by the repository release audit. A "
        "candidate archive is not a final release until the Gate-17 Windows "
        "audit passes.\n",
        encoding="utf-8",
    )
    return path


def create_deterministic_zip(
    package_dir: str | Path,
    archive_path: str | Path,
) -> Path:
    root = Path(package_dir).resolve()
    archive = Path(archive_path).resolve()
    if archive.exists():
        raise WindowsPackageError(f"release archive already exists: {archive}")
    archive.parent.mkdir(parents=True, exist_ok=True)

    base = root.parent
    files = sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(base).as_posix().lower(),
    )
    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as handle:
        for path in files:
            arcname = path.relative_to(base).as_posix()
            info = zipfile.ZipInfo(arcname)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            handle.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)

    if archive.stat().st_size <= 0:
        raise WindowsPackageError("release archive is empty")
    return archive


def write_external_manifest(
    path: str | Path,
    manifest: ReleasePackageManifest,
) -> Path:
    target = Path(path)
    if target.exists():
        raise WindowsPackageError(f"release manifest already exists: {target}")
    target.write_text(
        json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def build_windows_release_candidate(
    *,
    repo_root: str | Path,
    output_dir: str | Path,
    release_version: str,
    repository_commit: str,
) -> dict:
    windows = require_windows_11()
    root = Path(repo_root).resolve()
    output = require_output_directory_outside_repo(output_dir, root)
    safe_version = _safe_release_version(release_version)
    require_clean_release_commit(root, repository_commit)
    pyinstaller_version = require_pyinstaller_version()
    asset_count = count_bundled_original_assets(root)

    archive = output / f"{APP_NAME}-{safe_version}.zip"
    manifest_path = output / f"{APP_NAME}-{safe_version}.manifest.json"
    if archive.exists() or manifest_path.exists():
        raise WindowsPackageError(
            "release output already contains this version; use a fresh output directory"
        )

    with tempfile.TemporaryDirectory(prefix="fm2001-gate17-package-") as temp:
        temp_root = Path(temp)
        dist = temp_root / "dist"
        work = temp_root / "build"
        spec = temp_root / "spec"
        data_arg = (
            str(root / "original_assets")
            + os.pathsep
            + "original_assets"
        )
        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--windowed",
            "--onedir",
            "--name",
            APP_NAME,
            "--paths",
            str(root / "reconstruction"),
            "--add-data",
            data_arg,
            "--distpath",
            str(dist),
            "--workpath",
            str(work),
            "--specpath",
            str(spec),
            str(root / "reconstruction" / "app.py"),
        ]
        _run(command, cwd=root, label="PyInstaller build", timeout=900)

        built = dist / APP_NAME
        validate_package_contents(built)
        write_package_build_info(
            built,
            release_version=release_version,
            repository_commit=repository_commit,
            pyinstaller_version=pyinstaller_version,
        )
        write_release_readme(built)
        validation = validate_package_contents(built)

        _run(
            [str(built / f"{APP_NAME}.exe"), "--help"],
            cwd=built,
            label="packaged executable --help smoke",
            timeout=60,
        )

        package_dir = output / f"{APP_NAME}-{safe_version}"
        if package_dir.exists():
            raise WindowsPackageError(
                f"release package directory already exists: {package_dir}"
            )
        shutil.copytree(built, package_dir)
        validate_package_contents(package_dir)
        create_deterministic_zip(package_dir, archive)

    manifest = ReleasePackageManifest(
        schema_version=1,
        release_version=str(release_version),
        repository_commit=str(repository_commit),
        archive_name=archive.name,
        archive_sha256=_sha256_file(archive),
        archive_size_bytes=archive.stat().st_size,
        app_name=APP_NAME,
        pyinstaller_version=pyinstaller_version,
        bundled_original_asset_file_count=asset_count,
    )
    write_external_manifest(manifest_path, manifest)

    # Packaging must not dirty the release checkout.
    status_after = _git(root, "status", "--porcelain")
    if status_after:
        raise WindowsPackageError(
            "release packaging dirtied the Git checkout"
        )

    return {
        "windows": windows,
        "package_dir": str(package_dir),
        "archive": str(archive),
        "manifest": str(manifest_path),
        "archive_sha256": manifest.archive_sha256,
        "archive_size_bytes": manifest.archive_size_bytes,
        "bundled_original_asset_file_count": asset_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    report = build_windows_release_candidate(
        repo_root=repo_root,
        output_dir=args.output_dir,
        release_version=args.release_version,
        repository_commit=args.repository_commit,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
