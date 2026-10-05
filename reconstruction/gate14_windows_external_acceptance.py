"""Transactional coordinator for the two external Gate-14 Windows acceptances.

The startup-media and bound first-screen audio audits remain independent evidence
transactions. This coordinator runs both existing audits first, validates their
narrow receipt contracts, and only then writes a fresh private bundle directory
outside Git. It does not broaden either receipt's semantic claims.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import Callable

from gate14_windows_bound_first_screen_audio_audit import (
    run_windows_bound_first_screen_audio_audit,
)
from gate14_windows_startup_media_audit import run_windows_startup_media_audit


class Gate14WindowsAcceptanceCoordinatorError(RuntimeError):
    pass


BUNDLE_SCHEMA_VERSION = 1
STARTUP_RECEIPT_FILENAME = "startup_media.json"
BOUND_AUDIO_RECEIPT_FILENAME = "bound_first_screen_audio.json"
BUNDLE_MANIFEST_FILENAME = "gate14_external_acceptance_bundle.json"
_PLATFORM_FIELDS = (
    "platform_system",
    "platform_release",
    "platform_version",
    "windows_build",
    "windows_product_type",
    "windows_11",
    "outside_github_actions",
)


def _require_bool(receipt: dict, key: str, expected: bool, *, label: str) -> None:
    if receipt.get(key) is not expected:
        raise Gate14WindowsAcceptanceCoordinatorError(
            f"{label} receipt requires {key}={str(expected).lower()}"
        )


def _validate_startup_receipt(receipt: object) -> dict:
    if type(receipt) is not dict:
        raise Gate14WindowsAcceptanceCoordinatorError(
            "startup-media audit must return an exact receipt object"
        )
    if receipt.get("schema_version") != 1:
        raise Gate14WindowsAcceptanceCoordinatorError(
            "startup-media receipt schema drifted"
        )
    if receipt.get("audit_kind") != "gate14_windows_startup_media_acceptance":
        raise Gate14WindowsAcceptanceCoordinatorError(
            "unexpected startup-media receipt audit kind"
        )
    for key, expected in (
        ("passed", True),
        ("windows_11", True),
        ("outside_github_actions", True),
        ("source_order_preserved", True),
        ("human_visibility_confirmation", True),
        ("human_audibility_confirmation", True),
        ("startup_media_real_windows_verified", True),
        ("default_runtime_components_replayed", True),
        ("gate14_complete", False),
    ):
        _require_bool(receipt, key, expected, label="startup-media")
    return receipt


def _validate_bound_audio_receipt(receipt: object) -> dict:
    if type(receipt) is not dict:
        raise Gate14WindowsAcceptanceCoordinatorError(
            "bound-audio audit must return an exact receipt object"
        )
    if receipt.get("schema_version") != 1:
        raise Gate14WindowsAcceptanceCoordinatorError(
            "bound-audio receipt schema drifted"
        )
    if receipt.get("audit_kind") != (
        "gate14_windows_bound_first_screen_audio_acceptance"
    ):
        raise Gate14WindowsAcceptanceCoordinatorError(
            "unexpected bound-audio receipt audit kind"
        )
    for key, expected in (
        ("passed", True),
        ("windows_11", True),
        ("outside_github_actions", True),
        ("normal_application_host_path_invoked", True),
        ("human_audibility_confirmation", True),
        ("bound_application_press_audio_verified", True),
        ("audible_windows_verified", True),
        ("first_screen_press_binding_source_recovered", True),
        ("broad_audio_event_binding_recovered", False),
        ("sample_meaning_recovered", False),
        ("hover_audio_integrated", False),
        ("login_menu_audio_integrated", False),
        ("gate14_complete", False),
    ):
        _require_bool(receipt, key, expected, label="bound-audio")
    return receipt


def _validate_same_windows_client(startup: dict, bound_audio: dict) -> dict:
    platform_record: dict[str, object] = {}
    for key in _PLATFORM_FIELDS:
        left = startup.get(key)
        right = bound_audio.get(key)
        if left != right:
            raise Gate14WindowsAcceptanceCoordinatorError(
                f"child receipts disagree on Windows client field {key}"
            )
        platform_record[key] = left
    if platform_record["platform_system"] != "Windows":
        raise Gate14WindowsAcceptanceCoordinatorError(
            "acceptance bundle requires Windows child receipts"
        )
    return platform_record


def build_external_acceptance_bundle(
    startup_receipt: object,
    bound_audio_receipt: object,
) -> dict:
    """Validate two independent receipts and return a narrow aggregate record."""
    startup = _validate_startup_receipt(startup_receipt)
    bound_audio = _validate_bound_audio_receipt(bound_audio_receipt)
    windows = _validate_same_windows_client(startup, bound_audio)
    return {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "audit_kind": "gate14_windows_external_acceptance_bundle",
        "passed": True,
        **windows,
        "startup_media_real_windows_verified": True,
        "first_screen_press_audio_real_windows_verified": True,
        "broad_audio_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "hover_audio_integrated": False,
        "login_menu_audio_integrated": False,
        "source_fastview_navigation_trigger_recovered": False,
        "recognizable_original_match_workflow_verified": False,
        "gate14_complete": False,
        "evidence_limit": (
            "This bundle joins two distinct external Windows 11 acceptance "
            "receipts only. It does not broaden the bounded first-screen audio "
            "proof into application-wide AudioHooks semantics or login/menu "
            "integration, and it does not prove complete FastView/3D match "
            "presentation or Gate 14 completion."
        ),
    }


def run_windows_external_acceptance(
    game_dir: str | Path,
    application_root: str | Path,
    *,
    source_root: str | Path | None = None,
    startup_runner: Callable[..., dict] = run_windows_startup_media_audit,
    bound_audio_runner: Callable[..., dict] = run_windows_bound_first_screen_audio_audit,
) -> tuple[dict, dict, dict]:
    """Run both real-Windows audits before any bundle files are written."""
    startup_receipt = startup_runner(game_dir, application_root)
    bound_audio_receipt = bound_audio_runner(game_dir, source_root=source_root)
    bundle = build_external_acceptance_bundle(
        startup_receipt,
        bound_audio_receipt,
    )
    return startup_receipt, bound_audio_receipt, bundle


def _require_private_output_dir(
    output_dir: str | Path,
    *,
    repository_root: str | Path | None = None,
) -> Path:
    root = (
        Path(__file__).resolve().parent.parent
        if repository_root is None
        else Path(repository_root)
    ).resolve()
    target = Path(output_dir).resolve()
    if target == root or target.is_relative_to(root):
        raise Gate14WindowsAcceptanceCoordinatorError(
            "Gate-14 external acceptance bundle must remain outside Git"
        )
    if target.exists():
        raise Gate14WindowsAcceptanceCoordinatorError(
            "Use a new external acceptance bundle directory; do not overwrite evidence"
        )
    return target


def _receipt_bytes(receipt: dict) -> bytes:
    return (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_external_acceptance_bundle(
    output_dir: str | Path,
    startup_receipt: object,
    bound_audio_receipt: object,
    *,
    repository_root: str | Path | None = None,
) -> dict:
    """Write both child receipts and a hash-bound manifest transactionally."""
    target = _require_private_output_dir(
        output_dir,
        repository_root=repository_root,
    )
    startup = _validate_startup_receipt(startup_receipt)
    bound_audio = _validate_bound_audio_receipt(bound_audio_receipt)
    manifest = build_external_acceptance_bundle(startup, bound_audio)

    startup_bytes = _receipt_bytes(startup)
    bound_audio_bytes = _receipt_bytes(bound_audio)
    manifest = {
        **manifest,
        "child_receipts": [
            {
                "filename": STARTUP_RECEIPT_FILENAME,
                "audit_kind": startup["audit_kind"],
                "sha256": sha256(startup_bytes).hexdigest(),
            },
            {
                "filename": BOUND_AUDIO_RECEIPT_FILENAME,
                "audit_kind": bound_audio["audit_kind"],
                "sha256": sha256(bound_audio_bytes).hexdigest(),
            },
        ],
    }
    manifest_bytes = _receipt_bytes(manifest)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    try:
        (target / STARTUP_RECEIPT_FILENAME).write_bytes(startup_bytes)
        (target / BOUND_AUDIO_RECEIPT_FILENAME).write_bytes(bound_audio_bytes)
        (target / BUNDLE_MANIFEST_FILENAME).write_bytes(manifest_bytes)
    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--application-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    startup, bound_audio, _bundle = run_windows_external_acceptance(
        args.game_dir,
        args.application_root,
        source_root=args.source_root,
    )
    manifest = write_external_acceptance_bundle(
        args.output_dir,
        startup,
        bound_audio,
    )
    print(
        "PASS: both distinct Gate-14 external Windows acceptances passed; "
        f"private bundle written to {args.output_dir.resolve()}"
    )
    print(
        "Gate 14 remains open: broad audio semantics/integration and "
        "recognizable original match presentation are still unresolved."
    )
    if manifest.get("gate14_complete") is not False:
        raise Gate14WindowsAcceptanceCoordinatorError(
            "bundle manifest illegally promoted Gate 14 completion"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
