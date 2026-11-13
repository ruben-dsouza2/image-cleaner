# Image Cleaner

An offline-first desktop image utility for controlled, explicit edits.

## Included in this starter (v0.1)
- Open PNG, JPG, BMP, GIF (first frame), TIFF, and WebP.
- Convert to exact black and white using an adjustable luminance threshold.
- Convert to grayscale while preserving transparency.
- Remove connected pixels similar to the top-left corner color (simple flat-background removal).
- Checkerboard transparency preview, undo, redo, reset, and export.
- Sequential batch processing to PNG.

**Background removal is not AI segmentation.** It works best on a flat, uniform background. Inspect the result before saving. The original file is never overwritten automatically.

## Run from source
Requires Python 3.8+ and Tkinter.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements/modern.txt
```

Windows:
```bat
set PYTHONPATH=src
python app.py
```
macOS/Linux:
```bash
PYTHONPATH=src python app.py
```

## Tests
```bash
pip install -r requirements/dev.txt
PYTHONPATH=src pytest
```

## Windows 7 compatibility
Windows 7 is unsupported by Microsoft and current Python releases. The `windows7.txt` file is an experimental dependency pin intended for Python 3.8 64-bit with Tcl/Tk. It is **not a compatibility guarantee**. Test installation, opening, editing, saving, and packaging on a real Windows 7 SP1 machine before release. Modern AI runtimes and cloud SDKs may not support Windows 7.

## Privacy
This version makes no network requests and never uploads images. Future cloud AI functions must require explicit consent per operation and offer a local-only mode.

## Roadmap
1. Selection masks and brush-based precise cleanup.
2. Dedicated line/mark cleanup.
3. Optional local AI background removal and inpainting.
4. Opt-in online AI through replaceable provider adapters.
5. Separate Windows 7, modern Windows, and macOS packages.

MIT licensed. See `LICENSE`.
