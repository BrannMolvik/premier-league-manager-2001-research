"""Checksum-gated original FastView TeamTable art loader.

The seven TeamTable/PlayerRow EA444 resources already have source-proven exact
paths, byte sizes, SHA-256 identities and decoded geometry. This module turns
those identities into a reusable decoded-art boundary without committing or
substituting proprietary pixels.

A caller supplies an extracted authorized original game root and the canonical
FOOTBAL.EXE. The executable is independently hash-gated by the EA444 table and
quantization extractors before any resource is decoded.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate14_fastview_team import (
    BLANK_BAR,
    TEAM_BAR_1,
    TEAM_BAR_2,
    TEAM_NAME_GRID_1,
    TEAM_NAME_GRID_2,
    TEAM_NAME_GRID_3,
    TEAM_NAME_GRID_4,
    FastViewTeamResource,
)


FASTVIEW_TEAM_ART_RESOURCES = (
    TEAM_NAME_GRID_1,
    TEAM_NAME_GRID_2,
    TEAM_NAME_GRID_3,
    TEAM_NAME_GRID_4,
    TEAM_BAR_1,
    BLANK_BAR,
    TEAM_BAR_2,
)


class OriginalFastViewTeamArtError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalFastViewTeamDecodedResource:
    source: FastViewTeamResource
    image: EA444DecodedImage

    def __post_init__(self) -> None:
        if type(self.source) is not FastViewTeamResource:
            raise OriginalFastViewTeamArtError(
                "TeamTable decoded resource requires exact source metadata"
            )
        if not isinstance(self.image, EA444DecodedImage):
            raise OriginalFastViewTeamArtError(
                f"Decoded TeamTable art has wrong type: {self.source.name}"
            )
        if (self.image.width, self.image.height) != self.source.size:
            raise OriginalFastViewTeamArtError(
                f"Decoded TeamTable geometry mismatch: {self.source.name}"
            )
        if len(self.image.rgba) != self.image.width * self.image.height * 4:
            raise OriginalFastViewTeamArtError(
                f"Decoded TeamTable RGBA payload incomplete: {self.source.name}"
            )


@dataclass(frozen=True)
class OriginalFastViewTeamArt:
    resources: tuple[OriginalFastViewTeamDecodedResource, ...]

    def __post_init__(self) -> None:
        if tuple(item.source for item in self.resources) != FASTVIEW_TEAM_ART_RESOURCES:
            raise OriginalFastViewTeamArtError(
                "TeamTable art must preserve the exact seven-resource source order"
            )
        names = tuple(item.source.name for item in self.resources)
        if len(set(names)) != len(names):
            raise OriginalFastViewTeamArtError(
                "TeamTable art contains duplicate resource identities"
            )

    def image_for(self, resource: FastViewTeamResource) -> EA444DecodedImage:
        if type(resource) is not FastViewTeamResource:
            raise OriginalFastViewTeamArtError(
                "TeamTable resource lookup requires exact source metadata"
            )
        for item in self.resources:
            if item.source is resource:
                return item.image
        raise OriginalFastViewTeamArtError(
            f"TeamTable source resource is not loaded: {resource.name}"
        )


def build_fastview_team_art(
    decoded: dict[str, EA444DecodedImage],
) -> OriginalFastViewTeamArt:
    """Validate an already decoded exact seven-resource TeamTable set."""
    if not isinstance(decoded, dict):
        raise OriginalFastViewTeamArtError(
            "TeamTable decoded art must be keyed by source resource name"
        )

    expected_names = tuple(resource.name for resource in FASTVIEW_TEAM_ART_RESOURCES)
    if set(decoded) != set(expected_names):
        missing = tuple(name for name in expected_names if name not in decoded)
        unexpected = tuple(name for name in decoded if name not in expected_names)
        raise OriginalFastViewTeamArtError(
            "TeamTable decoded resource set differs from the exact source family: "
            f"missing={missing}, unexpected={unexpected}"
        )

    return OriginalFastViewTeamArt(
        tuple(
            OriginalFastViewTeamDecodedResource(resource, decoded[resource.name])
            for resource in FASTVIEW_TEAM_ART_RESOURCES
        )
    )


def _read_verified_resource(
    source_root: Path,
    resource: FastViewTeamResource,
) -> bytes:
    path = source_root / Path(resource.source_path)
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalFastViewTeamArtError(
            f"Missing original TeamTable resource: {resource.source_path}"
        ) from exc

    if len(data) != resource.byte_size:
        raise OriginalFastViewTeamArtError(
            f"Original TeamTable resource byte-size mismatch: {resource.source_path}"
        )
    digest = sha256(data).hexdigest()
    if digest != resource.sha256:
        raise OriginalFastViewTeamArtError(
            f"Original TeamTable resource checksum mismatch: {resource.source_path}"
        )
    return data


def load_verified_fastview_team_art(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalFastViewTeamArt:
    """Read, hash-check and decode all seven exact TeamTable EA444 resources."""
    root = Path(source_root)
    try:
        executable = Path(original_executable).read_bytes()
    except FileNotFoundError as exc:
        raise OriginalFastViewTeamArtError(
            f"Missing canonical original executable: {original_executable}"
        ) from exc

    # Both helpers independently require the exact canonical executable hash and
    # source table locations. Do not decode resource bytes with replacement
    # codec tables.
    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)

    decoded: dict[str, EA444DecodedImage] = {}
    for resource in FASTVIEW_TEAM_ART_RESOURCES:
        raw = _read_verified_resource(root, resource)
        image = decode_ea444(raw, tables=tables, quant=quant)
        if (image.width, image.height) != resource.size:
            raise OriginalFastViewTeamArtError(
                f"Decoded TeamTable geometry mismatch: {resource.source_path}"
            )
        decoded[resource.name] = image

    return build_fastview_team_art(decoded)
