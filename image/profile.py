from abc import ABC, abstractmethod
from tempfile import _TemporaryFileWrapper

import PIL.Image

from image import editor


def has_translucent_alpha(image: PIL.Image.Image) -> bool:
    bands_min_max = image.getextrema()

    if isinstance(bands_min_max[0], tuple) and len(bands_min_max) == 4:  # RGBA
        return bands_min_max[3][0] < 255
    return False


class IStaticImageProfile(ABC):
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


class StaticJpegRgbProfile(IStaticImageProfile):
    name = 'JPEG_RGB'

    def is_optimized(self) -> bool: return True

    def optimize(self) -> None: pass


class StaticWebpRgbProfile(IStaticImageProfile):
    name = 'WEBP_RGB'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['JPEG'])
        return self._image_editor.result


class StaticWebpRgbaProfile(IStaticImageProfile):
    name = 'WEBP_RGBA'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        if not has_translucent_alpha(self._image):
            self._image_editor.save(**save_options['JPEG'])
        else:
            self._image_editor.save(**save_options['PNG'])

        return self._image_editor.result


class StaticPngRgbProfile(IStaticImageProfile):
    name = 'PNG_RGB'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['JPEG'])
        return self._image_editor.result


class StaticPngRgbaProfile(IStaticImageProfile):
    name = 'PNG_RGBA'

    def is_optimized(self) -> bool:
        return has_translucent_alpha(self._image)

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['JPEG'])
        return self._image_editor.result


class IAnimatedImageProfile(ABC):
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


class AnimatedGifPProfile(IAnimatedImageProfile):
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


class AnimatedWebpRgbaProfile(IAnimatedImageProfile):
    name = 'WEBP_RGBA'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['GIF'])
        return self._image_editor.result


class AnimatedWebpRgbProfile(IAnimatedImageProfile):
    name = 'WEBP_RGB'

    def is_optimized(self) -> bool: return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options['GIF'])
        return self._image_editor.result
