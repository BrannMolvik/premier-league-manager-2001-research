"""Non-interactive native Inbox list milestone; no GUI or RNG-owner claims."""
from dataclasses import replace
from datetime import date, timedelta
from importlib.util import find_spec
import os
from pathlib import Path
import struct
from types import SimpleNamespace
import unittest

from ea444_decoder import EA444DecodedImage
from original_eamail_live_canvas import (
    OriginalEAMailRowArt, load_verified_original_eamail_row_art,
    original_eamail_initial_status_layers, original_eamail_scroll_at_point,
    original_eamail_scroll_layers, original_eamail_scroll_step,
)
from original_eamail_row_text import original_eamail_text_rgba, original_eamail_row_text_layers
from original_game_host import OriginalGameTkHost
from original_management_canvas import build_management_canvas_frame
from original_management_presenter import OriginalManagementPresenter
from original_management_text import load_verified_management_text_resources
from test_original_eamail_live_host_route import ordinary_inbox, delivered, FixtureEAMBridge


ROOT = Path(__file__).resolve().parents[1] / 'original_assets' / 'source'


def inbox(count=1):
    session = ordinary_inbox()
    for i in range(count):
        delivered(session, 1000 + i, date(2000, 8, 1) + timedelta(days=i))
    presenter = OriginalManagementPresenter(session, bridge_factory=FixtureEAMBridge)
    presenter.source_accepted_pbg_direct_inbox_action()
    return session, presenter


def image(width, height, color):
    return EA444DecodedImage(width, height, bytes((*color, 255)) * (width * height), 0, 0)


def test_art():
    return OriginalEAMailRowArt(
        image(532, 18, (20, 40, 60)), image(532, 18, (60, 80, 100)),
        image(532, 187, (0, 0, 0)), load_verified_management_text_resources(ROOT),
        image(18, 12, (120, 180, 240)), image(72, 50, (30, 40, 50)),
    )


class OriginalInboxListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resources = load_verified_management_text_resources(ROOT)

    def toy_resources(self, pairs=None):
        font = self.resources.league_tables_row_font
        glyphs = []
        for byte in range(32, 256):
            adjustments = [0] * 224
            for (current, previous), amount in (pairs or {}).items():
                if byte == ord(current):
                    adjustments[ord(previous) - 32] = amount
            original = font.glyph_for_byte(byte)
            glyphs.append(replace(original, atlas_x=0, width=2,
                                  height=original.height if byte == 32 else 1,
                                  draw_y=original.draw_y if byte == 32 else 0,
                                  pair_adjustments=tuple(adjustments)))
        return replace(self.resources, league_tables_row_font=replace(
            font, glyphs=tuple(glyphs), atlas_alpha=b'\xff' * (font.atlas_width * font.atlas_height)))

    def raster(self, text, **kw):
        return original_eamail_text_rgba(text, kw.pop('resources', self.resources),
                                        width=kw.pop('width', 215), height=kw.pop('height', 16),
                                        tagged=kw.pop('tagged', False), selected=kw.pop('selected', False), **kw)

    def test_actual_glyphs_font_column_origins_clip_and_selected_colors(self):
        _, presenter = inbox()
        visible = presenter.snapshot().eamail
        serial = visible.native_rows[0].original_internal_node_serial
        layers = original_eamail_row_text_layers(visible, self.resources)
        selected = original_eamail_row_text_layers(visible, self.resources, selected_node_serial=serial)
        self.assertEqual([x[:4] for x in layers],
                         [(271, 178, 215, 16), (489, 178, 215, 16), (707, 178, 71, 16)])
        for layer, chosen in zip(layers, selected):
            self.assertEqual(len(layer[4]), layer[2] * layer[3] * 4)
            self.assertTrue(any(layer[4][3::4]))
            self.assertEqual(layer[4][3::4], chosen[4][3::4])
        def colors(rgba):
            return {tuple(rgba[i:i+3]) for i in range(0, len(rgba), 4) if rgba[i+3]}
        self.assertIn((120, 238, 130), colors(layers[0][4]))
        self.assertIn((11, 37, 13), colors(selected[0][4]))
        self.assertEqual(colors(layers[1][4]), {(255, 255, 255)})
        self.assertEqual(colors(selected[1][4]), {(0, 0, 0)})
        # Source font pen is top-left; glyph draw_y, not vertical centering.
        glyph = self.resources.league_tables_row_font.glyph_for_byte(ord('T'))
        plain = self.raster('Transfer List')
        self.assertFalse(any(plain[3:glyph.draw_y * 215 * 4:4]))

    def test_native_advance_is_after_draw_and_uses_current_previous_raw_byte(self):
        resource = self.toy_resources({('B', 'A'): 3, ('A', 'B'): -1})
        rgba = self.raster('ABC', resources=resource, width=20)
        # A draws x0, B x2, then B's pair(A)=+3 makes C draw x7, not x3.
        self.assertEqual([i for i in range(20) if rgba[i*4+3]], [0, 1, 2, 3, 7, 8])
        resource = self.toy_resources({('A', '>'): 3})
        rgba = self.raster('<T+P>AB<T->', resources=resource, tagged=True, width=20)
        self.assertEqual([i for i in range(20) if rgba[i*4+3]], [0, 1, 5, 6])

    def test_native_word_wrap_tag_reset_space_and_clip_not_ellipsis(self):
        resource = self.toy_resources()
        rgba = self.raster('A BBB', resources=resource, width=7, height=27)
        self.assertEqual([i for i in range(7) if rgba[i*4+3]], [0, 1])
        self.assertEqual([i for i in range(7) if rgba[(25*7+i)*4+3]], list(range(6)))
        self.assertFalse(any(rgba[7*4:25*7*4]))
        clipped = self.raster('A BBB', resources=resource, width=7, height=16)
        self.assertEqual(sum(bool(a) for a in clipped[3::4]), 2)
        # First untagged word is not wrapped; long tagged first word is.
        self.assertTrue(any(self.raster('AAAA', resources=resource, width=7)[3::4]))
        self.assertFalse(any(self.raster('<T+P>AAAA<T->', resources=resource,
                                        tagged=True, width=7)[3::4]))
        rgba = self.raster('<T+P>A<T-> @ <T+C>B Football Club<T->',
                           resources=resource, tagged=True, width=215)
        self.assertEqual(tuple(rgba[:3]), (120, 238, 130))
        self.assertEqual(tuple(rgba[4*4:4*4+3]), (255, 255, 255))  # @, tags have no width

    def test_unknown_tags_names_rectangles_and_owners_fail_closed(self):
        for text, tagged in (('<T+P>A<T->', False), ('<T+X>A<T->', True),
                             ('<F2>A', True), ('A\nB', False), ('', False)):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.raster(text, tagged=tagged)
        _, presenter = inbox()
        visible = presenter.snapshot().eamail
        row = visible.native_rows[0]
        unknown = replace(row.original_text_fields[0], source_verified_visible_text=None)
        legacy = replace(visible, native_rows=(replace(row, original_text_fields=(unknown, *row.original_text_fields[1:])),))
        self.assertEqual(len(original_eamail_row_text_layers(legacy, self.resources)), 2)
        bad = replace(row.original_text_fields[0], screen_rect=(0, 0, 215, 16))
        with self.assertRaises(ValueError):
            original_eamail_row_text_layers(replace(visible, native_rows=(replace(row,
                original_text_fields=(bad, *row.original_text_fields[1:])),)), self.resources)
        with self.assertRaises(ValueError):
            original_eamail_row_text_layers(visible, self.resources, selected_node_serial=-1)

    def test_status_and_scroll_geometry_limits_and_disabled_controls(self):
        _, presenter = inbox(12)
        visible = presenter.snapshot().eamail
        layers = original_eamail_initial_status_layers(visible, test_art())
        self.assertEqual(len(layers), 8)
        self.assertEqual(layers[0][:4], (248, 181, 18, 12))
        self.assertEqual(layers[-1][:4], (248, 321, 18, 12))
        self.assertEqual(original_eamail_scroll_at_point(212, 178), 19)
        self.assertEqual(original_eamail_scroll_at_point(229, 335), 21)
        for point in ((230, 178), (212, 203), (212, 310), (212, 336)):
            self.assertIsNone(original_eamail_scroll_at_point(*point))
        self.assertEqual(original_eamail_scroll_step(visible, 19), 0)
        self.assertEqual(original_eamail_scroll_step(visible, 21), 1)
        presenter.source_accepted_eamail_scroll(21)
        self.assertEqual(presenter.snapshot().eamail.original_scroll_offset, 1)
        for _ in range(10):
            presenter.source_accepted_eamail_scroll(21)
        self.assertEqual(presenter.eamail_scroll_offset, 4)
        self.assertEqual(presenter.source_accepted_eamail_scroll(21).eamail.original_scroll_offset, 4)
        self.assertEqual(presenter.source_accepted_eamail_scroll(19).eamail.original_scroll_offset, 3)
        with self.assertRaises(ValueError):
            presenter.source_accepted_eamail_scroll(20)
        # Distinct source atlas columns, not arbitrary recoloring.
        pixels = b''.join(bytes((x // 18, y // 25, 0, 255)) for y in range(50) for x in range(72))
        atlas = EA444DecodedImage(72, 50, pixels, 0, 0)
        art = replace(test_art(), scroll_arrows=atlas)
        layers = original_eamail_scroll_layers(visible, art)
        self.assertEqual([x[:4] for x in layers], [(212, 178, 18, 25), (212, 311, 18, 25)])
        self.assertNotEqual(layers[0][4], layers[1][4])
        self.assertNotEqual(layers[1][4], original_eamail_scroll_layers(visible, art, pressed_control_id=21)[1][4])

    def test_live_draw_press_selection_rebuild_release_without_data_or_rng_mutation(self):
        session, presenter = inbox(12)
        frame = build_management_canvas_frame(presenter)
        before = session.gameplay.state.original_delivered_mailboxes.delivered_for_manager(0)
        rng = (session.gameplay.state.rng.state, session.gameplay.match_rng.state)
        host = object.__new__(OriginalGameTkHost)
        host.pmenu_popup_active = False
        host.eamail_row_art = test_art()
        host.management_presenter = presenter
        host._eamail_selected_node_serial = frame.presentation.eamail.native_rows[0].original_internal_node_serial
        host._eamail_selected_row_token = object()
        host._eamail_scroll_pressed = None
        host.tk = SimpleNamespace(NW='nw')
        host._photo = lambda data: data
        draws = []
        host._create_native_image = lambda x, y, **kw: draws.append((x, y, kw['image']))
        self.assertEqual(host._draw_eamail_rows(frame), 42)  # 8*(grid+3text+icon)+2arrows
        self.assertTrue(all(data.startswith(b'\x89PNG') for _, _, data in draws))
        updates = []
        host.redraw = lambda: updates.append(presenter.eamail_scroll_offset)
        host._press_original_eamail_scroll(SimpleNamespace(x=213, y=179), frame)
        self.assertIsNotNone(host._eamail_selected_node_serial)  # disabled up does not clear
        self.assertTrue(host._press_original_eamail_scroll(SimpleNamespace(x=213, y=312), frame))
        self.assertIsNone(host._eamail_selected_node_serial)
        self.assertIsNone(host._eamail_selected_row_token)
        self.assertEqual(updates, [1])
        host._press_original_eamail_scroll(SimpleNamespace(x=213, y=312), frame)
        self.assertEqual(updates, [1])  # held/repeated press rejected, no invented timer
        host._original_match_input_owner = lambda: None
        host._normalize_pointer_event = lambda e: e
        host._release_original_squad_row = lambda e: False
        host.fixtures_pager_flags = {}
        host.pmatchinfo_script_pressed = None
        host.on_script_arrow_release(SimpleNamespace(x=213, y=312))
        self.assertIsNone(host._eamail_scroll_pressed)
        self.assertEqual(updates, [1, 1])
        self.assertEqual(session.gameplay.state.original_delivered_mailboxes.delivered_for_manager(0), before)
        self.assertEqual((session.gameplay.state.rng.state, session.gameplay.match_rng.state), rng)
        presenter.navigate(0x65)  # newly constructed native panel resets list offset
        self.assertEqual(presenter.eamail_scroll_offset, 0)

    def test_delivered_list_and_text_survive_real_save_codec_not_view_state(self):
        from internal_save import dumps_human_gameplay, loads_human_gameplay
        from test_original_eamail_live_user_bridge import OriginalManagerMailDatabase, coefficient_matrix
        from original_eamail_native_row_fields import build_selected_user_original_eam_source_rows
        session, presenter = inbox(10)
        before = presenter.snapshot().eamail
        saved = dumps_human_gameplay(session.gameplay)
        loaded = loads_human_gameplay(OriginalManagerMailDatabase(), coefficient_matrix(),
                                     coefficient_matrix(), saved)
        bridge = FixtureEAMBridge(loaded)
        # The synthetic DB omits names; this test supplies the SAME source names
        # as ordinary_inbox, without persisting presentation strings as game data.
        for index, club in tuple(loaded.state.clubs.items()):
            loaded.state.clubs[index] = SimpleNamespace(**vars(club), name=f'Full Club {index}', short_name=f'C{index}')
        after = build_selected_user_original_eam_source_rows(
            bridge, original_source_root=ROOT, filter_index=0, sort_index=None)
        self.assertEqual(before, after)
        self.assertEqual(original_eamail_row_text_layers(before, self.resources),
                         original_eamail_row_text_layers(after, self.resources))


class OriginalInboxNativeCalibrationTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE') and find_spec('capstone'),
                         'Licensed original and optional Capstone required')
    def test_actual_specialist_dispatch_colors_geometry_wrap_and_scroll(self):
        from capstone import Cs, CS_ARCH_X86, CS_MODE_32
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        self.assertEqual(struct.unpack('<II', pe.read(0x7BFAC8 + 0x98, 8)), (0x43B680, 0x43B6A0))
        self.assertEqual(struct.unpack('<f', pe.read(0x7D738C, 4))[0], 1.5)
        decoder = Cs(CS_ARCH_X86, CS_MODE_32)
        facts = (
            (0x471E09, 'mov', 'dword ptr [esi], 0x7bfac8'),
            (0x43B68A, 'mov', 'eax, dword ptr [ecx + 0x124]'),
            (0x43B691, 'mov', 'eax, dword ptr [ecx + 0x120]'),
            (0x43B6AA, 'mov', 'eax, dword ptr [ecx + 0x12c]'),
            (0x43B6B1, 'mov', 'eax, dword ptr [ecx + 0x128]'),
            (0x5D78C1, 'call', 'dword ptr [eax + 0x9c]'),
            (0x5D7936, 'fmul', 'dword ptr [0x7d738c]'),
            (0x5D795C, 'movsx', 'eax, byte ptr [ecx + edi - 1]'),
            (0x5D7557, 'call', '0x6570f0'),
            (0x5D7590, 'movsx', 'eax, byte ptr [esi + ebp + 0x20]'),
            (0x46F7EA, 'mov', 'dword ptr [edi + 0x18], 1'),
            (0x650042, 'call', '0x64ff30'),
            (0x47223C, 'lea', 'ecx, [esi + 0xf58]'),
        )
        for va, mnemonic, operands in facts:
            with self.subTest(va=hex(va)):
                instruction = next(decoder.disasm(pe.read(va, 15), va))
                self.assertEqual((instruction.mnemonic, instruction.op_str), (mnemonic, operands))

    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE'), 'Licensed original decoder tables required')
    def test_exact_original_art_font_loader_and_noninteractive_raster(self):
        art = load_verified_original_eamail_row_art(ROOT, os.environ['FM2001_ORIGINAL_EXE'])
        self.assertEqual((art.unread_icon.width, art.unread_icon.height), (18, 12))
        self.assertEqual((art.scroll_arrows.width, art.scroll_arrows.height), (72, 50))
        _, presenter = inbox()
        self.assertEqual(len(original_eamail_row_text_layers(presenter.snapshot().eamail, art.text_resources)), 3)


if __name__ == '__main__':
    unittest.main()
