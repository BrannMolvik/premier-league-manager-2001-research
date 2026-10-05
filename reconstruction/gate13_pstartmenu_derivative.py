"""Deterministic, fail-closed PStartMenu render-derivative bundle.

This module is deliberately not wired into normal startup yet. It defines the
package-staged compatibility derivative described by issue #482 so that a
future private/source-backed generation step can move immutable first-screen
decode/composition work out of the user's cold-launch path without weakening
provenance.

A bundle contains:
- one deterministic binary payload with the exact composed 800x600 RGBA
  background, the 23 source-order button frames, and four caption alpha masks;
- one canonical JSON manifest with exact original-source identities, exact
  decoder-input provenance, payload SHA-256, geometry, offsets, and text
  metadata.

Normal runtime must not consume a bundle until its exact source-derived decoder
inputs and a real canonical derivative have been independently verified.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re

from ea444_quantization import (
    ORIGINAL_QUANT_SHA256,
    quantization_from_verified_executable,
)
from ea444_tables import (
    CANONICAL_EXE_SHA256,
    tables_from_original_executable,
)
from ea_font import EATextMask
from gate13_first_screen_manifest_readiness import assert_first_screen_manifest_ready
from gate13_first_screen_selection import ExpectedSource, FIRST_SCREEN_ORIGINALS
from original_button_frames import (
    OriginalButtonAtlas,
    OriginalButtonFrame,
    PSTARTMENU_BUTTON_ATLAS,
)
from original_front_end_layout import OriginalRect, PSTARTMENU_ACTIONS, SCREEN_SIZE
from original_pstartmenu_labels import PStartMenuCaption
from original_pstartmenu_resources import (
    COMPOSED_BACKGROUND_RGBA_SHA256,
    ENGLISH_ACTION_TEXTS,
    OriginalPStartMenuResources,
)


SCHEMA_VERSION = 1
CONVERTER_ID = "fm2001-pstartmenu-render-derivative-v1"
MANIFEST_NAME = "manifest.json"
PAYLOAD_NAME = "payload.bin"
PSTARTMENU_SOURCE_PATHS = (
    "FM2001_Art/Generic/bground.444",
    "FM2001_Art/Generic/main_menu/main_menu_bground.444",
    "FM2001_Art/Generic/GenericButtonsAndBars/button_type_1.444",
    "Fonts/Zurich_BdXCn_BT_20pixel.fnt",
    "English.str",
    "English.idx",
)
_PSTARTMENU_BY_PATH = {item.path: item for item in FIRST_SCREEN_ORIGINALS}
PSTARTMENU_SOURCE_ORIGINALS = tuple(
    _PSTARTMENU_BY_PATH[path] for path in PSTARTMENU_SOURCE_PATHS
)
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class PStartMenuDerivativeError(ValueError):
    """Derivative bundle bytes or provenance differ from the verified contract."""


@dataclass(frozen=True)
class PStartMenuDecoderProvenance:
    executable_sha256: str
    tqia_section_sha256: str
    quant_source_sha256: str
    converter_id: str = CONVERTER_ID

    def __post_init__(self) -> None:
        values = (
            self.executable_sha256,
            self.tqia_section_sha256,
            self.quant_source_sha256,
        )
        if any(not _HEX64.fullmatch(value) for value in values):
            raise PStartMenuDerivativeError(
                "Decoder provenance requires lowercase SHA-256"
            )
        if self.executable_sha256 != CANONICAL_EXE_SHA256:
            raise PStartMenuDerivativeError(
                "Decoder executable is not the canonical FM2001 build"
            )
        if self.quant_source_sha256 != ORIGINAL_QUANT_SHA256:
            raise PStartMenuDerivativeError(
                "Decoder quantization source identity differs"
            )
        if self.converter_id != CONVERTER_ID:
            raise PStartMenuDerivativeError(
                "Unknown PStartMenu derivative converter identity"
            )


def decoder_provenance_from_verified_executable(
    executable: bytes,
) -> PStartMenuDecoderProvenance:
    """Derive immutable decoder identity only from the canonical verified EXE."""
    tables = tables_from_original_executable(executable)
    quantization_from_verified_executable(executable)
    return PStartMenuDecoderProvenance(
        executable_sha256=sha256(executable).hexdigest(),
        tqia_section_sha256=sha256(tables.raw_section).hexdigest(),
        quant_source_sha256=ORIGINAL_QUANT_SHA256,
    )


def _canonical_json(data: dict) -> bytes:
    return (
        json.dumps(
            data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        + "\n"
    ).encode("utf-8")


def _source_rows(
    expected_sources: tuple[ExpectedSource, ...],
) -> list[dict[str, str]]:
    return [
        {"path": item.path, "sha256": item.sha256}
        for item in expected_sources
    ]


def _decoder_row(
    decoder: PStartMenuDecoderProvenance,
) -> dict[str, str]:
    return {
        "converter_id": decoder.converter_id,
        "executable_sha256": decoder.executable_sha256,
        "quant_source_sha256": decoder.quant_source_sha256,
        "tqia_section_sha256": decoder.tqia_section_sha256,
    }


def _rect_row(rect: OriginalRect) -> list[int]:
    return [rect.x, rect.y, rect.width, rect.height]


def _require_expected_resources(
    resources: OriginalPStartMenuResources,
    *,
    expected_background_sha256: str,
    expected_caption_texts: tuple[str, ...],
) -> None:
    if (
        sha256(resources.background_rgba).hexdigest()
        != expected_background_sha256
    ):
        raise PStartMenuDerivativeError(
            "Composed PStartMenu background identity differs"
        )
    if resources.button_atlas.spec != PSTARTMENU_BUTTON_ATLAS:
        raise PStartMenuDerivativeError(
            "PStartMenu derivative requires the canonical button atlas"
        )
    if (
        tuple(item.original_text for item in resources.captions)
        != expected_caption_texts
    ):
        raise PStartMenuDerivativeError(
            "PStartMenu caption text identity differs"
        )


def build_pstartmenu_derivative_bundle(
    resources: OriginalPStartMenuResources,
    output_dir: Path,
    *,
    decoder: PStartMenuDecoderProvenance,
    expected_sources: tuple[
        ExpectedSource, ...
    ] = PSTARTMENU_SOURCE_ORIGINALS,
    expected_background_sha256: str = COMPOSED_BACKGROUND_RGBA_SHA256,
    expected_caption_texts: tuple[str, ...] = ENGLISH_ACTION_TEXTS,
) -> tuple[Path, Path]:
    """Write one deterministic manifest/payload pair from verified render inputs."""
    _require_expected_resources(
        resources,
        expected_background_sha256=expected_background_sha256,
        expected_caption_texts=expected_caption_texts,
    )
    if len(expected_sources) != len(PSTARTMENU_SOURCE_PATHS):
        raise PStartMenuDerivativeError(
            "PStartMenu derivative source set is incomplete"
        )

    payload = bytearray()
    background_offset = len(payload)
    payload.extend(resources.background_rgba)
    background_size = len(resources.background_rgba)

    buttons_offset = len(payload)
    for frame in resources.button_atlas.frames:
        payload.extend(frame.rgba)
    buttons_size = len(payload) - buttons_offset

    caption_rows: list[dict] = []
    for caption in resources.captions:
        offset = len(payload)
        payload.extend(caption.glyph_mask.alpha)
        caption_rows.append(
            {
                "event": caption.event,
                "source_idx_position": caption.source_idx_position,
                "original_text": caption.original_text,
                "control_rect": _rect_row(caption.control_rect),
                "mask_width": caption.glyph_mask.width,
                "mask_height": caption.glyph_mask.height,
                "line_origin": [
                    caption.line_origin_x,
                    caption.line_origin_y,
                ],
                "clip_rect": _rect_row(caption.clip_rect),
                "native_style": caption.native_style,
                "normal_color_16": caption.normal_color_16,
                "alternate_group_color_16": (
                    caption.alternate_group_color_16
                ),
                "payload_offset": offset,
                "payload_size": len(caption.glyph_mask.alpha),
            }
        )

    payload_bytes = bytes(payload)
    atlas_bytes = payload_bytes[
        buttons_offset : buttons_offset + buttons_size
    ]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "converter_id": CONVERTER_ID,
        "screen": "PStartMenu",
        "source_assets": _source_rows(expected_sources),
        "decoder": _decoder_row(decoder),
        "geometry": {
            "screen": list(SCREEN_SIZE),
            "button_atlas": {
                "frame_count": PSTARTMENU_BUTTON_ATLAS.frame_count,
                "frame_width": PSTARTMENU_BUTTON_ATLAS.frame_width,
                "frame_height": PSTARTMENU_BUTTON_ATLAS.frame_height,
            },
        },
        "payload": {
            "file": PAYLOAD_NAME,
            "size": len(payload_bytes),
            "sha256": sha256(payload_bytes).hexdigest(),
            "background": {
                "offset": background_offset,
                "size": background_size,
                "sha256": sha256(
                    resources.background_rgba
                ).hexdigest(),
            },
            "button_atlas": {
                "offset": buttons_offset,
                "size": buttons_size,
                "sha256": sha256(atlas_bytes).hexdigest(),
            },
            "captions": caption_rows,
        },
    }

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    payload_path = directory / PAYLOAD_NAME
    manifest_path = directory / MANIFEST_NAME
    payload_path.write_bytes(payload_bytes)
    manifest_path.write_bytes(_canonical_json(manifest))
    return manifest_path, payload_path


def _require_keys(
    data: dict, expected: set[str], name: str
) -> None:
    if set(data) != expected:
        raise PStartMenuDerivativeError(
            f"{name} manifest keys differ from schema"
        )


def _slice(
    payload: bytes, offset: object, size: object, name: str
) -> bytes:
    if (
        type(offset) is not int
        or type(size) is not int
        or offset < 0
        or size < 0
    ):
        raise PStartMenuDerivativeError(
            f"{name} payload range is invalid"
        )
    end = offset + size
    if end > len(payload):
        raise PStartMenuDerivativeError(
            f"{name} payload range exceeds container"
        )
    return payload[offset:end]


def _rect_from_row(
    value: object, name: str
) -> OriginalRect:
    if (
        not isinstance(value, list)
        or len(value) != 4
        or any(type(item) is not int for item in value)
    ):
        raise PStartMenuDerivativeError(
            f"{name} rectangle is malformed"
        )
    return OriginalRect(*value)


def load_verified_pstartmenu_derivative_bundle(
    bundle_dir: Path,
    *,
    expected_decoder: PStartMenuDecoderProvenance,
    expected_manifest_sha256: str,
    expected_sources: tuple[
        ExpectedSource, ...
    ] = PSTARTMENU_SOURCE_ORIGINALS,
    expected_background_sha256: str = COMPOSED_BACKGROUND_RGBA_SHA256,
    expected_caption_texts: tuple[str, ...] = ENGLISH_ACTION_TEXTS,
) -> OriginalPStartMenuResources:
    """Rehydrate resources only after every manifest and payload check passes."""
    directory = Path(bundle_dir)
    manifest_path = directory / MANIFEST_NAME
    payload_path = directory / PAYLOAD_NAME
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        payload = payload_path.read_bytes()
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise PStartMenuDerivativeError(
            "PStartMenu derivative bundle is unreadable"
        ) from exc
    if not isinstance(manifest, dict):
        raise PStartMenuDerivativeError(
            "PStartMenu derivative manifest must be an object"
        )
    if (
        not _HEX64.fullmatch(expected_manifest_sha256)
        or sha256(manifest_bytes).hexdigest()
        != expected_manifest_sha256
    ):
        raise PStartMenuDerivativeError(
            "Derivative manifest identity differs from the pinned receipt"
        )

    _require_keys(
        manifest,
        {
            "schema_version",
            "converter_id",
            "screen",
            "source_assets",
            "decoder",
            "geometry",
            "payload",
        },
        "top-level",
    )
    if (
        manifest["schema_version"] != SCHEMA_VERSION
        or manifest["converter_id"] != CONVERTER_ID
    ):
        raise PStartMenuDerivativeError(
            "PStartMenu derivative schema/converter differs"
        )
    if manifest["screen"] != "PStartMenu":
        raise PStartMenuDerivativeError(
            "Derivative is not for PStartMenu"
        )
    if manifest["source_assets"] != _source_rows(expected_sources):
        raise PStartMenuDerivativeError(
            "Derivative original-source provenance differs"
        )
    if manifest["decoder"] != _decoder_row(expected_decoder):
        raise PStartMenuDerivativeError(
            "Derivative decoder provenance differs"
        )

    geometry = manifest["geometry"]
    if not isinstance(geometry, dict):
        raise PStartMenuDerivativeError(
            "Derivative geometry is malformed"
        )
    _require_keys(
        geometry, {"screen", "button_atlas"}, "geometry"
    )
    if geometry["screen"] != list(SCREEN_SIZE):
        raise PStartMenuDerivativeError(
            "Derivative screen geometry differs"
        )
    atlas_geometry = geometry["button_atlas"]
    if atlas_geometry != {
        "frame_count": PSTARTMENU_BUTTON_ATLAS.frame_count,
        "frame_width": PSTARTMENU_BUTTON_ATLAS.frame_width,
        "frame_height": PSTARTMENU_BUTTON_ATLAS.frame_height,
    }:
        raise PStartMenuDerivativeError(
            "Derivative button-atlas geometry differs"
        )

    payload_meta = manifest["payload"]
    if not isinstance(payload_meta, dict):
        raise PStartMenuDerivativeError(
            "Derivative payload metadata is malformed"
        )
    _require_keys(
        payload_meta,
        {
            "file",
            "size",
            "sha256",
            "background",
            "button_atlas",
            "captions",
        },
        "payload",
    )
    if payload_meta["file"] != PAYLOAD_NAME:
        raise PStartMenuDerivativeError(
            "Derivative payload file name differs"
        )
    if (
        payload_meta["size"] != len(payload)
        or payload_meta["sha256"]
        != sha256(payload).hexdigest()
    ):
        raise PStartMenuDerivativeError(
            "Derivative payload identity differs"
        )

    background_meta = payload_meta["background"]
    if not isinstance(background_meta, dict):
        raise PStartMenuDerivativeError(
            "Derivative background metadata is malformed"
        )
    _require_keys(
        background_meta, {"offset", "size", "sha256"}, "background"
    )
    background = _slice(
        payload,
        background_meta["offset"],
        background_meta["size"],
        "background",
    )
    if (
        len(background) != SCREEN_SIZE[0] * SCREEN_SIZE[1] * 4
        or sha256(background).hexdigest()
        != background_meta["sha256"]
        or background_meta["sha256"]
        != expected_background_sha256
    ):
        raise PStartMenuDerivativeError(
            "Derivative background bytes differ"
        )

    atlas_meta = payload_meta["button_atlas"]
    if not isinstance(atlas_meta, dict):
        raise PStartMenuDerivativeError(
            "Derivative button-atlas metadata is malformed"
        )
    _require_keys(
        atlas_meta, {"offset", "size", "sha256"}, "button_atlas"
    )
    atlas_bytes = _slice(
        payload,
        atlas_meta["offset"],
        atlas_meta["size"],
        "button atlas",
    )
    frame_size = (
        PSTARTMENU_BUTTON_ATLAS.frame_width
        * PSTARTMENU_BUTTON_ATLAS.frame_height
        * 4
    )
    expected_atlas_size = (
        frame_size * PSTARTMENU_BUTTON_ATLAS.frame_count
    )
    if (
        len(atlas_bytes) != expected_atlas_size
        or sha256(atlas_bytes).hexdigest()
        != atlas_meta["sha256"]
    ):
        raise PStartMenuDerivativeError(
            "Derivative button-atlas bytes differ"
        )
    frames = tuple(
        OriginalButtonFrame(
            PSTARTMENU_BUTTON_ATLAS.frame_width,
            PSTARTMENU_BUTTON_ATLAS.frame_height,
            atlas_bytes[
                index * frame_size : (index + 1) * frame_size
            ],
        )
        for index in range(
            PSTARTMENU_BUTTON_ATLAS.frame_count
        )
    )

    caption_meta = payload_meta["captions"]
    if (
        not isinstance(caption_meta, list)
        or len(caption_meta) != len(PSTARTMENU_ACTIONS)
    ):
        raise PStartMenuDerivativeError(
            "Derivative caption set is incomplete"
        )
    captions: list[PStartMenuCaption] = []
    for index, (action, row) in enumerate(
        zip(PSTARTMENU_ACTIONS, caption_meta, strict=True)
    ):
        if not isinstance(row, dict):
            raise PStartMenuDerivativeError(
                "Derivative caption metadata is malformed"
            )
        _require_keys(
            row,
            {
                "event",
                "source_idx_position",
                "original_text",
                "control_rect",
                "mask_width",
                "mask_height",
                "line_origin",
                "clip_rect",
                "native_style",
                "normal_color_16",
                "alternate_group_color_16",
                "payload_offset",
                "payload_size",
            },
            f"caption {index}",
        )
        if (
            row["event"] != action.event
            or row["source_idx_position"]
            != action.language_index
            or row["original_text"]
            != expected_caption_texts[index]
            or _rect_from_row(
                row["control_rect"], "caption control"
            )
            != action.rect
        ):
            raise PStartMenuDerivativeError(
                "Derivative caption binding differs"
            )
        if (
            type(row["mask_width"]) is not int
            or type(row["mask_height"]) is not int
            or row["mask_width"] < 0
            or row["mask_height"] < 0
        ):
            raise PStartMenuDerivativeError(
                "Derivative caption mask geometry is invalid"
            )
        mask = _slice(
            payload,
            row["payload_offset"],
            row["payload_size"],
            "caption",
        )
        if (
            len(mask)
            != row["mask_width"] * row["mask_height"]
        ):
            raise PStartMenuDerivativeError(
                "Derivative caption mask byte count differs"
            )
        line_origin = row["line_origin"]
        if (
            not isinstance(line_origin, list)
            or len(line_origin) != 2
            or any(
                type(item) is not int
                for item in line_origin
            )
        ):
            raise PStartMenuDerivativeError(
                "Derivative caption line origin is malformed"
            )
        captions.append(
            PStartMenuCaption(
                event=row["event"],
                source_idx_position=row[
                    "source_idx_position"
                ],
                original_text=row["original_text"],
                control_rect=action.rect,
                glyph_mask=EATextMask(
                    row["mask_width"],
                    row["mask_height"],
                    mask,
                ),
                line_origin_x=line_origin[0],
                line_origin_y=line_origin[1],
                clip_rect=_rect_from_row(
                    row["clip_rect"], "caption clip"
                ),
                native_style=row["native_style"],
                normal_color_16=row["normal_color_16"],
                alternate_group_color_16=row[
                    "alternate_group_color_16"
                ],
            )
        )

    resources = OriginalPStartMenuResources(
        background_rgba=background,
        button_atlas=OriginalButtonAtlas(
            PSTARTMENU_BUTTON_ATLAS, frames
        ),
        captions=tuple(captions),
    )
    _require_expected_resources(
        resources,
        expected_background_sha256=expected_background_sha256,
        expected_caption_texts=expected_caption_texts,
    )
    return resources


def assert_repository_pstartmenu_derivative_ready(
    repo_root: Path,
    *,
    bundle_relative: Path = (
        Path("original_assets")
        / "converted"
        / "pstartmenu-v1"
    ),
    expected_decoder: PStartMenuDecoderProvenance,
    expected_manifest_sha256: str,
    expected_sources: tuple[
        ExpectedSource, ...
    ] = PSTARTMENU_SOURCE_ORIGINALS,
) -> OriginalPStartMenuResources:
    """Audit source originals and derivative together; intended for package CI later."""
    root = Path(repo_root)
    assert_first_screen_manifest_ready(
        root, expected_assets=expected_sources
    )
    return load_verified_pstartmenu_derivative_bundle(
        root / bundle_relative,
        expected_decoder=expected_decoder,
        expected_manifest_sha256=expected_manifest_sha256,
        expected_sources=expected_sources,
    )
