"""Synthetic tests for the fail-closed Gate-17 release evidence contract."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gate17_full_scope_catalog import (
    OriginalPlayableScope,
    PlayableCountryScope,
    PlayableLeagueScope,
)

from gate17_release_readiness import (
    ReleaseReadinessError,
    build_full_scope_receipt_binding,
    parse_release_evidence,
    require_external_windows_11_workstation,
    require_path_outside_repo,
    validate_external_receipts,
    validate_full_original_scope_binding,
    validate_limitations_document,
    validate_release_archive,
    validate_roadmap_prerequisites,
)


COMMIT = "a" * 40
RELEASE_VERSION = "test-1"
RELEASE_ARCHIVE_BYTES = b"release bytes"
RELEASE_ARCHIVE_SHA256 = sha256(RELEASE_ARCHIVE_BYTES).hexdigest()


def write_receipt(path, **flags):
    payload = {
        "passed": True,
        "repository_commit": COMMIT,
        "release_version": RELEASE_VERSION,
        "release_archive_sha256": RELEASE_ARCHIVE_SHA256,
        "windows_11": True,
        "windows_build": 26200,
        "windows_product_type": 1,
        **flags,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return sha256(path.read_bytes()).hexdigest()


def synthetic_full_scope():
    return OriginalPlayableScope(
        countries=(
            PlayableCountryScope(
                country_id=26,
                name="England",
                source_root_league_count=1,
                visible_league_capacity=15,
                leagues=(
                    PlayableLeagueScope(
                        competition_id=100,
                        name="England League",
                        source_club_count=2,
                        selectable_club_ids=(1, 2),
                        selectable_club_names=("Alpha", "Beta"),
                    ),
                ),
            ),
            PlayableCountryScope(
                country_id=66,
                name="Scotland",
                source_root_league_count=1,
                visible_league_capacity=14,
                leagues=(
                    PlayableLeagueScope(
                        competition_id=200,
                        name="Scotland League",
                        source_club_count=2,
                        selectable_club_ids=(3, 4),
                        selectable_club_names=("Gamma", "Delta"),
                    ),
                ),
            ),
        )
    )


def write_roadmap(path, *, open_gate=None, omit_gate=None):
    lines = ["# Roadmap", ""]
    for gate in range(1, 18):
        if gate == omit_gate:
            continue
        lines.append(f"## Gate {gate} - Synthetic")
        lines.append("")
        marker = " " if gate == open_gate else "x"
        lines.append(f"- [{marker}] criterion {gate}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


class Gate17ReleaseReadinessTests(unittest.TestCase):
    def test_external_windows_guard_rejects_github_actions_and_server(self):
        base = {"platform": "Windows-11", "windows_build": 26200}

        with (
            patch("gate17_release_readiness.require_windows_11", return_value=base),
            patch.dict(
                "gate17_release_readiness.os.environ",
                {"GITHUB_ACTIONS": "true"},
                clear=False,
            ),
        ):
            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "GitHub Actions",
            ):
                require_external_windows_11_workstation()

        with (
            patch("gate17_release_readiness.require_windows_11", return_value=base),
            patch.dict("gate17_release_readiness.os.environ", {}, clear=True),
            patch(
                "gate17_release_readiness.sys.getwindowsversion",
                return_value=SimpleNamespace(product_type=3),
                create=True,
            ),
        ):
            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "client workstation",
            ):
                require_external_windows_11_workstation()

        with (
            patch("gate17_release_readiness.require_windows_11", return_value=base),
            patch.dict("gate17_release_readiness.os.environ", {}, clear=True),
            patch(
                "gate17_release_readiness.sys.getwindowsversion",
                return_value=SimpleNamespace(product_type=1),
                create=True,
            ),
        ):
            result = require_external_windows_11_workstation()

        self.assertEqual(result["windows_product_type"], 1)
        self.assertEqual(result["windows_build"], 26200)

    def fixture(self, temp):
        temp = Path(temp)
        repo = temp / "repo"
        repo.mkdir()
        limitations = repo / "research/RELEASE_LIMITATIONS.md"
        limitations.parent.mkdir(parents=True)
        limitations.write_text(
            "# Release limitations\\n\\n"
            + "Known accepted limitation. " * 20,
            encoding="utf-8",
        )

        private = temp / "private"
        receipts = {}
        receipt_flags = {
            "clean_windows_install": {
                "windows_11": True,
                "outside_development_environment": True,
            },
            "new_game_management_loop": {
                "new_game": True,
                "management_loop": True,
            },
            "season_progression": {
                "season_progression": True,
            },
            "save_reload": {
                "save_reload": True,
            },
            "full_original_scope": {
                "full_original_scope": True,
                "all_original_playable_leagues": True,
                "all_original_playable_countries": True,
                "human_career_flow": True,
                "competition_progression": True,
                "original_management_gameplay_subsystems": True,
                "multi_human_management": True,
                "simultaneous_human_users_verified": 6,
            },
        }
        for name, flags in receipt_flags.items():
            path = private / f"{name}.json"
            receipts[name] = {
                "path": str(path),
                "sha256": write_receipt(path, **flags),
            }

        archive = private / "fm2001-port.zip"
        archive.write_bytes(RELEASE_ARCHIVE_BYTES)
        evidence = {
            "schema_version": 2,
            "release_version": RELEASE_VERSION,
            "repository_commit": COMMIT,
            "limitations_path": "research/RELEASE_LIMITATIONS.md",
            "external_receipts": receipts,
            "archive": {
                "sha256": RELEASE_ARCHIVE_SHA256,
                "size_bytes": archive.stat().st_size,
            },
        }
        return repo, private, archive, evidence

    def test_roadmap_prerequisites_allow_open_gate17_only(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            write_roadmap(repo / "ROADMAP.md", open_gate=17)

            result = validate_roadmap_prerequisites(repo)

            self.assertTrue(result["all_prerequisites_complete"])
            self.assertEqual(result["required_gates"], list(range(1, 17)))
            self.assertNotIn("17", result["criteria"])

    def test_roadmap_prerequisites_reject_any_open_gate_1_through_16(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            write_roadmap(repo / "ROADMAP.md", open_gate=13)

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                r"Gate 13 \(1 unchecked\)",
            ):
                validate_roadmap_prerequisites(repo)

    def test_roadmap_prerequisites_reject_missing_gate_section(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            write_roadmap(repo / "ROADMAP.md", omit_gate=14)

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "missing prerequisite gate sections: \\[14\\]",
            ):
                validate_roadmap_prerequisites(repo)

    def test_complete_external_evidence_and_archive_validate(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, archive, raw = self.fixture(temp)
            evidence = parse_release_evidence(raw)
            checked = validate_external_receipts(evidence, repo)
            self.assertEqual(set(checked), set(raw["external_receipts"]))
            archive_check = validate_release_archive(
                archive, evidence.archive, repo
            )
            self.assertEqual(archive_check["size_bytes"], len(RELEASE_ARCHIVE_BYTES))
            limits = validate_limitations_document(
                repo, evidence.limitations_path
            )
            self.assertGreater(limits["characters"], 200)

    def test_missing_or_false_windows_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            evidence = parse_release_evidence(raw)
            descriptor = evidence.external_receipts["clean_windows_install"]
            path = Path(descriptor.path)
            write_receipt(
                path,
                windows_11=True,
                outside_development_environment=False,
            )
            mutable = dict(raw)
            mutable["external_receipts"] = dict(raw["external_receipts"])
            mutable["external_receipts"]["clean_windows_install"] = {
                "path": str(path),
                "sha256": sha256(path.read_bytes()).hexdigest(),
            }
            evidence = parse_release_evidence(mutable)
            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "outside_development_environment",
            ):
                validate_external_receipts(evidence, repo)

    def test_external_receipt_host_metadata_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            name = "save_reload"
            path = Path(raw["external_receipts"][name]["path"])

            cases = (
                ("windows_11", False, "does not prove Windows 11"),
                ("windows_build", 21999, "older than Windows 11"),
                ("windows_product_type", 3, "client workstation"),
            )
            for field, value, message in cases:
                with self.subTest(field=field):
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    payload[field] = value
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    raw["external_receipts"][name]["sha256"] = sha256(
                        path.read_bytes()
                    ).hexdigest()
                    with self.assertRaisesRegex(ReleaseReadinessError, message):
                        validate_external_receipts(
                            parse_release_evidence(raw),
                            repo,
                        )
                    # Restore canonical synthetic evidence before next case.
                    raw["external_receipts"][name]["sha256"] = write_receipt(
                        path,
                        save_reload=True,
                    )

    def test_external_receipts_must_be_five_distinct_files(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            shared = raw["external_receipts"]["clean_windows_install"]
            raw["external_receipts"]["new_game_management_loop"] = dict(shared)
            evidence = parse_release_evidence(raw)

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "reuses the same evidence file",
            ):
                validate_external_receipts(evidence, repo)

    def test_full_scope_receipt_requires_source_proven_six_user_capability(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            name = "full_original_scope"
            path = Path(raw["external_receipts"][name]["path"])

            cases = (
                ("multi_human_management", False, "multi_human_management"),
                (
                    "simultaneous_human_users_verified",
                    5,
                    "simultaneous_human_users_verified",
                ),
                (
                    "simultaneous_human_users_verified",
                    True,
                    "simultaneous_human_users_verified",
                ),
            )
            for field, value, message in cases:
                with self.subTest(field=field, value=value):
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    payload[field] = value
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    raw["external_receipts"][name]["sha256"] = sha256(
                        path.read_bytes()
                    ).hexdigest()
                    with self.assertRaisesRegex(
                        ReleaseReadinessError,
                        message,
                    ):
                        validate_external_receipts(
                            parse_release_evidence(raw),
                            repo,
                        )
                    raw["external_receipts"][name]["sha256"] = write_receipt(
                        path,
                        full_original_scope=True,
                        all_original_playable_leagues=True,
                        all_original_playable_countries=True,
                        human_career_flow=True,
                        competition_progression=True,
                        original_management_gameplay_subsystems=True,
                        multi_human_management=True,
                        simultaneous_human_users_verified=6,
                    )

    def test_full_original_scope_receipt_cannot_be_replaced_by_premier_smoke(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            name = "full_original_scope"
            path = Path(raw["external_receipts"][name]["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["all_original_playable_countries"] = False
            path.write_text(json.dumps(payload), encoding="utf-8")
            raw["external_receipts"][name]["sha256"] = sha256(
                path.read_bytes()
            ).hexdigest()

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "all_original_playable_countries",
            ):
                validate_external_receipts(parse_release_evidence(raw), repo)

    def test_full_scope_binding_is_exact_catalog_identity(self):
        scope = synthetic_full_scope()
        binding = build_full_scope_receipt_binding(scope)

        self.assertEqual(binding["scope_catalog_sha256"], scope.catalog_sha256)
        self.assertEqual(binding["scope_country_count"], 2)
        self.assertEqual(binding["scope_entry_count"], 2)
        self.assertEqual(binding["scope_selectable_club_row_count"], 4)
        self.assertEqual(binding["scope_ids"], ("26:100", "66:200"))

    def test_full_scope_receipt_is_bound_to_canonical_catalog(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            scope = synthetic_full_scope()
            binding = build_full_scope_receipt_binding(scope)
            name = "full_original_scope"
            path = Path(raw["external_receipts"][name]["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload.update(
                {
                    "scope_catalog_sha256": binding["scope_catalog_sha256"],
                    "scope_country_count": binding["scope_country_count"],
                    "scope_entry_count": binding["scope_entry_count"],
                    "scope_selectable_club_row_count": binding[
                        "scope_selectable_club_row_count"
                    ],
                    "verified_scope_entry_count": binding["scope_entry_count"],
                    "verified_scope_ids": list(binding["scope_ids"]),
                    "missing_scope_ids": [],
                    "failed_scope_ids": [],
                }
            )
            path.write_text(json.dumps(payload), encoding="utf-8")
            raw["external_receipts"][name]["sha256"] = sha256(
                path.read_bytes()
            ).hexdigest()
            evidence = parse_release_evidence(raw)

            with patch(
                "gate17_release_readiness.load_canonical_original_playable_scope",
                return_value=scope,
            ):
                result = validate_full_original_scope_binding(
                    evidence,
                    repo,
                    Path(temp) / "canonical-game",
                )

            self.assertEqual(result["scope_catalog_sha256"], scope.catalog_sha256)
            self.assertEqual(result["verified_scope_ids"], ["26:100", "66:200"])

            cases = (
                (
                    "scope_catalog_sha256",
                    "0" * 64,
                    "scope_catalog_sha256",
                ),
                (
                    "verified_scope_ids",
                    ["66:200", "26:100"],
                    "verified_scope_ids",
                ),
                (
                    "missing_scope_ids",
                    ["26:100"],
                    "missing_scope_ids",
                ),
                (
                    "scope_entry_count",
                    True,
                    "scope_entry_count",
                ),
            )
            for field, bad_value, message in cases:
                with self.subTest(field=field):
                    changed = dict(payload)
                    changed[field] = bad_value
                    path.write_text(json.dumps(changed), encoding="utf-8")
                    raw["external_receipts"][name]["sha256"] = sha256(
                        path.read_bytes()
                    ).hexdigest()
                    evidence = parse_release_evidence(raw)
                    with patch(
                        "gate17_release_readiness.load_canonical_original_playable_scope",
                        return_value=scope,
                    ):
                        with self.assertRaisesRegex(
                            ReleaseReadinessError,
                            message,
                        ):
                            validate_full_original_scope_binding(
                                evidence,
                                repo,
                                Path(temp) / "canonical-game",
                            )

    def test_receipt_for_another_release_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            name = "season_progression"
            path = Path(raw["external_receipts"][name]["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["release_version"] = "other-release"
            path.write_text(json.dumps(payload), encoding="utf-8")
            raw["external_receipts"][name]["sha256"] = sha256(
                path.read_bytes()
            ).hexdigest()

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "different release version",
            ):
                validate_external_receipts(parse_release_evidence(raw), repo)

    def test_receipt_for_another_release_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            name = "save_reload"
            path = Path(raw["external_receipts"][name]["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["release_archive_sha256"] = "b" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")
            raw["external_receipts"][name]["sha256"] = sha256(
                path.read_bytes()
            ).hexdigest()

            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "different release archive",
            ):
                validate_external_receipts(parse_release_evidence(raw), repo)

    def test_receipt_for_another_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            name = "save_reload"
            path = Path(raw["external_receipts"][name]["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["repository_commit"] = "b" * 40
            path.write_text(json.dumps(payload), encoding="utf-8")
            raw["external_receipts"][name]["sha256"] = sha256(
                path.read_bytes()
            ).hexdigest()
            evidence = parse_release_evidence(raw)
            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "different repository commit",
            ):
                validate_external_receipts(evidence, repo)

    def test_release_archive_and_receipts_must_stay_outside_git(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, _raw = self.fixture(temp)
            inside = repo / "release.zip"
            inside.write_bytes(b"x")
            with self.assertRaisesRegex(
                ReleaseReadinessError, "outside the Git repository"
            ):
                require_path_outside_repo(inside, repo, label="release archive")

    def test_pre_release_limitations_document_cannot_pass_final_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _private, _archive, raw = self.fixture(temp)
            path = repo / raw["limitations_path"]
            path.write_text(
                "# Release limitations\\n\\nPRE-RELEASE working list. "
                + "Still pending. " * 30,
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ReleaseReadinessError, "pre-release"):
                validate_limitations_document(repo, raw["limitations_path"])

    def test_schema_one_evidence_is_rejected_as_stale_after_full_scope_upgrade(self):
        with tempfile.TemporaryDirectory() as temp:
            _repo, _private, _archive, raw = self.fixture(temp)
            raw["schema_version"] = 1
            with self.assertRaisesRegex(
                ReleaseReadinessError,
                "schema_version must be 2",
            ):
                parse_release_evidence(raw)

    def test_evidence_schema_requires_exact_receipt_set_and_archive_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            _repo, _private, _archive, raw = self.fixture(temp)
            raw["external_receipts"].pop("save_reload")
            with self.assertRaisesRegex(
                ReleaseReadinessError, "receipt set mismatch"
            ):
                parse_release_evidence(raw)


if __name__ == "__main__":
    unittest.main()
