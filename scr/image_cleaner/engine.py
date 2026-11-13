from PIL import Image, ImageOps

def convert_to_black(image, threshold=128):
    rgba = image.convert("RGBA")
    gray = ImageOps.grayscale(rgba.convert("RGB"))
    bw = gray.point(lambda v: 0 if v <= threshold else 255).convert("RGBA")
    bw.putalpha(rgba.getchannel("A"))
    return bw

def convert_to_grayscale(image):
    rgba = image.convert("RGBA")
    out = ImageOps.grayscale(rgba.convert("RGB")).convert("RGBA")
    out.putalpha(rgba.getchannel("A"))
    return out

def remove_corner_background(image, tolerance=30):
    """Remove connected pixels similar to the top-left corner; flat backgrounds only."""
    if not 0 <= tolerance <= 441:
        raise ValueError("Tolerance must be between 0 and 441")
    out = image.convert("RGBA")
    px = out.load()
    w, h = out.size
    if not w or not h:
        return out
    sample = px[0, 0][:3]
    limit = tolerance * tolerance
    seen = bytearray(w * h)
    stack = [(0, 0)]
    while stack:
        x, y = stack.pop()
        idx = y * w + x
        if seen[idx]:
            continue
        seen[idx] = 1
        r, g, b, a = px[x, y]
        d = (r-sample[0])**2 + (g-sample[1])**2 + (b-sample[2])**2
        if d <= limit:
            px[x, y] = (r, g, b, 0)
            if x: stack.append((x-1, y))
            if x+1 < w: stack.append((x+1, y))
            if y: stack.append((x, y-1))
            if y+1 < h: stack.append((x, y+1))
    return out

def flatten_for_jpeg(image):
    rgba = image.convert("RGBA")
    base = Image.new("RGB", rgba.size, "white")
    base.paste(rgba, mask=rgba.getchannel("A"))
    return base
