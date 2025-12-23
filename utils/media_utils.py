from PIL import Image
import settings

def resize_and_pad(img_path: str, target_size=(1080, 1920)):
    img = Image.open(img_path).convert("RGB")
    orig_w, orig_h = img.size
    ratio = target_size[1] / orig_h
    new_w, new_h = int(orig_w * ratio), target_size[1]
    img = img.resize((new_w, new_h), Image.LANCZOS)
    background = Image.new("RGB", target_size, (0,0,0))
    offset = ((target_size[0] - new_w)//2, 0)
    background.paste(img, offset)
    background.save(img_path)


def resize_and_crop(img_path: str, shape: str):
    img = Image.open(img_path).convert("RGB")
    orig_w, orig_h = img.size

    # Determine target dims
    if shape == settings.ORIENTATION_LANDSCAPE:
        target_w, target_h = 1920, 1080
    elif shape == settings.ORIENTATION_PORTRAIT:
        target_w, target_h = 1080, 1920
    elif shape == settings.ORIENTATION_SQUARE:
        target_w = target_h = 1080
    else:
        raise ValueError(f"Unknown shape: {shape}")

    # If the image is already the target size, skip resampling entirely
    if (orig_w, orig_h) == (target_w, target_h):
        print(f"Image size of {orig_w}x{orig_w} is already the desired size of {target_w}x{target_h}. \nTherefore returning without resizing")
        return target_w, target_h

    # Otherwise compute scale & resize as before…
    if shape == settings.ORIENTATION_LANDSCAPE:
        scale = target_w / orig_w
        new_w = target_w
        new_h = int(orig_h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        top = (new_h - target_h) // 2
        img = img.crop((0, top, target_w, top + target_h))

    elif shape == settings.ORIENTATION_PORTRAIT:
        scale = target_h / orig_h
        new_h = target_h
        new_w = int(orig_w * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        img = img.crop((left, 0, left + target_w, target_h))

    elif shape == settings.ORIENTATION_SQUARE:
        # upscale smaller side to 1080 and center-crop
        scale = (target_w / orig_w) if orig_w < orig_h else (target_h / orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        top  = (new_h - target_h) // 2
        img = img.crop((left, top, left + target_w, top + target_h))

    img.save(img_path)
    return target_w, target_h
