# Image Compressor

A simple desktop tool to reduce image file size while preserving quality as much as possible.

## Features
- Select one or more images
- Keeps high visual quality by default
- Offers quality presets: Best, Balanced, and Smaller file
- Saves compressed copies next to the original with a `_compressed` suffix
- Supports JPG, JPEG, PNG, and WEBP

## Run it

1. Open a terminal in this folder.
2. Install the dependency:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   python compress_images.py
   ```

## How it works
- JPEG and WEBP are saved with optimized compression and high quality settings.
- PNG files are optimized without unnecessary metadata.
- Large images can also be resized to a max dimension to reduce size further while keeping quality strong.

## Notes
- For true lossless compression, PNG is more limited than JPEG/WEBP.
- The best quality-preserving option is usually the "Best quality" preset.
