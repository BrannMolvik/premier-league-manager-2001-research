"""Fail-closed runtime orchestration for verified FM2001 startup media.

This module is deliberately narrower than a Windows media player. It accepts
only the immutable derivative records produced by startup_media_derivatives.py,
requires the source-proven startup sequence, and invokes a caller-supplied
synchronous playback backend one item at a time.

The original wrapper's bit-0 flag is preserved only as neutral metadata. This
module does not interpret it as a skip flag, does not define input handling,
does not invent fades/transitions, and does not choose scaling/interlace
behavior. Those remain separate source-evidence and platform-integration tasks.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

from original_startup_media import (
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    OriginalStartupMediaSpec,
)
from startup_media_derivatives import (
    VerifiedStartupMediaDerivative,
    load_verified_startup_media_derivatives,
)


class StartupMediaPlaybackError(RuntimeError):
    """Verified startup media cannot be played without violating its contract."""


class StartupMediaPlaybackBackend(Protocol):
    """Minimal synchronous platform-player boundary."""

    def play(self, item: VerifiedStartupMediaDerivative) -> bool:
        """Return exactly True only after this item completes."""


@dataclass(frozen=True)
class StartupMediaPlaybackStep:
    sequence: int
    source_path: str
    derivative_path: Path
    playback_flag_bit0: bool
    completed: bool


@dataclass(frozen=True)
class StartupMediaPlaybackSummary:
    steps: tuple[StartupMediaPlaybackStep, ...]
    source_order_preserved: bool
    playback_flag_semantics_recovered: bool
    skip_input_recovered: bool
    transition_timing_recovered: bool
    gate14_complete: bool


def _require_verified_sequence(
    derivatives: Iterable[VerifiedStartupMediaDerivative],
    *,
    specs: Iterable[OriginalStartupMediaSpec],
) -> tuple[VerifiedStartupMediaDerivative, ...]:
    items = tuple(derivatives)
    expected = tuple(specs)
    if not expected:
        raise StartupMediaPlaybackError(
            "Startup-media playback sequence cannot have an empty source contract"
        )
    if len(items) != len(expected):
        raise StartupMediaPlaybackError(
            "Verified startup-media count differs from the source-proven sequence"
        )

    seen_paths: set[Path] = set()
    for sequence, (item, spec) in enumerate(zip(items, expected, strict=True)):
        if not isinstance(item, VerifiedStartupMediaDerivative):
            raise StartupMediaPlaybackError(
                f"Startup-media item {sequence} is not a verified derivative"
            )
        if item.sequence != sequence:
            raise StartupMediaPlaybackError(
                f"Startup-media sequence index {item.sequence} differs from {sequence}"
            )
        if item.spec != spec:
            raise StartupMediaPlaybackError(
                f"Startup-media source identity/order differs at sequence {sequence}"
            )
        path = Path(item.path)
        if path in seen_paths:
            raise StartupMediaPlaybackError(
                "Startup-media playback sequence reuses one derivative path"
            )
        seen_paths.add(path)
    return items


def play_verified_startup_sequence(
    derivatives: Iterable[VerifiedStartupMediaDerivative],
    backend: StartupMediaPlaybackBackend,
    *,
    specs: Iterable[OriginalStartupMediaSpec] = ORIGINAL_STARTUP_MEDIA_SEQUENCE,
) -> StartupMediaPlaybackSummary:
    """Play exact verified derivatives synchronously in the proven source order.

    A failed item aborts before any later media item is invoked. The differing
    original bit-0 values are carried in the result but never supplied to the
    backend as a user-facing behavior switch.
    """
    if backend is None or not callable(getattr(backend, "play", None)):
        raise StartupMediaPlaybackError(
            "Startup-media playback requires a backend with a play() method"
        )

    items = _require_verified_sequence(derivatives, specs=tuple(specs))
    completed: list[StartupMediaPlaybackStep] = []
    for item in items:
        try:
            result = backend.play(item)
        except Exception as exc:
            raise StartupMediaPlaybackError(
                f"Startup-media backend failed at sequence {item.sequence} "
                f"({item.spec.source_path}): {type(exc).__name__}: {exc}"
            ) from exc
        if result is not True:
            raise StartupMediaPlaybackError(
                f"Startup-media backend did not complete sequence {item.sequence} "
                f"({item.spec.source_path})"
            )
        completed.append(
            StartupMediaPlaybackStep(
                sequence=item.sequence,
                source_path=item.spec.source_path,
                derivative_path=Path(item.path),
                playback_flag_bit0=item.spec.playback_flag_bit0,
                completed=True,
            )
        )

    return StartupMediaPlaybackSummary(
        steps=tuple(completed),
        source_order_preserved=True,
        playback_flag_semantics_recovered=False,
        skip_input_recovered=False,
        transition_timing_recovered=False,
        gate14_complete=False,
    )


def load_and_play_verified_startup_sequence(
    *,
    receipt_path: Path,
    repo_root: Path,
    backend: StartupMediaPlaybackBackend,
    specs: Iterable[OriginalStartupMediaSpec] = ORIGINAL_STARTUP_MEDIA_SEQUENCE,
) -> StartupMediaPlaybackSummary:
    """Reverify the private receipt/files immediately before ordered playback."""
    expected = tuple(specs)
    derivatives = load_verified_startup_media_derivatives(
        receipt_path=Path(receipt_path),
        repo_root=Path(repo_root),
        specs=expected,
    )
    return play_verified_startup_sequence(
        derivatives,
        backend,
        specs=expected,
    )
