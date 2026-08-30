import os
import unittest

import compress_images


class VideoCompressorTests(unittest.TestCase):
    def test_get_output_path_uses_mp4_for_video_files(self):
        output = compress_images.get_output_path(r"C:\\videos\\demo.mov")
        expected = os.path.normpath(r"C:\videos\demo_compressed.mp4")
        self.assertEqual(os.path.normpath(output), expected)

    def test_quality_presets_are_video_friendly(self):
        self.assertEqual(compress_images.QUALITY_PRESETS["Best quality"], 23)
        self.assertEqual(compress_images.QUALITY_PRESETS["Balanced"], 28)
        self.assertEqual(compress_images.QUALITY_PRESETS["Smaller file"], 35)

    def test_is_video_file_recognizes_common_extensions(self):
        self.assertTrue(compress_images.is_video_file("movie.mp4"))
        self.assertTrue(compress_images.is_video_file("movie.MOV"))
        self.assertFalse(compress_images.is_video_file("image.jpg"))


if __name__ == "__main__":
    unittest.main()
