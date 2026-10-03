"""Decoded pixel seam for the source-closed FastView chrome strips."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate14_fastview_chrome import (
    FASTVIEW_CHROME_RESOURCES,
    FastViewChromeResource,
    imported_chrome_path,
    validate_imported_fastview_chrome,
)


class OriginalFastViewChromeArtError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalFastViewChromePlacement:
    resource_name: str
    source_path: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)


@dataclass(frozen=True)
class OriginalFastViewChromeArt:
    placements: tuple[OriginalFastViewChromePlacement, ...]
    middle_surface_recovered: bool = False

    @property
    def complete_800x600_frame_available(self) -> bool:
        return self.middle_surface_recovered


def build_fastview_chrome_art(
    decoded_art: dict[str, EA444DecodedImage],
) -> OriginalFastViewChromeArt:
    if not isinstance(decoded_art, dict):
        raise OriginalFastViewChromeArtError("decoded chrome art must be a dict")
    placements = []
    for resource in FASTVIEW_CHROME_RESOURCES:
        image = decoded_art.get(resource.name)
        if not isinstance(image, EA444DecodedImage):
            raise OriginalFastViewChromeArtError(
                f"missing decoded FastView chrome art: {resource.name}"
            )
        if (image.width, image.height) != (resource.width, resource.height):
            raise OriginalFastViewChromeArtError(
                f"decoded FastView chrome geometry mismatch: {resource.name}"
            )
        if len(image.rgba) != image.width * image.height * 4:
            raise OriginalFastViewChromeArtError(
                f"decoded FastView chrome RGBA payload is incomplete: {resource.name}"
            )
        placements.append(
            OriginalFastViewChromePlacement(
                resource_name=resource.name,
                source_path=resource.source_path,
                x=resource.x,
                y=resource.y,
                width=resource.width,
                height=resource.height,
                rgba=image.rgba,
            )
        )
    return OriginalFastViewChromeArt(tuple(placements))


def load_verified_fastview_chrome_art(
    repo_root: str | Path,
    original_executable: str | Path,
) -> OriginalFastViewChromeArt:
    root = Path(repo_root)
    validate_imported_fastview_chrome(root)
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalFastViewChromeArtError(
            f"missing original executable: {original_executable}"
        ) from exc
    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)
    decoded = {}
    for resource in FASTVIEW_CHROME_RESOURCES:
        decoded[resource.name] = decode_ea444(
            imported_chrome_path(root, resource).read_bytes(),
            tables=tables,
            quant=quant,
        )
    return build_fastview_chrome_art(decoded)
