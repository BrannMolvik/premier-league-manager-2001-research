"""Tests for the fail-closed Gate-17 FFmpeg provenance boundary."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from gate17_third_party_ffmpeg import (
    ThirdPartyFFmpegError,
    create_binary_attestation,
    load_ffmpeg_provenance,
    validate_ffmpeg_version_output,
    validate_release_archive_ffmpeg,
)


VERSION_OUTPUT = """ffmpeg version 7.1-essentials_build-www.gyan.dev Copyright (c) 2000-2024 the FFmpeg developers
built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
configuration: --enable-gpl --enable-version3 --enable-static --enable-libx264 --enable-libx265 --enable-librubberband
libavutil      59. 39.100 / 59. 39.100
libavcodec     61. 19.100 / 61. 19.100
libavformat    61.  7.100 / 61.  7.100
libavdevice    61.  3.100 / 61.  3.100
libavfilter    10.  4.100 / 10.  4.100
libswscale      8.  3.100 /  8.  3.100
libswresample   5.  3.100 /  5.  3.100
libpostproc    58.  3.100 / 58.  3.100
"""


def provenance_payload(*, release_ready=False, required_hashes=None):
    required = [
        "third_party/ffmpeg/LICENSE.txt",
        "third_party/ffmpeg/SOURCE-PROVENANCE.json",
    ]
    return {
        "schema_version": 1,
        "component": "FFmpeg",
        "bundled_binary_path": "runtime_tools/ffmpeg.exe",
        "provider_package": {
            "name": "imageio-ffmpeg",
            "version": "0.6.0",
            "wheel_observed": "imageio_ffmpeg-0.6.0-py3-none-win_amd64.whl",
            "release_url": "https://example.invalid/imageio",
        },
        "observed_package_run": {
            "workflow_run_id": 1,
            "job_id": 2,
            "repository_commit": "a" * 40,
        },
        "binary_identity": {
            "version_line": VERSION_OUTPUT.splitlines()[0],
            "compiler_line": VERSION_OUTPUT.splitlines()[1],
            "required_configuration_flags": [
                "--enable-gpl",
                "--enable-version3",
                "--enable-static",
                "--enable-libx264",
                "--enable-libx265",
                "--enable-librubberband",
            ],
            "library_versions": {
                "libavutil": "59. 39.100",
                "libavcodec": "61. 19.100",
                "libavformat": "61.  7.100",
                "libavdevice": "61.  3.100",
                "libavfilter": "10.  4.100",
                "libswscale": "8.  3.100",
                "libswresample": "5.  3.100",
                "libpostproc": "58.  3.100",
            },
        },
        "upstream_references": {},
        "release_materials": {
            "release_ready": release_ready,
            "license_material_complete": release_ready,
            "source_material_complete": release_ready,
            "required_files": required,
            "sha256": required_hashes or {},
        },
        "legal_boundary": "synthetic",
    }


def write_repo(root: Path, payload: dict) -> Path:
    path = root / "third_party" / "ffmpeg" / "PROVENANCE.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


class Gate17ThirdPartyFFmpegTests(unittest.TestCase):
    def test_canonical_repository_manifest_is_intentionally_not_release_ready(self):
        repo = Path(__file__).resolve().parent.parent
        payload, _path = load_ffmpeg_provenance(repo)

        self.assertEqual(payload["provider_package"]["version"], "0.6.0")
        self.assertFalse(payload["release_materials"]["release_ready"])
        self.assertFalse(payload["release_materials"]["license_material_complete"])
        self.assertFalse(payload["release_materials"]["source_material_complete"])

    def test_version_output_requires_exact_identity_and_gpl_flags(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            payload = provenance_payload()
            write_repo(repo, payload)

            result = validate_ffmpeg_version_output(VERSION_OUTPUT, payload)
            self.assertEqual(result["version_line"], payload["binary_identity"]["version_line"])

            with self.assertRaisesRegex(ThirdPartyFFmpegError, "configuration lost"):
                validate_ffmpeg_version_output(
                    VERSION_OUTPUT.replace(" --enable-libx264", ""),
                    payload,
                )

    def test_binary_attestation_hash_binds_executable_and_repository_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            provenance_path = write_repo(repo, provenance_payload())
            exe = Path(temp) / "ffmpeg.exe"
            exe.write_bytes(b"synthetic-ffmpeg")
            out = Path(temp) / "ffmpeg.provenance.json"

            completed = type(
                "Completed",
                (),
                {"returncode": 0, "stdout": VERSION_OUTPUT},
            )()
            with patch(
                "gate17_third_party_ffmpeg.subprocess.run",
                return_value=completed,
            ):
                attestation = create_binary_attestation(
                    ffmpeg_exe=exe,
                    repo_root=repo,
                    output_path=out,
                )

            self.assertEqual(
                attestation["binary_sha256"],
                sha256(exe.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                attestation["repository_provenance_sha256"],
                sha256(provenance_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                json.loads(out.read_text(encoding="utf-8"))["binary_size_bytes"],
                len(exe.read_bytes()),
            )

    def test_final_archive_rejects_incomplete_release_materials_before_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            write_repo(repo, provenance_payload())
            archive = root / "candidate.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("FM/runtime_tools/ffmpeg.exe", b"ffmpeg")

            with self.assertRaisesRegex(
                ThirdPartyFFmpegError,
                "release materials are not declared complete",
            ):
                validate_release_archive_ffmpeg(
                    repo_root=repo,
                    release_archive=archive,
                )

    def test_complete_archive_requires_hash_bound_binary_provenance_and_materials(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            license_bytes = b"license material"
            source_bytes = b"source provenance material"
            hashes = {
                "third_party/ffmpeg/LICENSE.txt": sha256(license_bytes).hexdigest(),
                "third_party/ffmpeg/SOURCE-PROVENANCE.json": sha256(source_bytes).hexdigest(),
            }
            provenance_path = write_repo(
                repo,
                provenance_payload(
                    release_ready=True,
                    required_hashes=hashes,
                ),
            )
            binary = b"ffmpeg binary"
            attestation = {
                "schema_version": 1,
                "component": "FFmpeg",
                "binary_path": "runtime_tools/ffmpeg.exe",
                "binary_sha256": sha256(binary).hexdigest(),
                "binary_size_bytes": len(binary),
                "repository_provenance_path": "third_party/ffmpeg/PROVENANCE.json",
                "repository_provenance_sha256": sha256(provenance_path.read_bytes()).hexdigest(),
                "provider_package": {
                    "name": "imageio-ffmpeg",
                    "version": "0.6.0",
                },
            }
            archive = root / "candidate.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("FM/runtime_tools/ffmpeg.exe", binary)
                zf.writestr(
                    "FM/runtime_tools/ffmpeg.provenance.json",
                    json.dumps(attestation),
                )
                zf.writestr(
                    "FM/third_party/ffmpeg/PROVENANCE.json",
                    provenance_path.read_bytes(),
                )
                zf.writestr("FM/third_party/ffmpeg/LICENSE.txt", license_bytes)
                zf.writestr(
                    "FM/third_party/ffmpeg/SOURCE-PROVENANCE.json",
                    source_bytes,
                )

            result = validate_release_archive_ffmpeg(
                repo_root=repo,
                release_archive=archive,
            )

            self.assertTrue(result["release_materials_complete"])
            self.assertFalse(result["legal_compliance_claimed"])
            self.assertEqual(result["binary_sha256"], sha256(binary).hexdigest())


if __name__ == "__main__":
    unittest.main()
