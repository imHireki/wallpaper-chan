from abc import ABC, abstractmethod
from tempfile import _TemporaryFileWrapper

import PIL.Image

from image import editor


def has_translucent_alpha(image: PIL.Image.Image) -> bool:
    return image.getextrema()[-1][0] < 255


class IStaticImageInfo(ABC):
    _image_editor: editor.StaticImageEditor
    name: str

    def __init__(self, image: PIL.Image.Image) -> None:
        self._image: PIL.Image.Image = image

    @abstractmethod
    def is_optimized(self) -> bool: pass

    @abstractmethod
    def optimize(self, save_options: dict[str, dict]
                 ) -> _TemporaryFileWrapper: pass

    def get_image_editor(self) -> editor.StaticImageEditor:
        if not hasattr(self, '_image_editor'):
            self._image_editor = editor.StaticImageEditor(self._image)
        return self._image_editor

    def get_image_for_color_clustering(self) -> PIL.Image.Image:
        return self._image


class StaticJpegRgbInfo(IStaticImageInfo):
    name = 'JPEG_RGB'

    def is_optimized(self) -> bool: return True

    def optimize(self) -> None: pass


class StaticWebpRgbInfo(IStaticImageInfo):
    name = 'WEBP_RGB'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['JPEG'])
        return self._image_editor.result


class StaticWebpRgbaInfo(IStaticImageInfo):
    name = 'WEBP_RGBA'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        if not has_translucent_alpha(self._image):
            self._image_editor.save(**save_options['JPEG'])
        else:
            self._image_editor.save(**save_options['PNG'])

        return self._image_editor.result


class StaticPngRgbInfo(IStaticImageInfo):
    name = 'PNG_RGB'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['JPEG'])
        return self._image_editor.result


class StaticPngRgbaInfo(IStaticImageInfo):
    name = 'PNG_RGBA'

    def is_optimized(self) -> bool:
        return has_translucent_alpha(self._image)

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['JPEG'])
        return self._image_editor.result


class IAnimatedImageInfo(ABC):
    _image_editor: editor.AnimatedImageEditor
    name: str

    def __init__(self, image: PIL.Image.Image) -> None:
        self._image: PIL.Image.Image = image

    @abstractmethod
    def is_optimized(self) -> bool: pass

    @abstractmethod
    def optimize(self, save_options: dict[str, dict]
                 ) -> _TemporaryFileWrapper: pass

    def get_image_editor(self) -> editor.AnimatedImageEditor:
        if not hasattr(self, '_image_editor'):
            self._image_editor = editor.AnimatedImageEditor(self._image)
        return self._image_editor

    def get_image_for_color_clustering(self) -> PIL.Image.Image:
        self.get_image_editor()
        return self._image.convert(self._image_editor.actual_mode)


class AnimatedGifPInfo(IAnimatedImageInfo):
    name = 'GIF_P'

    def is_optimized(self) -> bool:
        return getattr(self._image, 'is_animated', False)

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        if not 'transparency' in self._image.info:
            self._image_editor.save(**save_options['JPEG'])
        else:
            self._image_editor.save(**save_options['PNG'])

        return self._image_editor.result


class AnimatedWebpRgbaInfo(IAnimatedImageInfo):
    name = 'WEBP_RGBA'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['GIF'])
        return self._image_editor.result


class AnimatedWebpRgbInfo(IAnimatedImageInfo):
    name = 'WEBP_RGB'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['GIF'])
        return self._image_editor.result
