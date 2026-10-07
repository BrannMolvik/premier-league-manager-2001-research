from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from gate17_minimal_package_candidate import (
    CANDIDATE_EXECUTABLE_NAME,
    CANDIDATE_REQUIRED_BUNDLED_FILES,
    MinimalPackageCandidateError,
    build_minimal_package_candidate,
    create_candidate_profile_marker,
)


class Gate17MinimalPackageCandidateTests(unittest.TestCase):
    def _proofs(self, root: Path):
        ffmpeg = root / "ffmpeg.exe"
        ffmpeg.write_bytes(b"minimal-ffmpeg")
        ffmpeg_sha = sha256(ffmpeg.read_bytes()).hexdigest()
        license_bytes = b"LGPL source license\n"
        license_sha = sha256(license_bytes).hexdigest()
        build = {
            "schema_version": 1,
            "audit_kind": "gate17_minimal_ffmpeg_build",
            "passed": True,
            "source_commit": "46d8f462eeb87ee1f704d8c44a0ee24fca471ad1",
            "source_license_file": "COPYING.LGPLv2.1",
            "source_license_sha256": license_sha,
            "ffmpeg_sha256": ffmpeg_sha,
            "build_verified": True,
            "synthetic_roundtrip_verified": False,
            "exact_original_tgq_verified": False,
            "external_windows11_playback_verified": False,
            "source_material_complete": False,
            "production_migration_ready": False,
            "legal_compliance_claimed": False,
        }
        build_path = root / "build-proof.json"
        build_path.write_text(json.dumps(build, sort_keys=True), encoding="utf-8")
        build_sha = sha256(build_path.read_bytes()).hexdigest()
        roundtrip = {
            "schema_version": 1,
            "audit_kind": "gate17_minimal_ffmpeg_synthetic_roundtrip",
            "passed": True,
            "build_proof_sha256": build_sha,
            "build_proof_ffmpeg_sha256": ffmpeg_sha,
            "canonical_video_encoder": "h264_mf",
            "canonical_audio_encoder": "aac",
            "build_verified": True,
            "synthetic_roundtrip_verified": True,
            "exact_original_tgq_verified": False,
            "external_windows11_playback_verified": False,
            "source_material_complete": False,
            "production_migration_ready": False,
            "legal_compliance_claimed": False,
        }
        roundtrip_path = root / "roundtrip-proof.json"
        roundtrip_path.write_text(
            json.dumps(roundtrip, sort_keys=True),
            encoding="utf-8",
        )
        return ffmpeg, build_path, roundtrip_path, license_bytes

    def _distribution(self, root: Path):
        proof_root = root / "proofs"
        proof_root.mkdir()
        ffmpeg, build, roundtrip, license_bytes = self._proofs(proof_root)
        dist = root / "dist"
        dist.mkdir()
        (dist / CANDIDATE_EXECUTABLE_NAME).write_bytes(b"candidate-exe")

        for relative in CANDIDATE_REQUIRED_BUNDLED_FILES:
            path = dist / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative == "runtime_tools/ffmpeg.exe":
                path.write_bytes(ffmpeg.read_bytes())
            elif relative == "runtime_tools/minimal-ffmpeg-build-proof.json":
                path.write_bytes(build.read_bytes())
            elif relative == "runtime_tools/minimal-ffmpeg-roundtrip-proof.json":
                path.write_bytes(roundtrip.read_bytes())
            elif relative == "runtime_tools/COPYING.LGPLv2.1":
                path.write_bytes(license_bytes)
            elif relative == "runtime_tools/startup-media-profile.json":
                create_candidate_profile_marker(
                    ffmpeg_executable=ffmpeg,
                    build_proof=build,
                    roundtrip_proof=roundtrip,
                    output_marker=path,
                )
            else:
                path.write_bytes(b"asset")
        return dist

    def test_marker_is_bound_to_build_roundtrip_and_helper(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ffmpeg, build, roundtrip, _license = self._proofs(root)
            marker = root / "marker.json"
            payload = create_candidate_profile_marker(
                ffmpeg_executable=ffmpeg,
                build_proof=build,
                roundtrip_proof=roundtrip,
                output_marker=marker,
            )
        self.assertTrue(payload["candidate_only"])
        self.assertEqual(payload["profile"]["video_encoder"], "h264_mf")
        self.assertTrue(payload["synthetic_roundtrip_verified"])
        self.assertFalse(payload["exact_original_tgq_verified"])
        self.assertFalse(payload["production_runtime_switched"])

    def test_roundtrip_self_promotion_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ffmpeg, build, roundtrip, _license = self._proofs(root)
            payload = json.loads(roundtrip.read_text(encoding="utf-8"))
            payload["production_migration_ready"] = True
            roundtrip.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                MinimalPackageCandidateError,
                "production_migration_ready=false",
            ):
                create_candidate_profile_marker(
                    ffmpeg_executable=ffmpeg,
                    build_proof=build,
                    roundtrip_proof=roundtrip,
                    output_marker=root / "marker.json",
                )

    def test_candidate_archive_stays_non_production_and_excludes_user_game_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dist = self._distribution(root)
            output = root / "output"
            result = build_minimal_package_candidate(
                dist_root=dist,
                output_dir=output,
                repo_root=Path(__file__).resolve().parents[1],
                release_version="test-head",
                repository_commit="a" * 40,
            )
            self.assertTrue(result["archive"].is_file())
            self.assertFalse(result["production_runtime_switched"])
            self.assertFalse(result["exact_original_tgq_verified"])
            with zipfile.ZipFile(result["archive"]) as zf:
                names = zf.namelist()
                self.assertTrue(
                    any(name.endswith("/runtime_tools/startup-media-profile.json") for name in names)
                )
                self.assertFalse(
                    any(name.lower().endswith("/master.dat") for name in names)
                )
                self.assertFalse(
                    any("third_party/ffmpeg/" in name.replace("\\", "/") for name in names)
                )

    def test_old_provider_provenance_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dist = self._distribution(root)
            old = dist / "_internal" / "third_party" / "ffmpeg" / "PROVENANCE.json"
            old.parent.mkdir(parents=True)
            old.write_text("{}", encoding="utf-8")
            output = root / "output"
            with self.assertRaisesRegex(
                MinimalPackageCandidateError,
                "old provider provenance",
            ):
                build_minimal_package_candidate(
                    dist_root=dist,
                    output_dir=output,
                    repo_root=Path(__file__).resolve().parents[1],
                    release_version="test-head",
                    repository_commit="a" * 40,
                )


if __name__ == "__main__":
    unittest.main()
