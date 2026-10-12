"""Authentic SupportStart frame sources: exact pixel slicing, no fake hitbox."""
import unittest
from ea444_decoder import EA444DecodedImage
from original_supportstart_art import (
    ORIGINAL_SUPPORTSTART_ART_SPECS, OriginalSupportStartArtError
)
from original_supportstart_raster_inputs import (
    assemble_source_supportstart_rasters, source_rgba_crop,
)


def img(width,height):
    # Local test pixels deliberately nonuniform; source frame slicing must
    # retain exact row-major source pixels including transparent alpha.
    rgba=bytes(v for row in range(height) for col in range(width)
               for v in ((col*3)%256,(row*5)%256,(col+row)%256,
                         (0 if (col+row)%7==0 else 255)))
    return EA444DecodedImage(width,height,rgba,0,sum(rgba[i+3]==0 for i in range(0,len(rgba),4)))


class SourceSupportStartRasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.images={spec.relative_source:img(spec.width,spec.height)
                    for spec in ORIGINAL_SUPPORTSTART_ART_SPECS}

    def test_native_all_six_original_frame_shapes(self):
        result=assemble_source_supportstart_rasters(self.images)
        self.assertEqual((result.background.width,result.background.height),(760,500))
        self.assertEqual(len(result.row_bar_frames),4)
        self.assertEqual([(v.width,v.height) for v in result.row_bar_frames],[(306,17)]*4)
        self.assertEqual(len(result.row_animation_frames),23)
        self.assertEqual([(v.width,v.height) for v in result.row_animation_frames],[(17,37)]*23)
        self.assertEqual(len(result.exit_button_frames),3)
        self.assertEqual(len(result.apply_button_frames),3)
        self.assertEqual([(v.width,v.height) for v in result.star_rating_crops],
                         [(15,10),(30,10),(45,10),(60,10),(75,10)])

    def test_native_rgba_pixels_and_alpha_are_exact_source_crops(self):
        a=img(4,4)
        c=source_rgba_crop(a,x=1,y=1,width=2,height=2)
        expected=(a.rgba[(1*4+1)*4:(1*4+3)*4]
                  + a.rgba[(2*4+1)*4:(2*4+3)*4])
        self.assertEqual(c.rgba,expected)
        self.assertEqual(c.transparent_pixels,
                         sum(expected[i+3]==0 for i in range(0,len(expected),4)))
        result=assemble_source_supportstart_rasters(self.images)
        source=self.images["FM2001_Art/Generic/user_entry/text_bars.444"]
        self.assertEqual(result.row_bar_frames[3].rgba[:8],
                         source.rgba[(51*306)*4:(51*306)*4+8])
        self.assertEqual(result.row_animation_frames[-1].rgba[-8:],
                         self.images["FM2001_Art/Generic/GenericButtonsAndBars/user_entry_anim.444"].rgba[-8:])

    def test_strict_native_atlas_and_crop_bounds(self):
        for kwargs in (dict(x=-1,y=0,width=1,height=1),
                       dict(x=0,y=0,width=5,height=1),
                       dict(x=0,y=4,width=1,height=1),
                       dict(x=0,y=0,width=0,height=1),
                       dict(x=True,y=0,width=1,height=1)):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(OriginalSupportStartArtError):
                    source_rgba_crop(img(4,4),**kwargs)
        with self.assertRaises(OriginalSupportStartArtError):
            assemble_source_supportstart_rasters({})
        tampered=dict(self.images)
        tampered["FM2001_Art/Support/stars.444"]=img(75,9)
        with self.assertRaisesRegex(OriginalSupportStartArtError,"geometry"):
            assemble_source_supportstart_rasters(tampered)


if __name__=="__main__":
    unittest.main()
