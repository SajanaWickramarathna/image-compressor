import os
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageOps

QUALITY_PRESETS = {
    "Best quality": 92,
    "Balanced": 80,
    "Smaller file": 68,
}


def get_output_path(input_path, convert_to_webp=False):
    directory, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)
    target_ext = ".webp" if convert_to_webp else ext
    return os.path.join(directory, f"{name}_compressed{target_ext}")


def resize_if_needed(image, max_dimension):
    if not max_dimension:
        return image

    try:
        max_dimension = int(max_dimension)
    except ValueError:
        raise ValueError("Max dimension must be a number.")

    if max_dimension <= 0:
        raise ValueError("Max dimension must be greater than 0.")

    width, height = image.size
    if width > max_dimension or height > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    return image


def compress_image(input_path, quality_name, max_dimension=None, convert_to_webp=False):
    quality = QUALITY_PRESETS[quality_name]
    original = Image.open(input_path)
    image = ImageOps.exif_transpose(original)

    if image.mode in ("RGBA", "LA"):
        image = image.convert("RGBA")
    elif image.mode not in ("RGB", "L", "P"):
        image = image.convert("RGB")

    image = resize_if_needed(image, max_dimension)

    output_path = get_output_path(input_path, convert_to_webp=convert_to_webp)

    if convert_to_webp:
        image = image.convert("RGB")
        image.save(output_path, format="WEBP", quality=quality, method=6, optimize=True)
        return output_path

    original_ext = os.path.splitext(input_path)[1].lower()

    if original_ext in (".png", ".PNG"):
        if image.mode == "RGBA":
            image.save(output_path, format="PNG", optimize=True)
        else:
            image.save(output_path, format="PNG", optimize=True)
        return output_path

    if original_ext in (".jpg", ".jpeg", ".JPG", ".JPEG"):
        image = image.convert("RGB")
        image.save(output_path, format="JPEG", quality=quality, optimize=True, progressive=True)
        return output_path

    image.save(output_path, format="JPEG", quality=quality, optimize=True, progressive=True)
    return output_path


class ImageCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Compressor")
        self.root.geometry("640x420")
        self.root.resizable(False, False)

        self.selected_files = []

        tk.Label(root, text="Select images to compress", font=("Segoe UI", 12, "bold")).pack(pady=(18, 8))

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
        self.max_dimension = tk.StringVar(value="2000")
        tk.Entry(controls, textvariable=self.max_dimension, width=12).grid(row=1, column=1, sticky="w")

        self.webp_var = tk.BooleanVar(value=False)
        tk.Checkbutton(controls, text="Convert to WebP for smaller files", variable=self.webp_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))

        tk.Button(root, text="Compress Images", command=self.compress_all, width=22, height=2, bg="#2d7ff9", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=16)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, fg="#1f5f3a", font=("Segoe UI", 10, "bold")).pack()

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Choose images",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff")],
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
            messagebox.showwarning("No files", "Please select at least one image first.")
            return

        max_dimension = self.max_dimension.get().strip()
        try:
            if max_dimension:
                int(max_dimension)
        except ValueError:
            messagebox.showerror("Invalid value", "Max dimension must be a number.")
            return

        self.status_var.set("Compressing...")
        self.root.update()

        compressed_count = 0
        for path in self.selected_files:
            try:
                output_path = compress_image(
                    path,
                    quality_name=self.quality_var.get(),
                    max_dimension=max_dimension,
                    convert_to_webp=self.webp_var.get(),
                )
                compressed_count += 1
                if output_path:
                    print(f"Compressed: {path} -> {output_path}")
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to process {os.path.basename(path)}: {exc}")
                self.status_var.set("Compression stopped due to an error.")
                return

        self.status_var.set(f"Done! {compressed_count} image(s) compressed.")
        messagebox.showinfo("Complete", f"Compressed {compressed_count} image(s).\nSaved as files ending with '_compressed'.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCompressorApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nImage compressor closed by user.")
        root.destroy()
