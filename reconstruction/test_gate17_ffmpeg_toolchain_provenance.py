"""Tests for Gate-17 minimal FFmpeg toolchain provenance."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from gate17_ffmpeg_toolchain_provenance import (
    CONTRACT_PATH,
    PACKAGE_LOCK_PATH,
    MinimalFfmpegToolchainError,
    audit_critical_source_material,
    audit_toolchain,
    parse_package_list,
)


def canonical_contract():
    repo=Path(__file__).resolve().parent.parent
    return json.loads((repo/CONTRACT_PATH).read_text(encoding="utf-8"))


def canonical_lock_text():
    repo=Path(__file__).resolve().parent.parent
    return (repo/PACKAGE_LOCK_PATH).read_text(encoding="utf-8")


class Gate17MinimalFfmpegToolchainTests(unittest.TestCase):
    def fixture(self, temp):
        root=Path(temp)
        repo=root/"repo"
        path=repo/CONTRACT_PATH
        path.parent.mkdir(parents=True)
        payload=canonical_contract()
        path.write_text(json.dumps(payload),encoding="utf-8")
        lock_path=repo/PACKAGE_LOCK_PATH
        lock_path.parent.mkdir(parents=True,exist_ok=True)
        lock_text=canonical_lock_text()
        lock_path.write_text(lock_text,encoding="utf-8")
        packages=root/"packages.txt"
        packages.write_text(lock_text,encoding="utf-8")
        return repo,packages,payload

    def test_exact_complete_lock_passes_without_claiming_source_completeness(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,packages,payload=self.fixture(temp)
            result=audit_toolchain(repo_root=repo,package_list=packages)
        self.assertTrue(result["passed"])
        self.assertTrue(result["complete_package_lock"])
        self.assertEqual(result["package_lock"]["package_count"],151)
        self.assertEqual(
            result["package_lock"]["sha256"],
            "c1e79ae6500dd48a206fa786f9f863f37cdc788e6f2dbfba0c926e999077abec",
        )
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
            8,
        )
        self.assertEqual(
            result["critical_source_material"]["unverified_source_families"],
            [],
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

    def test_noncritical_version_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,packages,_=self.fixture(temp)
            text=packages.read_text(encoding="utf-8")
            packages.write_text(
                text.replace("bash 5.3.020-1","bash 5.3.020-2"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                MinimalFfmpegToolchainError,"complete UCRT64 package lock drifted"
            ):
                audit_toolchain(repo_root=repo,package_list=packages)

    def test_extra_package_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,packages,_=self.fixture(temp)
            with packages.open("a",encoding="utf-8") as handle:
                handle.write("synthetic-extra-package 1\n")
            with self.assertRaisesRegex(
                MinimalFfmpegToolchainError,"complete UCRT64 package lock drifted"
            ):
                audit_toolchain(repo_root=repo,package_list=packages)

    def test_missing_noncritical_package_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,packages,_=self.fixture(temp)
            rows=[
                line for line in packages.read_text(encoding="utf-8").splitlines()
                if not line.startswith("nano ")
            ]
            packages.write_text("\n".join(rows)+"\n",encoding="utf-8")
            with self.assertRaisesRegex(
                MinimalFfmpegToolchainError,"complete UCRT64 package lock drifted"
            ):
                audit_toolchain(repo_root=repo,package_list=packages)

    def test_package_lock_digest_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo,packages,payload=self.fixture(temp)
            payload["package_lock"]["sha256"]="0"*64
            (repo/CONTRACT_PATH).write_text(
                json.dumps(payload),encoding="utf-8"
            )
            with self.assertRaisesRegex(
                MinimalFfmpegToolchainError,"package-lock digest drifted"
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
        family=payload["critical_package_source_material"]["source_families"][
            "msys2-runtime"
        ]
        family["source_tarball_metadata_verified"]=False
        family["note"]="Synthetic unresolved family used to exercise fail-closed behavior."
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
