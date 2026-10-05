"""Tests for the Gate-17 minimal FFmpeg source/provenance contract."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from gate17_ffmpeg_minimal_source_contract import (
    CONTRACT_PATH,
    MinimalFfmpegSourceContractError,
    audit_source_contract,
)


class Gate17MinimalFfmpegSourceContractTests(unittest.TestCase):
    def canonical(self):
        repo = Path(__file__).resolve().parent.parent
        return json.loads((repo / CONTRACT_PATH).read_text(encoding="utf-8"))

    def write_contract(self, root: Path, payload: dict):
        path = root / CONTRACT_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_canonical_contract_is_fail_closed_and_not_production_ready(self):
        repo = Path(__file__).resolve().parent.parent
        result = audit_source_contract(repo)

        self.assertTrue(result["broad_candidate_pinned"])
        self.assertFalse(result["broad_candidate_minimal"])
        self.assertEqual(result["minimal_helper_external_library_flags"], [])
        self.assertEqual(result["minimal_helper_ea_codec_superset_count"], 13)
        self.assertFalse(result["minimal_helper_production_migration_ready"])
        self.assertFalse(result["legal_compliance_claimed"])
        self.assertTrue(
            all(value is False for value in result["minimal_helper_proofs"].values())
        )

    def test_minimal_contract_requires_mediafoundation_after_disabling_autodetect(self):
        payload = self.canonical()
        payload["minimal_helper_target"]["configure_args"].remove("--enable-mediafoundation")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_contract(root, payload)
            with self.assertRaisesRegex(
                MinimalFfmpegSourceContractError,
                "explicitly re-enable Windows Media Foundation",
            ):
                audit_source_contract(root)

    def test_minimal_contract_requires_w32threads_after_disabling_autodetect(self):
        payload = self.canonical()
        payload["minimal_helper_target"]["configure_args"].remove("--enable-w32threads")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_contract(root, payload)
            with self.assertRaisesRegex(
                MinimalFfmpegSourceContractError,
                "explicitly re-enable native Windows threads",
            ):
                audit_source_contract(root)

    def test_minimal_contract_requires_actual_mp4_muxer(self):
        payload = self.canonical()
        args = payload["minimal_helper_target"]["configure_args"]
        args[args.index("--enable-muxer=mp4")] = "--enable-muxer=mov"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_contract(root, payload)
            with self.assertRaisesRegex(
                MinimalFfmpegSourceContractError,
                "actual mp4 muxer",
            ):
                audit_source_contract(root)

    def test_minimal_contract_requires_derivative_validation_decoders(self):
        payload = self.canonical()
        args = payload["minimal_helper_target"]["configure_args"]
        index = next(i for i, arg in enumerate(args) if arg.startswith("--enable-decoder="))
        args[index] = args[index].replace(",h264,aac", "")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_contract(root, payload)
            with self.assertRaisesRegex(
                MinimalFfmpegSourceContractError,
                "H.264/AAC derivative validation decoders",
            ):
                audit_source_contract(root)

    def test_minimal_contract_requires_runtime_pipe_and_null_plumbing(self):
        payload = self.canonical()
        args = payload["minimal_helper_target"]["configure_args"]
        args[args.index("--enable-protocol=file,pipe")] = "--enable-protocol=file"
        args.remove("--enable-muxer=null")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_contract(root, payload)
            with self.assertRaisesRegex(
                MinimalFfmpegSourceContractError,
                "file/pipe I/O",
            ):
                audit_source_contract(root)

    def test_minimal_contract_rejects_third_party_enable_flags(self):
        payload = self.canonical()
        payload["minimal_helper_target"]["configure_args"].append("--enable-libx264")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_contract(root, payload)
            with self.assertRaisesRegex(
                MinimalFfmpegSourceContractError,
                "must not enable third-party libraries",
            ):
                audit_source_contract(root)

    def test_minimal_contract_rejects_missing_ea_decoder_possibility(self):
        payload = self.canonical()
        payload["minimal_helper_target"]["ea_demuxer_codec_superset"].remove("adpcm_ea_r3")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_contract(root, payload)
            with self.assertRaisesRegex(
                MinimalFfmpegSourceContractError,
                "EA decoder superset",
            ):
                audit_source_contract(root)

    def test_ready_requires_every_build_source_and_external_playback_proof(self):
        payload = self.canonical()
        payload["minimal_helper_target"]["production_migration_ready"] = True
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_contract(root, payload)
            with self.assertRaisesRegex(
                MinimalFfmpegSourceContractError,
                "cannot be production-ready",
            ):
                audit_source_contract(root)

    def test_verified_broad_candidate_cannot_be_relabelled_minimal(self):
        payload = self.canonical()
        payload["verified_broad_candidate"]["external_dependency_surface_minimal"] = True
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_contract(root, payload)
            with self.assertRaisesRegex(
                MinimalFfmpegSourceContractError,
                "must not be relabeled as minimal",
            ):
                audit_source_contract(root)


if __name__ == "__main__":
    unittest.main()
