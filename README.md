# Media Compressor

A simple desktop tool for reducing image and video file size while keeping quality as high as possible.

## Features
- Select one or more images or videos
- Convert images to PNG, WebP, or self-contained SVG files
- Uses FFmpeg and H.264 encoding
- Offers image quality presets and asks for video quality: 1080p, 720p, or 480p
- Saves compressed copies next to the original with a `_compressed` suffix
- Supports common video formats such as MP4, MKV, MOV, AVI, WEBM, and more

## Requirements

You must install FFmpeg before running the app.

### Windows
1. Download a FFmpeg build from: https://www.gyan.dev/ffmpeg/builds/
2. Extract it to a folder such as:
   `C:\Users\A S U S\Downloads\ffmpeg-9.0.1-essentials_build`
3. Add the `bin` folder to your system PATH:
   `C:\Users\A S U S\Downloads\ffmpeg-9.0.1-essentials_build\bin`
4. Restart PowerShell or VS Code after updating PATH.

### macOS
```bash
brew install ffmpeg
```

### Ubuntu / Debian
```bash
sudo apt install ffmpeg
```

## Check FFmpeg is available

Open PowerShell and run:

```powershell
ffmpeg -version
```

If it prints the FFmpeg version, the tool is installed correctly.

## Setup the project

From the project folder:

```bash
pip install -r requirements.txt
```

## Run the app

```bash
python compress_images.py
```

## How to use
1. Click `Browse`
2. Select one or more image or video files
3. Choose an image quality preset; for videos, choose 1080, 720, or 480 when prompted
4. Optionally set a maximum dimension for resizing
5. For images, choose `Convert images to PNG`, `Convert images to WebP`, or `Convert images to SVG`
6. Select `Convert only (do not resize or reduce quality)` to change format without resizing or reducing quality
7. Click `Compress Media`
8. The app saves compressed files next to the original with `_compressed` added to the name, or `_converted` for conversion-only files

## How it works
- Video quality is controlled with FFmpeg CRF values and the selected output height.
- The app encodes using H.264 and AAC audio.
- Output is saved as MP4 for compatibility.
- SVG output embeds a compressed PNG inside an SVG wrapper, preserving the source image reliably while allowing the SVG canvas to scale.
- A max dimension may reduce file size further by shrinking larger videos.

## Notes
- Lower CRF values keep more quality but produce larger files.
- The "Best quality" preset is best for important footage.
- The "Smaller file" preset is better when you want faster uploads or smaller storage use.
- If `ffmpeg` is not found, the app will show an error until FFmpeg is installed and available in PATH.
