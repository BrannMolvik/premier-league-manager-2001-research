"""Tests for the exact minimal FFmpeg Windows build audit."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate17_ffmpeg_minimal_build_audit import (
    MinimalFfmpegBuildAuditError,
    _parse_imports,
    _version_contract,
    audit_minimal_build,
)
from gate17_ffmpeg_minimal_source_contract import CONTRACT_PATH, PINNED_FFMPEG_COMMIT


def contract_payload():
    repo = Path(__file__).resolve().parent.parent
    return json.loads((repo / CONTRACT_PATH).read_text(encoding="utf-8"))


def version_output(label: str, args: list[str]) -> str:
    return (
        f"{label} version git-2026-09-30-46d8f46\n"
        "built with gcc synthetic\n"
        "configuration: " + " ".join(args) + "\n"
    )


DECODERS = "\n".join(
    f" V....D {name} synthetic"
    for name in (
        "eatgq","adpcm_ea","adpcm_ea_r1","adpcm_ea_r2","adpcm_ea_r3",
        "adpcm_ima_ea_eacs","adpcm_ima_ea_sead","adpcm_psx","pcm_mulaw",
        "pcm_s16le","pcm_s16le_planar","pcm_s8","mp3","h264","aac"
    )
)
ENCODERS = " V..... h264_mf synthetic\n A..... aac synthetic\n"
DEMUXERS = " D  ea synthetic\n D  mov,mp4,m4a synthetic\n"
MUXERS = " E  mp4 synthetic\n E  null synthetic\n"
PROTOCOLS = "Input:\n  file\n  pipe\nOutput:\n  file\n  pipe\n"
FILTERS = " ... aresample A->A synthetic\n ... scale V->V synthetic\n"


class Gate17MinimalFfmpegBuildAuditTests(unittest.TestCase):
    def fixture(self, temp: str):
        root = Path(temp)
        repo = root / "repo"
        contract_path = repo / CONTRACT_PATH
        contract_path.parent.mkdir(parents=True)
        contract_path.write_text(json.dumps(contract_payload(), indent=2) + "\n", encoding="utf-8")
        ffmpeg = root / "ffmpeg.exe"
        ffprobe = root / "ffprobe.exe"
        ffmpeg.write_bytes(b"minimal-ffmpeg")
        ffprobe.write_bytes(b"minimal-ffprobe")
        source_commit = root / "source-commit.txt"
        source_commit.write_text(PINNED_FFMPEG_COMMIT + "\n", encoding="utf-8")
        license_file = root / "COPYING.LGPLv2.1"
        license_file.write_text("synthetic LGPL source license\n", encoding="utf-8")
        imports = root / "imports.txt"
        imports.write_text(
            "DLL Name: KERNEL32.dll\nDLL Name: mfplat.dll\nDLL Name: ole32.dll\n",
            encoding="utf-8",
        )
        return repo, ffmpeg, ffprobe, source_commit, license_file, imports

    def runner(self, args):
        def run(executable, *command):
            name = Path(executable).name.lower()
            if command == ("-version",):
                label = "ffprobe" if name.startswith("ffprobe") else "ffmpeg"
                return version_output(label, args)
            if command[-1:] == ("-decoders",):
                return DECODERS
            if command[-1:] == ("-encoders",):
                return ENCODERS
            if command[-1:] == ("-demuxers",):
                return DEMUXERS
            if command[-1:] == ("-muxers",):
                return MUXERS
            if command[-1:] == ("-protocols",):
                return PROTOCOLS
            if command[-1:] == ("-filters",):
                return FILTERS
            raise AssertionError(command)
        return run

    def test_complete_build_receipt_still_keeps_later_proofs_false(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, ffmpeg, ffprobe, source_commit, license_file, imports = self.fixture(temp)
            args = contract_payload()["minimal_helper_target"]["configure_args"]
            with patch(
                "gate17_ffmpeg_minimal_build_audit._run",
                side_effect=self.runner(args),
            ):
                result = audit_minimal_build(
                    repo_root=repo,
                    ffmpeg_exe=ffmpeg,
                    ffprobe_exe=ffprobe,
                    source_commit_file=source_commit,
                    source_license_file=license_file,
                    ffmpeg_imports_file=imports,
                    ffprobe_imports_file=imports,
                )

        self.assertTrue(result["passed"])
        self.assertTrue(result["build_verified"])
        self.assertFalse(result["synthetic_roundtrip_verified"])
        self.assertFalse(result["exact_original_tgq_verified"])
        self.assertFalse(result["external_windows11_playback_verified"])
        self.assertFalse(result["source_material_complete"])
        self.assertFalse(result["production_migration_ready"])
        self.assertFalse(result["legal_compliance_claimed"])

    def test_configuration_accepts_ffmpeg_expanded_component_lists(self):
        args = contract_payload()["minimal_helper_target"]["configure_args"]
        expanded = []
        for arg in args:
            if arg.startswith((
                "--enable-protocol=",
                "--enable-decoder=",
                "--enable-encoder=",
                "--enable-demuxer=",
                "--enable-muxer=",
                "--enable-filter=",
            )) and "," in arg:
                option, values = arg.split("=", 1)
                expanded.extend(f"{option}={value}" for value in values.split(","))
            else:
                expanded.append(arg)

        result = _version_contract(
            version_output("ffmpeg", expanded),
            label="ffmpeg",
            configure_args=args,
        )
        self.assertEqual(result["third_party_enable_flags"], [])

        expanded.remove("--enable-protocol=pipe")
        with self.assertRaisesRegex(
            MinimalFfmpegBuildAuditError,
            "--enable-protocol=pipe",
        ):
            _version_contract(
                version_output("ffmpeg", expanded),
                label="ffmpeg",
                configure_args=args,
            )

    def test_wrong_source_commit_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, ffmpeg, ffprobe, source_commit, license_file, imports = self.fixture(temp)
            source_commit.write_text("0" * 40 + "\n", encoding="utf-8")
            with self.assertRaisesRegex(MinimalFfmpegBuildAuditError, "source commit drifted"):
                audit_minimal_build(
                    repo_root=repo,
                    ffmpeg_exe=ffmpeg,
                    ffprobe_exe=ffprobe,
                    source_commit_file=source_commit,
                    source_license_file=license_file,
                    ffmpeg_imports_file=imports,
                    ffprobe_imports_file=imports,
                )

    def test_import_guard_rejects_mingw_or_msys_runtime_dlls(self):
        for name in (
            "libgcc_s_seh-1.dll",
            "libstdc++-6.dll",
            "libwinpthread-1.dll",
            "libssp-0.dll",
            "msys-2.0.dll",
        ):
            with self.subTest(name=name):
                with self.assertRaisesRegex(
                    MinimalFfmpegBuildAuditError,
                    "unexpected toolchain/runtime DLLs",
                ):
                    _parse_imports(
                        f"DLL Name: KERNEL32.dll\nDLL Name: {name}\n",
                        label="ffmpeg.exe",
                    )

    def test_configuration_rejects_third_party_enable_flag(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, ffmpeg, ffprobe, source_commit, license_file, imports = self.fixture(temp)
            args = contract_payload()["minimal_helper_target"]["configure_args"]
            polluted = args + ["--enable-libx264"]
            with patch(
                "gate17_ffmpeg_minimal_build_audit._run",
                side_effect=self.runner(polluted),
            ):
                with self.assertRaisesRegex(
                    MinimalFfmpegBuildAuditError,
                    "third-party libraries",
                ):
                    audit_minimal_build(
                        repo_root=repo,
                        ffmpeg_exe=ffmpeg,
                        ffprobe_exe=ffprobe,
                        source_commit_file=source_commit,
                        source_license_file=license_file,
                        ffmpeg_imports_file=imports,
                        ffprobe_imports_file=imports,
                    )


if __name__ == "__main__":
    unittest.main()
