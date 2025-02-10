import PIL.Image


def has_translucent_alpha(image: PIL.Image.Image) -> bool:
    bands_min_max = image.getextrema()

    if isinstance(bands_min_max[0], tuple) and len(bands_min_max) == 4:  # RGBA
        return bands_min_max[3][0] < 255
    return False
