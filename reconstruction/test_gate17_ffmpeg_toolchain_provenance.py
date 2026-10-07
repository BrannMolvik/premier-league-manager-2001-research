"""Tests for Gate-17 minimal FFmpeg toolchain provenance."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from gate17_ffmpeg_toolchain_provenance import (
    CONTRACT_PATH,
    MinimalFfmpegToolchainError,
    audit_critical_source_material,
    audit_toolchain,
    parse_package_list,
)


def canonical_contract():
    repo=Path(__file__).resolve().parent.parent
    return json.loads((repo/CONTRACT_PATH).read_text(encoding="utf-8"))


class Gate17MinimalFfmpegToolchainTests(unittest.TestCase):
    def fixture(self, temp):
        root=Path(temp)
        repo=root/"repo"
        path=repo/CONTRACT_PATH
        path.parent.mkdir(parents=True)
        payload=canonical_contract()
        path.write_text(json.dumps(payload),encoding="utf-8")
        packages=root/"packages.txt"
        rows=["base-files 2026.01-1"]
        rows.extend(
            f"{name} {version}"
            for name,version in payload["required_package_versions"].items()
        )
        packages.write_text("\n".join(rows)+"\n",encoding="utf-8")
        return repo,packages,payload

    def test_exact_required_subset_passes_without_claiming_completeness(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,packages,payload=self.fixture(temp)
            result=audit_toolchain(repo_root=repo,package_list=packages)
        self.assertTrue(result["passed"])
        self.assertFalse(result["complete_package_lock"])
        self.assertFalse(result["source_material_complete"])
        self.assertFalse(result["legal_compliance_claimed"])
        self.assertEqual(
            result["required_package_versions"],
            dict(sorted(payload["required_package_versions"].items())),
        )
        self.assertEqual(
            result["critical_source_material"]["critical_package_count"],
            len(payload["required_package_versions"]),
        )
        self.assertEqual(
            result["critical_source_material"]["source_family_count"],
            8,
        )
        self.assertEqual(
            result["critical_source_material"]["verified_source_family_count"],
            6,
        )
        self.assertEqual(
            result["critical_source_material"]["unverified_source_families"],
            ["mingw-w64-crt", "msys2-runtime"],
        )

    def test_version_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,packages,_=self.fixture(temp)
            text=packages.read_text(encoding="utf-8")
            packages.write_text(
                text.replace(
                    "mingw-w64-ucrt-x86_64-gcc 16.2.0-4",
                    "mingw-w64-ucrt-x86_64-gcc 16.2.0-5",
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                MinimalFfmpegToolchainError,"package versions drifted"
            ):
                audit_toolchain(repo_root=repo,package_list=packages)

    def test_missing_required_package_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,packages,_=self.fixture(temp)
            rows=[
                line for line in packages.read_text(encoding="utf-8").splitlines()
                if not line.startswith("mingw-w64-ucrt-x86_64-crt ")
            ]
            packages.write_text("\n".join(rows)+"\n",encoding="utf-8")
            with self.assertRaisesRegex(
                MinimalFfmpegToolchainError,"package versions drifted"
            ):
                audit_toolchain(repo_root=repo,package_list=packages)

    def test_source_material_plan_covers_every_required_package(self):
        payload=canonical_contract()
        del payload["critical_package_source_material"]["package_to_source_family"][
            "mingw-w64-ucrt-x86_64-crt"
        ]
        with self.assertRaisesRegex(
            MinimalFfmpegToolchainError,"package coverage drifted"
        ):
            audit_critical_source_material(payload)

    def test_source_material_family_version_must_match_binary_package(self):
        payload=canonical_contract()
        payload["critical_package_source_material"]["source_families"][
            "mingw-w64-gcc"
        ]["binary_version"]="16.2.0-5"
        with self.assertRaisesRegex(
            MinimalFfmpegToolchainError,"family version drifted"
        ):
            audit_critical_source_material(payload)

    def test_unverified_source_family_cannot_publish_guessed_tarball(self):
        payload=canonical_contract()
        payload["critical_package_source_material"]["source_families"][
            "msys2-runtime"
        ]["source_only_tarball"]=(
            "https://mirror.msys2.org/msys/sources/"
            "msys2-runtime-3.6.10-6.src.tar.zst"
        )
        with self.assertRaisesRegex(
            MinimalFfmpegToolchainError,"must not publish a tarball URL"
        ):
            audit_critical_source_material(payload)

    def test_source_material_plan_cannot_claim_completeness(self):
        payload=canonical_contract()
        payload["critical_package_source_material"]["source_material_complete"]=True
        with self.assertRaisesRegex(
            MinimalFfmpegToolchainError,"source_material_complete=false"
        ):
            audit_critical_source_material(payload)

    def test_package_parser_rejects_duplicates(self):
        with self.assertRaisesRegex(MinimalFfmpegToolchainError,"duplicate"):
            parse_package_list("gcc 1\ngcc 1\n")


if __name__=="__main__":
    unittest.main()
