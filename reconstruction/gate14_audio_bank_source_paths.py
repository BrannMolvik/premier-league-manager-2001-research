"""Exact source-path contract for the four source-owned Gate-14 BNK banks."""
from __future__ import annotations

from pathlib import Path

from gate13_source_inventory import normalize_member
from gate14_audio_bank_ownership import BANKS


AUDIO_BANK_EXACT_PATH_FILE = Path("research/gate14_audio_bank_exact_paths.txt")
AUDIO_BANK_SOURCE_DIRECTORY = "DATA/AUDIO/SFXS"
CANONICAL_AUDIO_SOURCE_ARCHIVE_SIZE = 511_121_336
CANONICAL_AUDIO_SOURCE_ARCHIVE_SHA256 = (
    "677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4"
)


class Gate14AudioBankSourcePathError(ValueError):
    pass


def expected_audio_bank_source_paths() -> tuple[str, ...]:
    """Derive exact disc-relative paths from source-proven bank ownership."""
    return tuple(
        normalize_member(f"{AUDIO_BANK_SOURCE_DIRECTORY}/{bank.filename}")
        for bank in BANKS
    )


def validate_audio_bank_exact_path_contract(
    repo_root: str | Path,
) -> tuple[str, ...]:
    """Require the checked-in path file to equal the source-owned bank set."""
    root = Path(repo_root)
    contract = root / AUDIO_BANK_EXACT_PATH_FILE
    try:
        lines = contract.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise Gate14AudioBankSourcePathError(
            "audio-bank exact-path contract is not readable"
        ) from exc

    observed = tuple(
        normalize_member(line.strip())
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    )
    expected = expected_audio_bank_source_paths()
    if observed != expected:
        raise Gate14AudioBankSourcePathError(
            "audio-bank exact-path contract differs from source-owned bank order"
        )
    if len(set(path.casefold() for path in observed)) != len(observed):
        raise Gate14AudioBankSourcePathError(
            "audio-bank exact-path contract contains duplicate paths"
        )
    return observed
