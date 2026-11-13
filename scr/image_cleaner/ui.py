import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
from image_cleaner.engine import convert_to_black, convert_to_grayscale, remove_corner_background, flatten_for_jpeg
from image_cleaner.batch import process_batch

class App:
    def __init__(self, root):
        self.root = root
        root.title("Image Cleaner")
        root.geometry("980x680")
        root.minsize(740, 500)
        self.original = self.current = None
        self.history, self.index = [], -1
        self.photo = None
        self.build()

    def build(self):
        header = ttk.Frame(self.root, padding=10); header.pack(fill="x")
        ttk.Label(header, text="IMAGE CLEANER", font=("TkDefaultFont", 18, "bold")).pack(side="left")
        ttk.Label(header, text="Offline-first image tools").pack(side="left", padx=15)
        bar = ttk.Frame(self.root, padding=(10, 0)); bar.pack(fill="x")
        for label, cmd in [("Open", self.open), ("Save As", self.save), ("Undo", self.undo),
                           ("Redo", self.redo), ("Reset", self.reset), ("Batch", self.batch)]:
            ttk.Button(bar, text=label, command=cmd).pack(side="left", padx=3, pady=5)
        pane = ttk.Panedwindow(self.root, orient="horizontal"); pane.pack(fill="both", expand=True, padx=10, pady=8)
        tools = ttk.Frame(pane, padding=10); right = ttk.Frame(pane, padding=8)
        pane.add(tools, weight=0); pane.add(right, weight=1)
        ttk.Label(tools, text="EDIT TOOLS", font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=5)
        ttk.Label(tools, text="Black/white threshold").pack(anchor="w")
        self.threshold = tk.IntVar(value=128)
        ttk.Scale(tools, from_=0, to=255, variable=self.threshold).pack(fill="x", pady=4)
        ttk.Button(tools, text="Convert to Pure Black & White", command=self.black).pack(fill="x", pady=4)
        ttk.Button(tools, text="Convert to Grayscale", command=self.gray).pack(fill="x", pady=4)
        ttk.Separator(tools).pack(fill="x", pady=10)
        ttk.Label(tools, text="Background removal", font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        ttk.Label(tools, text="Removes connected pixels similar to the top-left corner. Best for flat backgrounds.",
                  wraplength=190).pack(anchor="w", pady=5)
        self.tolerance = tk.IntVar(value=30)
        ttk.Label(tools, text="Color tolerance").pack(anchor="w")
        ttk.Scale(tools, from_=0, to=100, variable=self.tolerance).pack(fill="x", pady=4)
        ttk.Button(tools, text="Remove Corner Background", command=self.background).pack(fill="x", pady=4)
        ttk.Separator(tools).pack(fill="x", pady=10)
        ttk.Label(tools, text="Your original is kept unchanged. Review the preview before saving.",
                  wraplength=190).pack(anchor="w")
        ttk.Label(right, text="PREVIEW", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
        self.canvas = tk.Canvas(right, bg="#333333", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, pady=6)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        self.status = tk.StringVar(value="Open an image. Files stay on this computer; no upload.")
        ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w", padding=5).pack(fill="x")

    def need(self):
        if self.current is None:
            messagebox.showinfo("Image Cleaner", "Open an image first.")
            return False
        return True

    def open(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp")])
        if not path: return
        try:
            with Image.open(path) as im:
                im.seek(0); loaded = im.convert("RGBA")
            self.original = loaded.copy(); self.current = loaded.copy()
            self.history = [loaded.copy()]; self.index = 0
            self.status.set("{} — {} × {} px".format(os.path.basename(path), loaded.width, loaded.height))
            self.draw()
        except Exception as e: messagebox.showerror("Open failed", str(e))

    def push(self, im):
        self.current = im
        self.history = self.history[:self.index+1] + [im.copy()]
        self.index += 1; self.draw()

    def black(self):
        if self.need():
            self.push(convert_to_black(self.current, int(self.threshold.get())))
            self.status.set("Converted to exact black and white.")

    def gray(self):
        if self.need():
            self.push(convert_to_grayscale(self.current)); self.status.set("Converted to grayscale.")

    def background(self):
        if self.need():
            try:
                self.push(remove_corner_background(self.current, int(self.tolerance.get())))
                self.status.set("Removed connected corner-color background pixels.")
            except Exception as e: messagebox.showerror("Background removal failed", str(e))

    def undo(self):
        if self.index > 0:
            self.index -= 1; self.current = self.history[self.index].copy(); self.draw()

    def redo(self):
        if self.index + 1 < len(self.history):
            self.index += 1; self.current = self.history[self.index].copy(); self.draw()

    def reset(self):
        if self.original is not None:
            self.push(self.original.copy()); self.status.set("Reset to original.")

    def save(self):
        if not self.need(): return
        path = filedialog.asksaveasfilename(defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("TIFF", "*.tif")])
        if not path: return
        try:
            if os.path.splitext(path)[1].lower() in (".jpg", ".jpeg"):
                flatten_for_jpeg(self.current).save(path, quality=95)
            else: self.current.save(path)
            self.status.set("Saved: " + path)
        except Exception as e: messagebox.showerror("Save failed", str(e))

    def batch(self):
        paths = filedialog.askopenfilenames(title="Select images",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp")])
        if not paths: return
        dlg = tk.Toplevel(self.root); dlg.title("Batch operation"); dlg.transient(self.root); dlg.grab_set()
        choice = tk.StringVar(value="black")
        ttk.Label(dlg, text="Choose one operation for all images").pack(padx=15, pady=8)
        for val, label in [("black", "Pure black & white"), ("grayscale", "Grayscale"), ("background", "Corner background removal")]:
            ttk.Radiobutton(dlg, text=label, value=val, variable=choice).pack(anchor="w", padx=15)
        result = []
        ttk.Button(dlg, text="Continue", command=lambda: (result.append(choice.get()), dlg.destroy())).pack(pady=10)
        dlg.wait_window()
        if not result: return
        outdir = filedialog.askdirectory(title="Choose output folder")
        if not outdir: return
        ok, errors = process_batch(paths, outdir, result[0], int(self.threshold.get()), int(self.tolerance.get()))
        msg = "{} saved; {} failed.".format(len(ok), len(errors))
        if errors: msg += "\n" + "\n".join("{}: {}".format(p, e) for p, e in errors[:5])
        messagebox.showinfo("Batch complete", msg); self.status.set(msg)

    def draw(self):
        self.canvas.delete("all")
        if self.current is None:
            self.canvas.create_text(max(1, self.canvas.winfo_width()//2), max(1, self.canvas.winfo_height()//2),
                                    text="Open an image to preview it", fill="white")
            return
        im = self.current.copy()
        im.thumbnail((max(1, self.canvas.winfo_width()-20), max(1, self.canvas.winfo_height()-20)),
                     Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS)
        checker = Image.new("RGB", im.size, "#eeeeee"); d = ImageDraw.Draw(checker)
        for y in range(0, im.height, 12):
            for x in range(0, im.width, 12):
                if (x//12 + y//12) % 2: d.rectangle((x, y, x+11, y+11), fill="#cccccc")
        checker.paste(im.convert("RGB"), mask=im.getchannel("A"))
        self.photo = ImageTk.PhotoImage(checker)
        self.canvas.create_image((self.canvas.winfo_width()-im.width)//2,
            (self.canvas.winfo_height()-im.height)//2, image=self.photo, anchor="nw")

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
