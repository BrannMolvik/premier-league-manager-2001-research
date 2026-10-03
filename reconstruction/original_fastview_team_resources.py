"""Exact original FastViewTeam/TeamTable EA444 resource contract.

The seven resources in this module are already source-closed by canonical
executable ownership and authorized-disc hashes. They may be supplied from an
outside-Git extracted original source root or intentionally staged later under
original_assets. Validation is byte-for-byte and does not infer text pixels,
draw order, or dynamic PictureControl crop behavior.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import struct

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


class OriginalFastViewTeamResourceError(ValueError):
    pass


FASTVIEW_TEAM_TABLE_RESOURCES = (
    TEAM_NAME_GRID_1,
    TEAM_NAME_GRID_2,
    TEAM_NAME_GRID_3,
    TEAM_NAME_GRID_4,
    TEAM_BAR_1,
    BLANK_BAR,
    TEAM_BAR_2,
)


def source_resource_path(
    source_root: str | Path,
    resource: FastViewTeamResource,
) -> Path:
    if not isinstance(resource, FastViewTeamResource):
        raise OriginalFastViewTeamResourceError(
            "FastViewTeam resource must use the source-backed resource contract"
        )
    return Path(source_root) / resource.source_path


def validate_source_fastview_team_resources(
    source_root: str | Path,
) -> tuple[FastViewTeamResource, ...]:
    """Validate all seven exact original TeamTable resources under source_root."""
    for resource in FASTVIEW_TEAM_TABLE_RESOURCES:
        path = source_resource_path(source_root, resource)
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalFastViewTeamResourceError(
                f"Missing original FastViewTeam resource: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise OriginalFastViewTeamResourceError(
                f"FastViewTeam byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalFastViewTeamResourceError(
                f"FastViewTeam checksum mismatch: {resource.source_path}"
            )
        if len(data) < 4:
            raise OriginalFastViewTeamResourceError(
                f"FastViewTeam resource has no EA444 header: {resource.source_path}"
            )
        width, height = struct.unpack_from("<HH", data, 0)
        if (width, height) != resource.size:
            raise OriginalFastViewTeamResourceError(
                f"FastViewTeam geometry mismatch: {resource.source_path}"
            )
    return FASTVIEW_TEAM_TABLE_RESOURCES
