"""Exact decoded pixel seam for directly bound FastView chrome."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate14_fastview_chrome import (
    FASTVIEW_DIRECT_CHROME_RESOURCES,
    FastViewChromeError,
    FastViewChromeResource,
    REJECTED_UNBOUND_BACKGROUND_PATH,
)


class OriginalFastViewChromeArtError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalFastViewChromePlacement:
    resource_name: str
    source_path: str
    rect: tuple[int, int, int, int]
    rgba: bytes


@dataclass(frozen=True)
class OriginalFastViewChromeArt:
    placements: tuple[OriginalFastViewChromePlacement, ...]
    rejected_unbound_background_path: str = REJECTED_UNBOUND_BACKGROUND_PATH
    complete_fastview_frame_available: bool = False


def _decoded_for(
    decoded: dict[str, EA444DecodedImage],
    resource: FastViewChromeResource,
) -> EA444DecodedImage:
    try:
        image = decoded[resource.name]
    except KeyError as exc:
        raise OriginalFastViewChromeArtError(
            f"Missing decoded FastView chrome: {resource.name}"
        ) from exc
    if not isinstance(image, EA444DecodedImage):
        raise OriginalFastViewChromeArtError(
            f"Decoded FastView chrome has wrong type: {resource.name}"
        )
    if (image.width, image.height) != resource.size:
        raise OriginalFastViewChromeArtError(
            f"Decoded FastView chrome geometry mismatch: {resource.name}"
        )
    if len(image.rgba) != image.width * image.height * 4:
        raise OriginalFastViewChromeArtError(
            f"Decoded FastView chrome RGBA payload incomplete: {resource.name}"
        )
    return image


def build_fastview_chrome_art(
    decoded: dict[str, EA444DecodedImage],
) -> OriginalFastViewChromeArt:
    """Return only the two directly PictureControl-bound source placements."""
    if not isinstance(decoded, dict):
        raise OriginalFastViewChromeArtError(
            "FastView chrome decoded art must be keyed by resource name"
        )
    placements = []
    for resource in FASTVIEW_DIRECT_CHROME_RESOURCES:
        image = _decoded_for(decoded, resource)
        placements.append(
            OriginalFastViewChromePlacement(
                resource_name=resource.name,
                source_path=resource.source_path,
                rect=resource.rect,
                rgba=image.rgba,
            )
        )
    return OriginalFastViewChromeArt(tuple(placements))


def load_verified_fastview_chrome_art_from_source(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalFastViewChromeArt:
    """Hash-check and decode the two directly owned FastView chrome resources.

    This source-root loader is intentionally separate from repository staging.
    It allows a runtime/private audit to consume the authorized originals
    without committing the binary resources or substituting replacement art.
    """
    root = Path(source_root)
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalFastViewChromeArtError(
            f"Missing canonical original executable: {original_executable}"
        ) from exc

    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)

    decoded: dict[str, EA444DecodedImage] = {}
    for resource in FASTVIEW_DIRECT_CHROME_RESOURCES:
        path = root / Path(resource.source_path)
        try:
            raw = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalFastViewChromeArtError(
                f"Missing original FastView chrome: {resource.source_path}"
            ) from exc
        if len(raw) != resource.byte_size:
            raise OriginalFastViewChromeArtError(
                f"FastView chrome byte-size mismatch: {resource.source_path}"
            )
        if sha256(raw).hexdigest() != resource.sha256:
            raise OriginalFastViewChromeArtError(
                f"FastView chrome checksum mismatch: {resource.source_path}"
            )
        image = decode_ea444(raw, tables=tables, quant=quant)
        if (image.width, image.height) != resource.size:
            raise OriginalFastViewChromeArtError(
                f"Decoded FastView chrome geometry mismatch: {resource.source_path}"
            )
        decoded[resource.name] = image

    return build_fastview_chrome_art(decoded)
