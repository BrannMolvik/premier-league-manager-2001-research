"""Synchronous command backend for verified FM2001 startup derivatives.

This adapter deliberately does not choose a media framework or invent FM2001
input/fade/scaling semantics. It launches an explicitly configured player
process with the verified derivative path as the final argument and treats only
an exit code of zero as successful synchronous completion.

The configured player is responsible for the tiny backend contract: it must not
return success until playback of the supplied item has completed.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Callable, Sequence

from startup_media_derivatives import VerifiedStartupMediaDerivative


class StartupMediaCommandBackendError(ValueError):
    """The explicit startup-media player command is invalid."""


class SynchronousCommandStartupMediaBackend:
    """Invoke one explicitly configured media-player command per verified item."""

    def __init__(
        self,
        executable: str,
        arguments: Sequence[str] = (),
        *,
        runner: Callable[..., object] = subprocess.run,
    ):
        if not isinstance(executable, str) or not executable.strip():
            raise StartupMediaCommandBackendError(
                "Startup-media player executable must be non-empty"
            )
        args = tuple(arguments)
        if any(not isinstance(value, str) for value in args):
            raise StartupMediaCommandBackendError(
                "Startup-media player arguments must be strings"
            )
        if not callable(runner):
            raise StartupMediaCommandBackendError(
                "Startup-media command runner must be callable"
            )
        self.executable = executable
        self.arguments = args
        self._runner = runner

    def play(self, item: VerifiedStartupMediaDerivative) -> bool:
        if not isinstance(item, VerifiedStartupMediaDerivative):
            return False
        completed = self._runner(
            (
                self.executable,
                *self.arguments,
                str(Path(item.path)),
            ),
            check=False,
        )
        return getattr(completed, "returncode", None) == 0
