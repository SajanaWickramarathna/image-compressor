import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

QUALITY_PRESETS = {
    "Best quality": 23,
    "Balanced": 28,
    "Smaller file": 35,
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


def is_video_file(path):
    return os.path.splitext(path)[1].lower() in VIDEO_EXTENSIONS


def get_output_path(input_path, convert_to_webp=False):
    normalized_path = os.path.normpath(input_path)
    directory, filename = os.path.split(normalized_path)
    name, _ = os.path.splitext(filename)
    target_ext = ".mp4"
    return os.path.normpath(os.path.join(directory, f"{name}_compressed{target_ext}"))


def validate_max_dimension(max_dimension):
    if not max_dimension:
        return None

    try:
        max_dimension = int(max_dimension)
    except ValueError as exc:
        raise ValueError("Max dimension must be a number.") from exc

    if max_dimension <= 0:
        raise ValueError("Max dimension must be greater than 0.")

    return max_dimension


def build_video_filter(max_dimension):
    if not max_dimension:
        return None

    return (
        f"scale='min({max_dimension},iw)':min'({max_dimension},ih)':"
        "force_original_aspect_ratio=decrease"
    )


def compress_video(input_path, quality_name, max_dimension=None):
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg is not installed or not on PATH. Please install ffmpeg and try again.")

    quality = QUALITY_PRESETS[quality_name]
    max_dimension = validate_max_dimension(max_dimension)
    output_path = get_output_path(input_path)

    command = [ffmpeg_path, "-y", "-i", input_path]
    video_filter = build_video_filter(max_dimension)
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


class VideoCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Compressor")
        self.root.geometry("640x420")
        self.root.resizable(False, False)

        self.selected_files = []

        tk.Label(root, text="Select videos to compress", font=("Segoe UI", 12, "bold")).pack(pady=(18, 8))

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

        tk.Label(controls, text="Max dimension:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
        self.max_dimension = tk.StringVar(value="1280")
        tk.Entry(controls, textvariable=self.max_dimension, width=12).grid(row=1, column=1, sticky="w")

        tk.Button(root, text="Compress Videos", command=self.compress_all, width=22, height=2, bg="#2d7ff9", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=16)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, fg="#1f5f3a", font=("Segoe UI", 10, "bold")).pack()

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Choose videos",
            filetypes=[("Video files", "*.mp4 *.mkv *.mov *.avi *.wmv *.flv *.webm *.m4v *.mpeg *.mpg *.3gp *.3g2 *.ts")],
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
            messagebox.showwarning("No files", "Please select at least one video first.")
            return

        max_dimension = self.max_dimension.get().strip()
        try:
            validate_max_dimension(max_dimension)
        except ValueError as exc:
            messagebox.showerror("Invalid value", str(exc))
            return

        self.status_var.set("Compressing...")
        self.root.update()

        compressed_count = 0
        for path in self.selected_files:
            if not is_video_file(path):
                messagebox.showwarning("Unsupported file", f"{os.path.basename(path)} is not a supported video file.")
                self.status_var.set("Compression stopped due to an unsupported file.")
                return

            try:
                output_path = compress_video(
                    path,
                    quality_name=self.quality_var.get(),
                    max_dimension=max_dimension,
                )
                compressed_count += 1
                if output_path:
                    print(f"Compressed: {path} -> {output_path}")
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to process {os.path.basename(path)}: {exc}")
                self.status_var.set("Compression stopped due to an error.")
                return

        self.status_var.set(f"Done! {compressed_count} video(s) compressed.")
        messagebox.showinfo("Complete", f"Compressed {compressed_count} video(s).\nSaved as files ending with '_compressed'.")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCompressorApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nVideo compressor closed by user.")
        root.destroy()
