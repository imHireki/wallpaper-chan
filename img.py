import PIL.Image

from image.support import ImageSupportProxy
from image.editor import bulk_resize
from image import info


SAVE_OPTIONS = {
    "GIF": {
        "format": "GIF",
        "optimize": True,
        "disposal": 2,
        "background": (0,0,0,0),
        "save_all": True
    },
    "JPEG": {
        "format": "JPEG",
        "optimize": True,
        "quality": 75
    },
    "PNG": {
        "format": "PNG",
        "optimize": True
    },
}

SUPPORTED_IMAGES = {
    'STATIC': {
        'JPEG_RGB': info.StaticJpegRgbInfo,
        'PNG_RGB': info.StaticPngRgbInfo,
        'PNG_RGBA': info.StaticPngRgbaInfo,
        'WEBP_RGB': info.StaticWebpRgbInfo,
        'WEBP_RGBA': info.StaticWebpRgbaInfo
    },
    'ANIMATED': {
        'GIF_P': info.AnimatedGifPInfo,
        'WEBP_RGB': info.AnimatedWebpRgbInfo,
        'WEBP_RGBA': info.AnimatedWebpRgbaInfo
    }
}


with PIL.Image.open('image.jpg') as image:
    support_proxy = ImageSupportProxy(image, SUPPORTED_IMAGES)
    support = support_proxy.get_image_support()
    support_info = support.get_image_info()

    if not support_info:
        print("image not supported")
        exit()

    image_info = support_info(image)
           
    if not image_info.is_optimized():
        image_info.optimize(SAVE_OPTIONS)

    editor = image_info.get_image_editor()

    images = bulk_resize(editor, [{
        'resize': {'size': size, 'resample': 1, 'reducing_gap': 3},
        'save':   {'format': 'JPEG', 'optimize': True, 'quality': 75}
        }
        for size in [(256, 256), (128, 128)]
    ])

    image_256x256 = next(images).name
    image_128x128 = next(images).name

