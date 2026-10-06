"""Create a fail-closed receipt for the production Windows startup-FMV path.

The acceptance transaction now uses the same game-owned host path as a normal
Windows launch: canonical TGQ validation/conversion, WindowsWpfStartupMediaBackend,
OriginalGameTkHost parent-HWND binding, and the source-proven two-item order.

A passing receipt requires explicit human confirmation that both videos were
visible and audible, remained embedded in the FM2001 game window, and appeared
in source order. It does not promote unresolved native skip/fade timing or Gate
14 completion.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import sys
from typing import Callable

from original_game_host import run_original_game_ui
from original_startup_media import ORIGINAL_STARTUP_MEDIA_SEQUENCE
from startup_fmv_presentation import ORIGINAL_STARTUP_FMV_PRESENTATION
from startup_media_derivatives import VerifiedStartupMediaDerivative
from startup_media_runtime_cache import (
    RuntimeStartupMediaError,
    prepare_runtime_startup_media,
)
from startup_media_windows_backend import (
    WindowsWpfStartupMediaBackend,
    WindowsStartupMediaBackendError,
)


class Gate14WindowsStartupMediaAuditError(RuntimeError):
    pass


RECEIPT_SCHEMA_VERSION = 2
VISIBLE_AUDIBLE_CONFIRMATION_TOKEN = "YES-GAME-WINDOW"


def _require_external_windows_11(
    *,
    platform_system: str | None = None,
    platform_release: str | None = None,
    platform_version: str | None = None,
    github_actions: str | None = None,
    windows_product_type: int | None = None,
) -> dict:
    """Require an actual Windows 11 client workstation, never hosted/server CI."""
    system = platform.system() if platform_system is None else platform_system
    release = platform.release() if platform_release is None else platform_release
    version = platform.version() if platform_version is None else platform_version
    actions = (
        str(os.environ.get("GITHUB_ACTIONS", ""))
        if github_actions is None
        else str(github_actions)
    )
    if system != "Windows":
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance audit must run on Windows 11"
        )
    if actions.casefold() == "true":
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance evidence cannot be produced under GitHub Actions"
        )

    if windows_product_type is None:
        try:
            product_type = int(sys.getwindowsversion().product_type)
        except Exception as exc:
            raise Gate14WindowsStartupMediaAuditError(
                "unable to verify Windows workstation product type"
            ) from exc
    else:
        product_type = int(windows_product_type)
    if product_type != 1:
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance requires a Windows client workstation"
        )

    try:
        build_text = str(version).split(".")[-1]
        build = int(build_text)
    except (TypeError, ValueError) as exc:
        raise Gate14WindowsStartupMediaAuditError(
            "unable to parse Windows build number"
        ) from exc
    if build < 22000:
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance requires Windows 11 build 22000 or newer"
        )
    return {
        "platform_system": "Windows",
        "platform_release": str(release),
        "platform_version": str(version),
        "windows_build": build,
        "windows_product_type": product_type,
        "windows_11": True,
        "outside_github_actions": True,
    }


def _require_private_receipt(
    path: str | Path,
    *,
    repository_root: str | Path | None = None,
) -> Path:
    root = (
        Path(__file__).resolve().parent.parent
        if repository_root is None
        else Path(repository_root)
    ).resolve()
    target = Path(path).resolve()
    if target.is_relative_to(root):
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media acceptance receipt must remain outside Git"
        )
    if target.exists():
        raise Gate14WindowsStartupMediaAuditError(
            "Use a new startup-media receipt path; do not overwrite prior evidence"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _human_confirmation(
    confirmer: Callable[[str], str],
) -> bool:
    source_names = ", then ".join(
        Path(spec.source_path).name for spec in ORIGINAL_STARTUP_MEDIA_SEQUENCE
    )
    prompt = (
        "The production-host startup sequence has completed: "
        f"{source_names}.\n"
        "Confirm ALL of the following: both videos were visible, both had audible "
        "audio, they stayed embedded inside the FM2001 game-owned window rather "
        "than appearing as a separate player, the movie treatment remained "
        "centered without obvious aspect distortion, and they appeared in that "
        "order. Type "
        f"{VISIBLE_AUDIBLE_CONFIRMATION_TOKEN} exactly and press Enter. "
        "Any other response fails closed: "
    )
    try:
        response = confirmer(prompt)
    except Exception as exc:
        raise Gate14WindowsStartupMediaAuditError(
            f"human startup-media confirmation failed: {type(exc).__name__}: {exc}"
        ) from exc
    return response == VISIBLE_AUDIBLE_CONFIRMATION_TOKEN


def _validate_derivatives(derivatives: tuple[VerifiedStartupMediaDerivative, ...]) -> None:
    expected = tuple(ORIGINAL_STARTUP_MEDIA_SEQUENCE)
    if len(derivatives) != len(expected):
        raise Gate14WindowsStartupMediaAuditError(
            "runtime startup-media preparation did not return the complete source sequence"
        )
    for index, (derivative, spec) in enumerate(zip(derivatives, expected, strict=True)):
        if not isinstance(derivative, VerifiedStartupMediaDerivative):
            raise Gate14WindowsStartupMediaAuditError(
                "runtime startup-media preparation returned an unverified derivative"
            )
        if derivative.sequence != index or derivative.spec != spec:
            raise Gate14WindowsStartupMediaAuditError(
                "runtime startup-media derivative order or source identity drifted"
            )


def _validated_host_binding(host, player: WindowsWpfStartupMediaBackend) -> dict:
    binding_method = getattr(host, "startup_media_child_binding", None)
    if not callable(binding_method):
        raise Gate14WindowsStartupMediaAuditError(
            "production host did not expose startup-media child binding"
        )
    try:
        binding = dict(binding_method())
    except Exception as exc:
        raise Gate14WindowsStartupMediaAuditError(
            "production host startup-media child binding could not be read"
        ) from exc

    required = ("parent_hwnd", "x", "y", "width", "height")
    if tuple(binding.keys()) != required:
        raise Gate14WindowsStartupMediaAuditError(
            "production startup-media child binding schema drifted"
        )
    values = tuple(binding[key] for key in required)
    if any(type(value) is not int for value in values):
        raise Gate14WindowsStartupMediaAuditError(
            "production startup-media child binding must contain integers"
        )
    if (
        binding["parent_hwnd"] <= 0
        or binding["x"] < 0
        or binding["y"] < 0
        or binding["width"] <= 0
        or binding["height"] <= 0
    ):
        raise Gate14WindowsStartupMediaAuditError(
            "production startup-media child binding geometry is invalid"
        )

    if getattr(player, "_parent_hwnd", None) != binding["parent_hwnd"]:
        raise Gate14WindowsStartupMediaAuditError(
            "WPF startup backend was not bound to the production game HWND"
        )
    expected_rect = (
        binding["x"],
        binding["y"],
        binding["width"],
        binding["height"],
    )
    if getattr(player, "_presentation_rect", None) != expected_rect:
        raise Gate14WindowsStartupMediaAuditError(
            "WPF startup backend geometry differs from the production host binding"
        )
    return binding


def run_windows_startup_media_audit(
    game_dir: str | Path,
    application_root: str | Path,
    *,
    backend=None,
    confirmer: Callable[[str], str] = input,
    platform_system: str | None = None,
    platform_release: str | None = None,
    platform_version: str | None = None,
    github_actions: str | None = None,
    windows_product_type: int | None = None,
    preparer=None,
) -> dict:
    """Exercise the production host/WPF startup path and require human acceptance."""
    windows = _require_external_windows_11(
        platform_system=platform_system,
        platform_release=platform_release,
        platform_version=platform_version,
        github_actions=github_actions,
        windows_product_type=windows_product_type,
    )
    prepare = prepare_runtime_startup_media if preparer is None else preparer
    if not callable(prepare):
        raise Gate14WindowsStartupMediaAuditError(
            "startup-media preparer must be callable"
        )
    try:
        derivatives = tuple(prepare(game_dir, application_root))
    except (RuntimeStartupMediaError, OSError) as exc:
        raise Gate14WindowsStartupMediaAuditError(
            "runtime startup-media preparation failed"
        ) from exc
    _validate_derivatives(derivatives)

    player = (
        WindowsWpfStartupMediaBackend(platform_system="Windows")
        if backend is None
        else backend
    )
    if type(player) is not WindowsWpfStartupMediaBackend:
        raise Gate14WindowsStartupMediaAuditError(
            "real startup-media acceptance requires exact WindowsWpfStartupMediaBackend"
        )

    observed: dict[str, object] = {}

    def host_ready(host, _audio_binding) -> None:
        root = getattr(host, "root", None)
        if not callable(getattr(root, "after", None)) or not callable(
            getattr(root, "destroy", None)
        ):
            raise Gate14WindowsStartupMediaAuditError(
                "production Tk host must expose after() and destroy()"
            )
        try:
            observed["host_binding"] = _validated_host_binding(host, player)
            observed["host_ready_after_startup"] = True
        except Exception:
            try:
                root.destroy()
            except Exception:
                pass
            raise
        root.after(0, root.destroy)

    try:
        run_original_game_ui(
            game_dir,
            startup_media_backend=player,
            startup_media_derivatives=derivatives,
            host_ready_callback=host_ready,
        )
    except Gate14WindowsStartupMediaAuditError:
        raise
    except (WindowsStartupMediaBackendError, RuntimeStartupMediaError) as exc:
        raise Gate14WindowsStartupMediaAuditError(
            "real Windows production-host startup-media playback failed"
        ) from exc
    except Exception as exc:
        raise Gate14WindowsStartupMediaAuditError(
            f"production-host startup-media audit failed: {type(exc).__name__}: {exc}"
        ) from exc

    if observed.get("host_ready_after_startup") is not True:
        raise Gate14WindowsStartupMediaAuditError(
            "production host exited before startup media reached the host-ready boundary"
        )
    binding = observed.get("host_binding")
    if type(binding) is not dict:
        raise Gate14WindowsStartupMediaAuditError(
            "production host did not retain verified child-window binding evidence"
        )

    if not _human_confirmation(confirmer):
        raise Gate14WindowsStartupMediaAuditError(
            "game-owned visible and audible Windows startup media were not explicitly confirmed"
        )

    items = []
    for derivative in derivatives:
        items.append(
            {
                "sequence": derivative.sequence,
                "source_path": derivative.spec.source_path,
                "source_sha256": derivative.spec.source_sha256,
                "source_size_bytes": derivative.spec.size_bytes,
                "decoded_video_frames": derivative.spec.decoded_video_frames,
                "audio_sample_rate": derivative.spec.audio_sample_rate,
                "audio_channels": derivative.spec.audio_channels,
                "playback_flag_bit0": derivative.spec.playback_flag_bit0,
                "converted_filename": Path(derivative.path).name,
                "converted_sha256": derivative.converted_sha256,
                "converted_size_bytes": derivative.converted_size_bytes,
                "container": derivative.container,
                "video_codec": derivative.video_codec,
                "pixel_format": derivative.pixel_format,
                "audio_codec": derivative.audio_codec,
                "playback_completed": True,
            }
        )

    presentation = ORIGINAL_STARTUP_FMV_PRESENTATION
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "audit_kind": "gate14_windows_startup_media_acceptance",
        "passed": True,
        **windows,
        "playback_backend": "WindowsWpfStartupMediaBackend",
        "production_host_runner": "run_original_game_ui",
        "normal_application_host_path_invoked": True,
        "normal_app_cli_invoked": False,
        "startup_sequence": items,
        "source_order_preserved": True,
        "game_owned_child_window_verified": True,
        "backend_parent_binding_verified": True,
        "host_child_binding": binding,
        "source_presentation": {
            "coded_size": [presentation.coded_width, presentation.coded_height],
            "movie_size": [presentation.movie_width, presentation.movie_height],
            "ordinary_game_display_size": [
                presentation.game_display_width,
                presentation.game_display_height,
            ],
            "ordinary_movie_offset": [presentation.movie_x, presentation.movie_y],
            "horizontal_repeat": presentation.horizontal_repeat,
            "ffmpeg_filter": presentation.ffmpeg_filter,
        },
        "human_visibility_confirmation": True,
        "human_audibility_confirmation": True,
        "human_game_owned_window_confirmation": True,
        "startup_media_real_windows_verified": True,
        "default_runtime_components_replayed": True,
        "source_display_geometry_integrated": True,
        "exact_horizontal_repeat_integrated": True,
        "normal_application_launch_invoked": False,
        "skip_input_recovered": False,
        "transition_timing_recovered": False,
        "exact_display_treatment_recovered": False,
        "gate14_complete": False,
        "evidence_limit": (
            "This receipt proves the canonical startup derivatives completed through "
            "the production run_original_game_ui host, the exact WPF backend was "
            "bound to the game-owned child HWND, and a human confirmed both videos "
            "visible/audible in source order without a separate player window. It "
            "does not prove the top-level CLI wrapper, native skip input, exact "
            "fade/transition timing, every DirectDraw-era display detail, or Gate 14."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--application-root", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    output = _require_private_receipt(args.output_receipt)
    receipt = run_windows_startup_media_audit(
        args.game_dir,
        args.application_root,
    )
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "PASS: production-host Windows 11 startup-media path verified; "
        f"private receipt written to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
