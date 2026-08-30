# Video Compressor

A simple desktop tool to reduce video file size while keeping quality as high as possible.

## Features
- Select one or more videos
- Uses FFmpeg's efficient H.264 encoding
- Offers quality presets: Best, Balanced, and Smaller file
- Saves compressed copies next to the original with a `_compressed` suffix
- Supports common video formats such as MP4, MKV, MOV, AVI, WEBM, and more

## Requirements

Install FFmpeg on your system before running the app.

- Windows: https://www.ffmpeg.org/download.html
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`

Then install Python dependencies:

```bash
pip install -r requirements.txt
```

## Run it

```bash
python compress_images.py
```

## How it works
- Video quality is controlled with FFmpeg CRF values.
- The app uses H.264 with AAC audio and outputs MP4 files for compatibility.
- A max dimension can be applied to reduce file size further by scaling down the video.

## Notes
- Lower CRF values keep more quality but produce larger files.
- The "Best quality" preset is usually best for important footage, while "Smaller file" is better for sharing.
