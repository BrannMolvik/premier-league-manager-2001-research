"""Bounded original ID16 interaction; noninteractive, no RNG/preview claims."""
from dataclasses import replace
from importlib.util import find_spec
import os
from pathlib import Path
import struct
from types import SimpleNamespace
import unittest

from original_eamail_live_canvas import original_eamail_received_hit, original_eamail_received_layers
from original_game_host import OriginalGameTkHost
from original_management_canvas import build_management_canvas_frame
from test_original_eamail_list import inbox, test_art, image


class ReceivedControlTests(unittest.TestCase):
    def test_geometry_states_real_sort_and_scroll(self):
        _, presenter = inbox(12)
        self.assertTrue(original_eamail_received_hit(705, 149))
        for point in ((704, 149), (778, 149), (705, 169)):
            self.assertFalse(original_eamail_received_hit(*point))
        art = replace(test_art(), received_header=image(73, 60, (40, 60, 90)))
        layers = [original_eamail_received_layers(art, selected=s, hovered=h)
                  for s, h in ((False, False), (False, True), (True, True))]
        self.assertEqual([x[0][:4] for x in layers], [(705, 149, 73, 20)] * 3)
        self.assertNotEqual(layers[0][1][-1], layers[2][1][-1])  # white vs black
        colored = replace(art, received_header=replace(art.received_header,
            rgba=b''.join(bytes((v, 0, 0, 255)) * (73 * 20) for v in (10, 20, 30))))
        crops = [original_eamail_received_layers(colored, selected=s, hovered=h)[0][-1]
                 for s, h in ((False, False), (False, True), (True, False))]
        self.assertEqual(len(set(crops)), 3)
        self.assertEqual(crops[2], original_eamail_received_layers(colored, selected=True, hovered=True)[0][-1])
        host = object.__new__(OriginalGameTkHost)
        host.pmenu_popup_active = False
        host.management_presenter = presenter
        host.eamail_row_art = art
        host._eamail_selected_node_serial = 99
        host._eamail_selected_row_token = object()
        redraws = []
        host.redraw = lambda: redraws.append(True)
        frame = build_management_canvas_frame(presenter)
        self.assertTrue(host._press_original_eamail_received(SimpleNamespace(x=706, y=150), frame))
        self.assertEqual(presenter.eamail_sort_index, 4)
        self.assertIsNone(host._eamail_selected_node_serial)
        rows = presenter.snapshot().eamail.native_rows
        self.assertGreater(rows[0].qualified_record_date, rows[-1].qualified_record_date)
        presenter.source_accepted_eamail_scroll(21)
        self.assertEqual(presenter.eamail_sort_index, 4)
        self.assertEqual(presenter.eamail_scroll_offset, 1)
        host._eamail_selected_node_serial = 42
        host._press_original_eamail_received(SimpleNamespace(x=706, y=150), frame)
        self.assertEqual(host._eamail_selected_node_serial, 42)
        self.assertEqual(len(redraws), 1)
        presenter.navigate(0x65)
        self.assertIsNone(presenter.eamail_sort_index)
        self.assertEqual(presenter.eamail_scroll_offset, 0)

    def test_popup_and_unqualified_art_do_not_accept(self):
        _, presenter = inbox()
        host = object.__new__(OriginalGameTkHost)
        host.pmenu_popup_active = True
        self.assertFalse(host._press_original_eamail_received(SimpleNamespace(x=706, y=150), build_management_canvas_frame(presenter)))
        host.pmenu_popup_active = False
        host.eamail_row_art = test_art()
        self.assertFalse(host._press_original_eamail_received(SimpleNamespace(x=706, y=150), build_management_canvas_frame(presenter)))

    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE') and find_spec('capstone'), 'licensed static original unavailable')
    def test_final_native_dispatch_resource_and_geometry(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        self.assertEqual(struct.unpack('<I', pe.read(0x7C2B04 + 0x98, 4))[0], 0x474F80)
        self.assertEqual(struct.unpack('<I', pe.read(0x7C2B04 + 0x6C, 4))[0], 0x652CF0)
        self.assertEqual(pe.read(0x46F387, 7), bytes.fromhex('6A0168C1020000'))
        self.assertIn(b'recieved_tog.444', pe.read(0x836158, 100))
        self.assertEqual(pe.read(0x47236C + 15, 1), b'\x01')
        self.assertEqual(struct.unpack('<I', pe.read(0x472354 + 4, 4))[0], 0x4721F2)
