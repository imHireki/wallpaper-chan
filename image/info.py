from abc import ABC, abstractmethod
import tempfile

import PIL.Image

from . import editor


save_options = {
    "GIF": {"format": "GIF", "optimize": True, "disposal": 2, "background": (0,0,0,0), "save_all": True},
    "JPEG": {"format": "JPEG", "optimize": True, "quality": 75},
    "PNG": {"format": "PNG", "optimize": True},
}

def has_translucent_alpha(image: PIL.Image.Image) -> bool:
    return image.getextrema()[-1][0] < 255


class IStaticImageInfo(ABC):
    _image_editor: editor.StaticImageEditor

    def __init__(self, image: PIL.Image.Image) -> None:
        self._image: PIL.Image.Image = image

    @classmethod
    @abstractmethod
    def name(cls) -> str: pass

    @abstractmethod
    def is_standardized(self) -> bool: pass

    @abstractmethod
    def standardize(self) -> tempfile.NamedTemporaryFile: pass

    def get_image_editor(self) -> editor.StaticImageEditor:
        if not hasattr(self, '_image_editor'):
            self._image_editor = editor.StaticImageEditor(self._image)
        return self._image_editor

    def get_image_for_color_clustering(self) -> PIL.Image.Image:
        return self._image


class StaticJpegRgbInfo(IStaticImageInfo):
    @classmethod
    @property
    def name(cls) -> str: return 'JPEG_RGB'

    def is_standardized(self) -> bool: return True

    def standardize(self) -> None: pass


class StaticWebpRgbInfo(IStaticImageInfo):
    @classmethod
    @property
    def name(cls) -> str: return 'WEBP_RGB'

    def is_standardized(self) -> bool: return False

    def standardize(self) -> tempfile.NamedTemporaryFile:
        self.get_image_editor()

        self._image_editor.save(**save_options['JPEG'])
        return self._image_editor.result


class StaticWebpRgbaInfo(IStaticImageInfo):
    @classmethod
    @property
    def name(cls) -> str: return 'WEBP_RGBA'

    def is_standardized(self) -> bool: return False

    def standardize(self) -> tempfile.NamedTemporaryFile:
        self.get_image_editor()

        if not has_translucent_alpha(self._image):
            self._image_editor.save(**save_options['JPEG'])
        else:
            self._image_editor.save(**save_options['PNG'])

        return self._image_editor.result


class StaticPngRgbInfo(IStaticImageInfo):
    @classmethod
    @property
    def name(cls) -> str: return 'PNG_RGB'

    def is_standardized(self) -> bool: return False

    def standardize(self) -> tempfile.NamedTemporaryFile:
        self.get_image_editor()

        self._image_editor.save(**save_options['JPEG'])
        return self._image_editor.result
