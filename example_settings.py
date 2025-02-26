from image import profile


GIF_SAVE_OPTIONS = {
    "format": "GIF",
    "optimize": True,
    "disposal": 2,
    "background": (0, 0, 0, 0),
    "save_all": True,
}
JPEG_SAVE_OPTIONS = {"format": "JPEG", "optimize": True, "quality": 75}
PNG_SAVE_OPTIONS = {"format": "PNG", "optimize": True}
SAVE_OPTIONS = {
    "GIF": GIF_SAVE_OPTIONS,
    "JPEG": JPEG_SAVE_OPTIONS,
    "PNG": PNG_SAVE_OPTIONS,
}

STATIC_SUPPORTED_IMAGES = [
    profile.StaticJpegRgbProfile,
    profile.StaticPngRgbProfile,
    profile.StaticPngRgbaProfile,
    profile.StaticWebpRgbProfile,
    profile.StaticWebpRgbaProfile,
]
ANIMATED_SUPPORTED_IMAGES = [
    profile.AnimatedGifPProfile,
    profile.AnimatedWebpRgbProfile,
    profile.AnimatedWebpRgbaProfile,
]

SUPPORTED_IMAGES = {
    "STATIC": {static.name: static for static in STATIC_SUPPORTED_IMAGES},
    "ANIMATED": {animated.name: animated for animated in ANIMATED_SUPPORTED_IMAGES},
}
