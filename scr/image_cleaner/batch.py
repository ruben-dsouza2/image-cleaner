from pathlib import Path
from PIL import Image
from image_cleaner.engine import convert_to_black, convert_to_grayscale, remove_corner_background

def process_batch(paths, output_dir, operation, threshold=128, tolerance=30):
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    funcs = {
        "black": lambda im: convert_to_black(im, threshold),
        "grayscale": convert_to_grayscale,
        "background": lambda im: remove_corner_background(im, tolerance),
    }
    if operation not in funcs:
        raise ValueError("Unknown operation")
    ok, errors = [], []
    for path in paths:
        src = Path(path)
        try:
            with Image.open(str(src)) as im:
                im.seek(0)
                result = funcs[operation](im.copy())
                target = outdir / (src.stem + "_cleaned.png")
                result.save(str(target), "PNG")
                result.close()
            ok.append(str(target))
        except Exception as exc:
            errors.append((str(src), str(exc)))
    return ok, errors
