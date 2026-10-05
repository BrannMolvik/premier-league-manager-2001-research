"""Low-overhead runtime timing/exception trace for hands-on Windows playtests."""

from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
import sys
import traceback

TRACE_PREFIX = "[FM2001 runtime]"


@contextmanager
def timed_stage(stage: str):
    """Emit flushed BEGIN/END/FAIL markers without changing runtime semantics."""
    name = str(stage)
    started = perf_counter()
    print(f"{TRACE_PREFIX} BEGIN {name}", file=sys.stderr, flush=True)
    try:
        yield
    except Exception as exc:
        elapsed = perf_counter() - started
        print(
            f"{TRACE_PREFIX} FAIL {name} seconds={elapsed:.3f} "
            f"error={type(exc).__name__}: {exc}",
            file=sys.stderr,
            flush=True,
        )
        traceback.print_exc(file=sys.stderr)
        raise
    else:
        elapsed = perf_counter() - started
        print(
            f"{TRACE_PREFIX} END {name} seconds={elapsed:.3f}",
            file=sys.stderr,
            flush=True,
        )
