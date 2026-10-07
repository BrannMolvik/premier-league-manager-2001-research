"""Application-owned management art; native lookup 0x5D3490/0x5D3560.

The source-closed native lookup attempts the club seasonal image, the club
unsuffixed image, the fan-base seasonal generic, then the static generic.
Runtime selection mirrors that exact order over provenance-staged originals;
it never invents replacement pixels when a source-backed candidate is absent.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from gate13_ea444_staged_rasters import decode_staged_or_original as decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable

MONTH_VARIANTS = (2, 2, 3, 3, 0, 0, 0, 0, 1, 1, 1, 2)
TEAM_ROOT = 'FM2001_Art/Generic/Team_Backgrounds'
HEADER_ROOT = 'FM2001_Art/Generic/Background_buttons'
ASSET_HASHES = json.loads(Path(__file__).with_name(
    'original_management_background_assets.json').read_text(encoding='utf-8'))


class ManagementBackgroundError(ValueError):
    pass


def native_art_component(value: str) -> str:
    """Exact CP1252 byte translation from 0x5EFB40, not generic slugifying."""
    if not value or any(c in value for c in ('/', '\\', '\x00')):
        raise ManagementBackgroundError('Missing/unsafe original art component')
    raw = value.encode('cp1252', errors='strict')
    translation = bytes.maketrans(b" .'\xdc\xfc\xd6\xf6\xc2\xe2", b'___UuOoAa')
    return raw.translate(translation).decode('cp1252')


def background_candidates(directory: str, basename: str, month: int,
                          fan_base: int) -> tuple[str, ...]:
    if type(month) is not int or not 1 <= month <= 12:
        raise ManagementBackgroundError('Native date month must be 1..12')
    if type(fan_base) is not int or not 0 <= fan_base <= 0xFFFFFFFF:
        raise ManagementBackgroundError('Missing original fan-base index')
    directory, basename = map(native_art_component, (directory, basename))
    variant = MONTH_VARIANTS[month - 1]
    signed_fan_base = fan_base if fan_base < 0x80000000 else fan_base - 0x100000000
    generic = 0 if signed_fan_base > 20 else 1 if signed_fan_base > 8 else 2
    return (
        f'{TEAM_ROOT}/{directory}/{basename}_background{variant}.444',
        f'{TEAM_ROOT}/{directory}/{basename}_background.444',
        f'{TEAM_ROOT}/generic{generic}_background{variant}.444',
        f'{TEAM_ROOT}/generic.444',
    )


def header_variant(competition_id: int) -> str:
    if type(competition_id) is not int or competition_id < 0:
        raise ManagementBackgroundError('Missing original competition identity')
    return {0: 'Premiership', 21: 'Bundesliga', 22: 'Bundesliga',
            50: 'LNF', 51: 'LNF'}.get(competition_id, 'generic')


def staged_background_candidate(
    candidates: tuple[str, ...],
    staged_paths: dict[str, str],
) -> str:
    """Resolve the first provenance-staged path in native 0x5D3560 order."""
    for candidate in candidates:
        staged = staged_paths.get(candidate.casefold())
        if staged is not None:
            return staged
    raise ManagementBackgroundError(
        'No source-backed management background candidate is staged'
    )


@dataclass(frozen=True)
class ManagementShellImage:
    source_path: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes


class OriginalManagementBackground:
    def __init__(self, source_root, original_executable):
        self.root = Path(source_root)
        executable = Path(original_executable).read_bytes()
        self.tables = tables_from_original_executable(executable)
        self.quant = quantization_from_verified_executable(executable)
        self.paths = {p.casefold(): p for p in ASSET_HASHES}
        self.cache = {}

    def _image(self, source_path, rect):
        key = (source_path, rect)
        if key not in self.cache:
            raw = (self.root / source_path).read_bytes()
            if sha256(raw).hexdigest() != ASSET_HASHES[source_path]:
                raise ManagementBackgroundError('Original management art hash mismatch')
            image = decode_ea444(raw, tables=self.tables, quant=self.quant)
            x, y, width, height = rect
            if (image.width, image.height) != (width, height):
                raise ManagementBackgroundError('Original management art geometry mismatch')
            self.cache[key] = ManagementShellImage(source_path, x, y, width, height, image.rgba)
        return self.cache[key]

    def images(self, club_header):
        candidates = background_candidates(
            club_header.graphics_directory, club_header.graphics_basename,
            club_header.current_date.month, club_header.fan_base_index)
        base = staged_background_candidate(candidates, self.paths)
        header = f'{HEADER_ROOT}/back_2_{header_variant(club_header.competition_id)}.444'
        staged_header = self.paths.get(header.casefold())
        if staged_header is None:
            raise ManagementBackgroundError(
                'Competition management header is not source-staged'
            )
        return (self._image(base, (0, 0, 800, 600)),
                self._image(staged_header, (171, 0, 385, 95)))
