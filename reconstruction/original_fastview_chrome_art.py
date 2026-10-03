"""Exact decoded pixel seam for directly bound FastView chrome."""
from __future__ import annotations

from dataclasses import dataclass

from ea444_decoder import EA444DecodedImage
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
