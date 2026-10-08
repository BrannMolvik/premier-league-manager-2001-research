from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from ea444_decoder import EA444DecodedImage
from original_management_next import (
    native_next_source_row, native_next_at_point, native_next_caption,
    native_next_bitmap_pixels, native_next_caption_pixels,
    load_verified_management_next_art, NEXT_RECT, NEXT_SOURCE_PATH,
)
from original_management_header import validate_management_header_font


class NativeNextControlTests(unittest.TestCase):
    def test_exact_source_row_priority_not_generic_bitmap_selector(self):
        for flags, row in ((0,3),(8,3),(16,3),(26,2),(10,1),(2,0),(0x22,0),(0x8002,0)):
            self.assertEqual(native_next_source_row(flags), row)
        for flags in (-1, 0x100000000, True, '2'):
            with self.assertRaises(ValueError): native_next_source_row(flags)

    def test_qualified_background_transform_and_half_open_edges(self):
        for point in ((700,0),(799,94),(773,62)): self.assertTrue(native_next_at_point(*point))
        for point in ((699,0),(800,0),(700,-1),(700,95)):
            self.assertFalse(native_next_at_point(*point))

    def test_caption_only_uses_retained_native_tomorrow_date(self):
        today=date(2000,8,1)
        for delta, caption in ((0,'NEXT'),(1,'MATCH'),(2,'NEXT')):
            self.assertEqual(native_next_caption(today,today+timedelta(days=delta)),caption)
        self.assertEqual(native_next_caption(today,None),'NEXT')
        with self.assertRaises(ValueError): native_next_caption(today,'2000-08-02')

    def test_four_state_crops_preserve_exact_pixels(self):
        rows = tuple(bytes((i, i, i, 255))*100*95 for i in range(4))
        art = EA444DecodedImage(100,380,b''.join(rows),0,0)
        for flags,row in ((2,0),(10,1),(18,2),(0,3)):
            self.assertEqual(native_next_bitmap_pixels(art,flags),(*NEXT_RECT,rows[row]))
        with self.assertRaises(ValueError): native_next_bitmap_pixels(SimpleNamespace(width=100,height=95,rgba=rows[0]),2)

    def test_exact_caption_font_and_clip_geometry(self):
        root=Path(__file__).resolve().parents[1]/'original_assets/source'
        font=validate_management_header_font(root)
        for text,match in (('NEXT',None),('MATCH',date(2000,8,2))):
            x,y,w,h,rgba=native_next_caption_pixels(font,date(2000,8,1),match)
            self.assertEqual(x,773-font.measure_text(text))
            self.assertEqual(y,77-font.native_line_height()//2)
            self.assertLessEqual(x+w,773);self.assertLessEqual(y+h,92)
            self.assertEqual(len(rgba),w*h*4)

    def test_corrupt_source_rejected_before_executable_read(self):
        with patch.object(Path,'read_bytes',return_value=b'not the original'):
            with self.assertRaisesRegex(ValueError,'identity'):
                load_verified_management_next_art('unused','never-read')

    def test_host_draws_bitmap_and_caption_with_retained_calendar(self):
        from original_game_host import OriginalGameTkHost
        from original_management_header import OriginalManagementHeaderResources
        root=Path(__file__).resolve().parents[1]/'original_assets/source'
        font=validate_management_header_font(root)
        host=OriginalGameTkHost.__new__(OriginalGameTkHost)
        host.management_next_art=EA444DecodedImage(100,380,bytes((1,2,3,255))*100*380,0,0)
        resources=OriginalManagementHeaderResources.__new__(OriginalManagementHeaderResources)
        object.__setattr__(resources,'font',font)
        host.management_header_resources=resources
        host.management_next_flags=10
        host.tk=SimpleNamespace(NW='nw')
        host.presenter=SimpleNamespace(session=SimpleNamespace(gameplay=SimpleNamespace(
            state=SimpleNamespace(calendar=SimpleNamespace(current_date=date(2000,8,1))))))
        draws=[]
        host._rgba_photo=lambda w,h,pixels: (w,h,pixels)
        host._create_native_image=lambda x,y,**kwargs: draws.append((x,y,kwargs))
        frame=SimpleNamespace(presentation=SimpleNamespace(header_match=SimpleNamespace(
            scheduled_date=date(2000,8,2))))
        self.assertEqual(host._draw_management_next_control(frame),2)
        self.assertEqual(draws[0][:2],(700,0))
        self.assertEqual(draws[0][2]['image'][:2],(100,95))
        self.assertEqual(draws[1][0],773-font.measure_text('MATCH'))
        host.management_next_art=None
        self.assertEqual(host._draw_management_next_control(frame),0)


if __name__=='__main__': unittest.main()
