import os
import tempfile
import unittest

import tkinter as tk

import compress_images


class MediaCompressorTests(unittest.TestCase):
    def test_get_output_path_keeps_image_extension_by_default(self):
        output = compress_images.get_output_path(r"C:\\images\\demo.jpg")
        expected = os.path.normpath(r"C:\images\demo_compressed.jpg")
        self.assertEqual(os.path.normpath(output), expected)

    def test_get_output_path_uses_svg_when_requested(self):
        output = compress_images.get_output_path("photo.png", convert_to_svg=True)
        self.assertEqual(output, os.path.normpath("photo_compressed.svg"))

    def test_get_output_path_uses_png_when_requested(self):
        output = compress_images.get_output_path("photo.svg", convert_to_png=True)
        self.assertEqual(output, os.path.normpath("photo_compressed.png"))

    def test_get_output_path_uses_converted_suffix_for_conversion_only(self):
        output = compress_images.get_output_path("photo.jpg", convert_to_png=True, convert_only=True)
        self.assertEqual(output, os.path.normpath("photo_converted.png"))

    def test_get_video_output_path_uses_mp4_for_video_files(self):
        output = compress_images.get_video_output_path(r"C:\\videos\\demo.mov")
        expected = os.path.normpath(r"C:\videos\demo_compressed.mp4")
        self.assertEqual(os.path.normpath(output), expected)

    def test_quality_presets_are_image_and_video_friendly(self):
        self.assertEqual(compress_images.QUALITY_PRESETS["Best quality"], 90)
        self.assertEqual(compress_images.QUALITY_PRESETS["Balanced"], 75)
        self.assertEqual(compress_images.QUALITY_PRESETS["Smaller file"], 60)
        self.assertEqual(compress_images.VIDEO_QUALITY_PRESETS["Best quality"], 23)
        self.assertEqual(compress_images.VIDEO_QUALITY_PRESETS["Balanced"], 28)
        self.assertEqual(compress_images.VIDEO_QUALITY_PRESETS["Smaller file"], 35)

    def test_is_image_file_and_is_video_file_recognize_common_extensions(self):
        self.assertTrue(compress_images.is_image_file("photo.jpg"))
        self.assertTrue(compress_images.is_image_file("photo.PNG"))
        self.assertTrue(compress_images.is_video_file("movie.mp4"))
        self.assertTrue(compress_images.is_video_file("movie.MOV"))
        self.assertFalse(compress_images.is_image_file("movie.mp4"))
        self.assertFalse(compress_images.is_video_file("image.jpg"))

    def test_validate_max_dimension_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            compress_images.validate_max_dimension("abc")
        with self.assertRaises(ValueError):
            compress_images.validate_max_dimension(0)

    def test_validate_video_resolution_accepts_supported_heights(self):
        self.assertEqual(compress_images.validate_video_resolution("1080"), 1080)
        self.assertEqual(compress_images.validate_video_resolution(720), 720)
        self.assertEqual(compress_images.validate_video_resolution("480"), 480)

    def test_validate_video_resolution_rejects_unsupported_values(self):
        with self.assertRaises(ValueError):
            compress_images.validate_video_resolution("360")

    def test_build_video_resolution_filter_limits_height(self):
        self.assertEqual(compress_images.build_video_resolution_filter(720), r"scale=-2:min(720\,ih)")

    def test_app_tracks_webp_conversion_option(self):
        root = tk.Tk()
        try:
            app = compress_images.MediaCompressorApp(root)
            self.assertIsNotNone(app.convert_to_webp_var)
            self.assertFalse(app.convert_to_webp_var.get())
            self.assertEqual(app.video_quality_var.get(), "1080")
            self.assertIsNotNone(app.convert_only_var)
            self.assertFalse(app.convert_only_var.get())
        finally:
            root.destroy()

    def test_compress_image_can_convert_to_webp(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "sample.png")
            with compress_images.Image.new("RGB", (60, 40), color="blue") as image:
                image.save(source_path)

            output_path = compress_images.compress_image(
                source_path,
                quality_name="Balanced",
                max_dimension=None,
                convert_to_webp=True,
            )

            self.assertTrue(os.path.exists(output_path))
            self.assertEqual(os.path.splitext(output_path)[1].lower(), ".webp")
            with compress_images.Image.open(output_path) as image:
                self.assertEqual(image.format, "WEBP")

    def test_conversion_only_preserves_dimensions_when_max_dimension_is_set(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "sample.jpg")
            with compress_images.Image.new("RGB", (120, 80), color="blue") as image:
                image.save(source_path)

            output_path = compress_images.compress_image(
                source_path,
                quality_name="Smaller file",
                max_dimension=20,
                convert_to_png=True,
                convert_only=True,
            )

            with compress_images.Image.open(output_path) as image:
                self.assertEqual(image.size, (120, 80))

    def test_conversion_only_png_is_not_optimized(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "sample.png")
            image = compress_images.Image.effect_noise((120, 80), 100).convert("RGB")
            image.save(source_path)
            image.close()

            converted_path = compress_images.compress_image(
                source_path,
                quality_name="Smaller file",
                convert_to_png=True,
                convert_only=True,
            )
            compressed_path = compress_images.compress_image(
                source_path,
                quality_name="Smaller file",
                convert_to_png=True,
            )

            self.assertGreater(os.path.getsize(converted_path), os.path.getsize(compressed_path))

    def test_compress_image_can_convert_to_svg(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "sample.png")
            with compress_images.Image.new("RGB", (60, 40), color="blue") as image:
                image.save(source_path)

            output_path = compress_images.compress_image(
                source_path,
                quality_name="Balanced",
                max_dimension=None,
                convert_to_svg=True,
            )

            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(output_path.endswith("_compressed.svg"))
            with open(output_path, encoding="utf-8") as svg_file:
                svg = svg_file.read()
            self.assertIn('<svg xmlns="http://www.w3.org/2000/svg"', svg)
            self.assertIn('width="60" height="40"', svg)
            self.assertIn("data:image/png;base64,", svg)

    def test_compress_image_can_convert_svg_to_png(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "sample.svg")
            with open(source_path, "w", encoding="utf-8") as svg_file:
                svg_file.write(
                    '<svg xmlns="http://www.w3.org/2000/svg" width="60" height="40">'
                    '<rect width="60" height="40" fill="blue" /></svg>'
                )

            output_path = compress_images.compress_image(
                source_path,
                quality_name="Balanced",
                max_dimension=None,
                convert_to_png=True,
            )

            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(output_path.endswith("_compressed.png"))
            with compress_images.Image.open(output_path) as image:
                self.assertEqual(image.format, "PNG")
                self.assertEqual(image.size, (60, 40))


if __name__ == "__main__":
    unittest.main()
