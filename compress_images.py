import base64
import io
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image

QUALITY_PRESETS = {
    "Best quality": 90,
    "Balanced": 75,
    "Smaller file": 60,
}

VIDEO_QUALITY_PRESETS = {
    "Best quality": 23,
    "Balanced": 28,
    "Smaller file": 35,
}

VIDEO_RESOLUTION_PRESETS = {
    "1080": 1080,
    "720": 720,
    "480": 480,
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".svg",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".mpeg",
    ".mpg",
    ".3gp",
    ".3g2",
    ".ts",
}


def is_image_file(path):
    return os.path.splitext(path)[1].lower() in IMAGE_EXTENSIONS


def is_video_file(path):
    return os.path.splitext(path)[1].lower() in VIDEO_EXTENSIONS


def get_output_path(input_path, convert_to_webp=False, convert_to_svg=False, convert_to_png=False, convert_only=False):
    normalized_path = os.path.normpath(input_path)
    directory, filename = os.path.split(normalized_path)
    name, ext = os.path.splitext(filename)

    if convert_to_png:
        target_ext = ".png"
    elif convert_to_svg:
        target_ext = ".svg"
    elif convert_to_webp:
        target_ext = ".webp"
    elif ext.lower() in {".jpg", ".jpeg"}:
        target_ext = ".jpg"
    elif ext:
        target_ext = ext.lower()
    else:
        target_ext = ".jpg"

    suffix = "_converted" if convert_only else "_compressed"
    return os.path.normpath(os.path.join(directory, f"{name}{suffix}{target_ext}"))


def get_video_output_path(input_path):
    normalized_path = os.path.normpath(input_path)
    directory, filename = os.path.split(normalized_path)
    name, _ = os.path.splitext(filename)
    return os.path.normpath(os.path.join(directory, f"{name}_compressed.mp4"))


def validate_max_dimension(max_dimension):
    if max_dimension in (None, ""):
        return None

    try:
        max_dimension = int(max_dimension)
    except (TypeError, ValueError) as exc:
        raise ValueError("Max dimension must be a number.") from exc

    if max_dimension <= 0:
        raise ValueError("Max dimension must be greater than 0.")

    return max_dimension


def validate_video_resolution(video_resolution):
    if video_resolution in VIDEO_RESOLUTION_PRESETS:
        return VIDEO_RESOLUTION_PRESETS[video_resolution]

    try:
        video_resolution = int(video_resolution)
    except (TypeError, ValueError) as exc:
        raise ValueError("Video quality must be 1080, 720, or 480.") from exc

    if video_resolution not in VIDEO_RESOLUTION_PRESETS.values():
        raise ValueError("Video quality must be 1080, 720, or 480.")

    return video_resolution


def build_video_filter(max_dimension):
    if not max_dimension:
        return None
    return (
        f"scale='min({max_dimension},iw)':min'({max_dimension},ih)':"
        "force_original_aspect_ratio=decrease"
    )


def build_video_resolution_filter(video_height):
    return f"scale=-2:min({video_height}\\,ih)"


def compress_image(
    input_path,
    quality_name,
    max_dimension=None,
    convert_to_webp=False,
    convert_to_svg=False,
    convert_to_png=False,
    convert_only=False,
):
    quality = 100 if convert_only else QUALITY_PRESETS[quality_name]
    max_dimension = None if convert_only else validate_max_dimension(max_dimension)
    output_path = get_output_path(
        input_path,
        convert_to_webp=convert_to_webp,
        convert_to_svg=convert_to_svg,
        convert_to_png=convert_to_png,
        convert_only=convert_only,
    )

    if os.path.splitext(input_path)[1].lower() == ".svg":
        try:
            import resvg
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "SVG support requires resvg. Install dependencies with 'python -m pip install -r requirements.txt'."
            ) from exc

        with open(input_path, "r", encoding="utf-8") as svg_file:
            svg_data = svg_file.read()
        tree = resvg.usvg.Tree.from_str(svg_data, resvg.usvg.Options.default())
        image_data = resvg.render(tree, (1, 0, 0, 1, 0, 0))
        image_context = Image.open(io.BytesIO(image_data))
    else:
        image_context = Image.open(input_path)

    with image_context as image:
        image_copy = image.copy()

        if max_dimension:
            width, height = image_copy.size
            if width > max_dimension or height > max_dimension:
                scale = min(max_dimension / width, max_dimension / height)
                new_size = (
                    max(max(1, int(width * scale)), 1),
                    max(max(1, int(height * scale)), 1),
                )
                image_copy = image_copy.resize(new_size, Image.Resampling.LANCZOS)

        output_format = output_path.rsplit(".", 1)[-1].lower()
        if output_format == "svg":
            png_buffer = io.BytesIO()
            png_compression = 0 if convert_only else 9
            image_copy.save(png_buffer, format="PNG", optimize=False, compress_level=png_compression)
            encoded_image = base64.b64encode(png_buffer.getvalue()).decode("ascii")
            width, height = image_copy.size
            svg = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
                f'viewBox="0 0 {width} {height}">\n'
                f'  <image width="{width}" height="{height}" href="data:image/png;base64,{encoded_image}" />\n'
                "</svg>\n"
            )
            with open(output_path, "w", encoding="utf-8") as svg_file:
                svg_file.write(svg)
        elif output_format in {"jpg", "jpeg"}:
            image_copy = image_copy.convert("RGB")
            image_copy.save(output_path, format="JPEG", quality=quality, optimize=not convert_only)
        elif output_format == "png":
            png_compression = 0 if convert_only else 9
            image_copy.save(output_path, format="PNG", optimize=False, compress_level=png_compression)
        elif output_format == "webp":
            if convert_only:
                image_copy.save(output_path, format="WEBP", lossless=True, method=6)
            else:
                image_copy.save(output_path, format="WEBP", quality=quality, method=6)
        else:
            image_copy.save(output_path, format=image.format or "PNG", quality=quality)

    return output_path


def compress_video(input_path, quality_name, max_dimension=None, video_height=None):
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg is not installed or not on PATH. Please install ffmpeg and try again.")

    quality = VIDEO_QUALITY_PRESETS[quality_name]
    max_dimension = validate_max_dimension(max_dimension)
    if video_height is not None:
        video_height = validate_video_resolution(video_height)
    output_path = get_video_output_path(input_path)

    command = [ffmpeg_path, "-y", "-i", input_path]
    video_filter = (
        build_video_resolution_filter(video_height)
        if video_height is not None
        else build_video_filter(max_dimension)
    )
    if video_filter:
        command.extend(["-vf", video_filter])

    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            str(quality),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            output_path,
        ]
    )

    subprocess.run(command, check=True, capture_output=True, text=True)
    return output_path


class MediaCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Compressor")
        self.root.geometry("700x480")
        self.root.resizable(False, False)

        self.selected_files = []

        tk.Label(root, text="Select images or videos to compress", font=("Segoe UI", 12, "bold")).pack(pady=(18, 8))

        row = tk.Frame(root)
        row.pack(fill="x", padx=18, pady=6)
        self.file_label = tk.Label(row, text="No files selected", anchor="w", justify="left")
        self.file_label.pack(side="left", expand=True, fill="x")

        tk.Button(row, text="Browse", command=self.select_files, width=12).pack(side="right")

        controls = tk.Frame(root)
        controls.pack(fill="x", padx=18, pady=10)

        tk.Label(controls, text="Quality:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
        self.quality_var = tk.StringVar(value="Best quality")
        quality_menu = tk.OptionMenu(controls, self.quality_var, *QUALITY_PRESETS.keys())
        quality_menu.grid(row=0, column=1, sticky="w")

        tk.Label(controls, text="Video quality:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
        self.video_quality_var = tk.StringVar(value="1080")
        video_quality_menu = tk.OptionMenu(controls, self.video_quality_var, *VIDEO_RESOLUTION_PRESETS.keys())
        video_quality_menu.grid(row=1, column=1, sticky="w")

        tk.Label(controls, text="Max dimension:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=6)
        self.max_dimension = tk.StringVar(value="1920")
        tk.Entry(controls, textvariable=self.max_dimension, width=12).grid(row=2, column=1, sticky="w")

        self.convert_to_webp_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            controls,
            text="Convert images to WebP",
            variable=self.convert_to_webp_var,
            onvalue=True,
            offvalue=False,
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 8))

        self.convert_to_svg_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            controls,
            text="Convert images to SVG",
            variable=self.convert_to_svg_var,
            onvalue=True,
            offvalue=False,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.convert_to_png_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            controls,
            text="Convert images to PNG",
            variable=self.convert_to_png_var,
            onvalue=True,
            offvalue=False,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.convert_only_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            controls,
            text="Convert only (do not resize or reduce quality)",
            variable=self.convert_only_var,
            onvalue=True,
            offvalue=False,
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 8))

        tk.Button(root, text="Compress Media", command=self.compress_all, width=22, height=2, bg="#2d7ff9", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=16)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, fg="#1f5f3a", font=("Segoe UI", 10, "bold")).pack()

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Choose images or videos",
            filetypes=[
                ("Media files", "*.jpg *.jpeg *.png *.webp *.bmp *.gif *.tif *.tiff *.svg *.mp4 *.mkv *.mov *.avi *.wmv *.flv *.webm *.m4v *.mpeg *.mpg *.3gp *.3g2 *.ts")
            ],
        )
        if not files:
            return

        self.selected_files = list(files)
        self.file_label.config(text="\n".join(os.path.basename(path) for path in self.selected_files[:5]))
        if len(self.selected_files) > 5:
            self.file_label.config(text=self.file_label.cget("text") + f" ... (+{len(self.selected_files)-5} more)")
        self.status_var.set(f"{len(self.selected_files)} file(s) selected")

    def compress_all(self):
        if not self.selected_files:
            messagebox.showwarning("No files", "Please select at least one file first.")
            return

        max_dimension = self.max_dimension.get().strip()
        try:
            validate_max_dimension(max_dimension)
        except ValueError as exc:
            messagebox.showerror("Invalid value", str(exc))
            return

        video_height = validate_video_resolution(self.video_quality_var.get())

        self.status_var.set("Compressing...")
        self.root.update()

        compressed_count = 0
        convert_to_webp = self.convert_to_webp_var.get()
        convert_to_svg = self.convert_to_svg_var.get()
        convert_to_png = self.convert_to_png_var.get()
        convert_only = self.convert_only_var.get()
        for path in self.selected_files:
            if is_image_file(path):
                try:
                    output_path = compress_image(
                        path,
                        quality_name=self.quality_var.get(),
                        max_dimension=max_dimension,
                        convert_to_webp=convert_to_webp,
                        convert_to_svg=convert_to_svg,
                        convert_to_png=convert_to_png,
                        convert_only=convert_only,
                    )
                    compressed_count += 1
                    if output_path:
                        print(f"Compressed image: {path} -> {output_path}")
                except Exception as exc:
                    messagebox.showerror("Error", f"Failed to process {os.path.basename(path)}: {exc}")
                    self.status_var.set("Compression stopped due to an error.")
                    return
            elif is_video_file(path):
                try:
                    output_path = compress_video(
                        path,
                        quality_name=self.quality_var.get(),
                        max_dimension=max_dimension,
                        video_height=video_height,
                    )
                    compressed_count += 1
                    if output_path:
                        print(f"Compressed video: {path} -> {output_path}")
                except Exception as exc:
                    messagebox.showerror("Error", f"Failed to process {os.path.basename(path)}: {exc}")
                    self.status_var.set("Compression stopped due to an error.")
                    return
            else:
                messagebox.showwarning("Unsupported file", f"{os.path.basename(path)} is not a supported image or video file.")
                self.status_var.set("Compression stopped due to an unsupported file.")
                return

        self.status_var.set(f"Done! {compressed_count} file(s) compressed.")
        messagebox.showinfo("Complete", f"Compressed {compressed_count} file(s).\nSaved as files ending with '_compressed'.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MediaCompressorApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nMedia compressor closed by user.")
        root.destroy()
