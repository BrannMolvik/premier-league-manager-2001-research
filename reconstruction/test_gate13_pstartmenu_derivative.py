from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from ea_font import EATextMask
from original_button_frames import (
    OriginalButtonAtlas,
    OriginalButtonFrame,
    PSTARTMENU_BUTTON_ATLAS,
)
from original_front_end_layout import PSTARTMENU_ACTIONS, SCREEN_SIZE
from original_pstartmenu_labels import PStartMenuCaption
from original_pstartmenu_resources import OriginalPStartMenuResources
from gate13_pstartmenu_derivative import (
    CONVERTER_ID,
    MANIFEST_NAME,
    PAYLOAD_NAME,
    PStartMenuDecoderProvenance,
    PStartMenuDerivativeError,
    build_pstartmenu_derivative_bundle,
    load_verified_pstartmenu_derivative_bundle,
)


def fixture_resources():
    background = bytes((1, 2, 3, 255)) * (
        SCREEN_SIZE[0] * SCREEN_SIZE[1]
    )
    atlas = OriginalButtonAtlas(
        PSTARTMENU_BUTTON_ATLAS,
        tuple(
            OriginalButtonFrame(
                PSTARTMENU_BUTTON_ATLAS.frame_width,
                PSTARTMENU_BUTTON_ATLAS.frame_height,
                bytes((index & 0xFF, 5, 6, 255))
                * (
                    PSTARTMENU_BUTTON_ATLAS.frame_width
                    * PSTARTMENU_BUTTON_ATLAS.frame_height
                ),
            )
            for index in range(
                PSTARTMENU_BUTTON_ATLAS.frame_count
            )
        ),
    )
    texts = (
        "Continue",
        "Start New Game",
        "Load Game",
        "Quit to Windows",
    )
    captions = tuple(
        PStartMenuCaption(
            event=action.event,
            source_idx_position=action.language_index,
            original_text=text,
            control_rect=action.rect,
            glyph_mask=EATextMask(
                2 + index,
                3,
                bytes([10 + index]) * ((2 + index) * 3),
            ),
            line_origin_x=action.rect.x + 1,
            line_origin_y=action.rect.y + 2,
            clip_rect=action.rect,
        )
        for index, (action, text) in enumerate(
            zip(PSTARTMENU_ACTIONS, texts, strict=True)
        )
    )
    return OriginalPStartMenuResources(
        background, atlas, captions
    )


DECODER = PStartMenuDecoderProvenance(
    executable_sha256=(
        "833bf95e92a1c76ade47106f8ad7d3ca307069b7e"
        "5778a7067cd0658838b7cc3"
    ),
    tqia_section_sha256="1" * 64,
    quant_source_sha256=(
        "6fb2af66cb6a51e4b3fa7da9bacab417fa40f180"
        "aa0c18c85adb2550c04c89eb"
    ),
)


class PStartMenuDerivativeTests(unittest.TestCase):
    def setUp(self):
        self.resources = fixture_resources()
        self.background_sha = sha256(
            self.resources.background_rgba
        ).hexdigest()

    def _build(self, directory):
        return build_pstartmenu_derivative_bundle(
            self.resources,
            Path(directory),
            decoder=DECODER,
            expected_background_sha256=self.background_sha,
        )

    def _load(self, directory, decoder=DECODER, manifest_sha=None):
        root = Path(directory)
        if manifest_sha is None:
            manifest_sha = sha256(
                (root / MANIFEST_NAME).read_bytes()
            ).hexdigest()
        return load_verified_pstartmenu_derivative_bundle(
            root,
            expected_decoder=decoder,
            expected_manifest_sha256=manifest_sha,
            expected_background_sha256=self.background_sha,
        )

    def test_bundle_is_deterministic_and_round_trips_render_inputs(
        self,
    ):
        with (
            tempfile.TemporaryDirectory() as a,
            tempfile.TemporaryDirectory() as b,
        ):
            self._build(a)
            self._build(b)
            self.assertEqual(
                (Path(a) / MANIFEST_NAME).read_bytes(),
                (Path(b) / MANIFEST_NAME).read_bytes(),
            )
            self.assertEqual(
                (Path(a) / PAYLOAD_NAME).read_bytes(),
                (Path(b) / PAYLOAD_NAME).read_bytes(),
            )
            loaded = self._load(a)
            self.assertEqual(
                loaded.background_rgba,
                self.resources.background_rgba,
            )
            self.assertEqual(
                tuple(
                    frame.rgba
                    for frame in loaded.button_atlas.frames
                ),
                tuple(
                    frame.rgba
                    for frame in self.resources.button_atlas.frames
                ),
            )
            self.assertEqual(
                tuple(
                    caption.glyph_mask.alpha
                    for caption in loaded.captions
                ),
                tuple(
                    caption.glyph_mask.alpha
                    for caption in self.resources.captions
                ),
            )
            self.assertEqual(
                tuple(
                    caption.original_text
                    for caption in loaded.captions
                ),
                (
                    "Continue",
                    "Start New Game",
                    "Load Game",
                    "Quit to Windows",
                ),
            )

    def test_payload_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            self._build(directory)
            path = Path(directory) / PAYLOAD_NAME
            data = bytearray(path.read_bytes())
            data[-1] ^= 0xFF
            path.write_bytes(data)
            with self.assertRaisesRegex(
                PStartMenuDerivativeError,
                "payload identity",
            ):
                self._load(directory)

    def test_manifest_requires_independently_pinned_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            self._build(directory)
            path = Path(directory) / MANIFEST_NAME
            pinned = sha256(path.read_bytes()).hexdigest()
            manifest = json.loads(
                path.read_text(encoding="utf-8")
            )
            path.write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                PStartMenuDerivativeError,
                "pinned receipt",
            ):
                self._load(directory, manifest_sha=pinned)

    def test_source_or_decoder_provenance_drift_fails_closed(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            self._build(directory)
            path = Path(directory) / MANIFEST_NAME
            manifest = json.loads(
                path.read_text(encoding="utf-8")
            )
            manifest["source_assets"][0]["sha256"] = "0" * 64
            path.write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                PStartMenuDerivativeError,
                "original-source",
            ):
                self._load(directory)

        with tempfile.TemporaryDirectory() as directory:
            self._build(directory)
            other = replace(
                DECODER, tqia_section_sha256="2" * 64
            )
            with self.assertRaisesRegex(
                PStartMenuDerivativeError,
                "decoder provenance",
            ):
                self._load(directory, decoder=other)

    def test_schema_and_caption_binding_drift_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            self._build(directory)
            path = Path(directory) / MANIFEST_NAME
            manifest = json.loads(
                path.read_text(encoding="utf-8")
            )
            manifest["converter_id"] = CONVERTER_ID + "-changed"
            path.write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                PStartMenuDerivativeError,
                "schema/converter",
            ):
                self._load(directory)

        with tempfile.TemporaryDirectory() as directory:
            self._build(directory)
            path = Path(directory) / MANIFEST_NAME
            manifest = json.loads(
                path.read_text(encoding="utf-8")
            )
            manifest["payload"]["captions"][0]["event"] = 99
            path.write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                PStartMenuDerivativeError,
                "caption binding",
            ):
                self._load(directory)

    def test_decoder_identity_rejects_noncanonical_executable_or_quant_source(
        self,
    ):
        with self.assertRaisesRegex(
            PStartMenuDerivativeError, "canonical FM2001"
        ):
            PStartMenuDecoderProvenance(
                executable_sha256="0" * 64,
                tqia_section_sha256="1" * 64,
                quant_source_sha256=DECODER.quant_source_sha256,
            )
        with self.assertRaisesRegex(
            PStartMenuDerivativeError, "quantization"
        ):
            PStartMenuDecoderProvenance(
                executable_sha256=DECODER.executable_sha256,
                tqia_section_sha256="1" * 64,
                quant_source_sha256="0" * 64,
            )


if __name__ == "__main__":
    unittest.main()
