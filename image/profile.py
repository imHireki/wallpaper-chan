from abc import ABC, abstractmethod
from io import BytesIO

from PIL.Image import Image

from image import utils
from image import editor


class IStaticProfile(ABC):
    _image_editor: editor.StaticImageEditor
    name: str

    def __init__(self, image: Image) -> None:
        self._image: Image = image

    @abstractmethod
    def is_optimized(self) -> bool:
        pass

    def get_image_editor(self) -> editor.StaticImageEditor:
        if not hasattr(self, "_image_editor"):
            self._image_editor = editor.StaticImageEditor(self._image)
        return self._image_editor

    def get_image_for_color_clustering(self) -> Image:
        return self._image


class IOptimizableStaticProfile(IStaticProfile):
    @abstractmethod
    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        pass


class StaticJpegRgbProfile(IStaticProfile):
    name = "JPEG_RGB"

    def is_optimized(self) -> bool:
        return True


class StaticWebpRgbProfile(IOptimizableStaticProfile):
    name = "WEBP_RGB"

    def is_optimized(self) -> bool:
        return False

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_image_editor()
        self._image_editor.save(output, **save_options["JPEG"])


class StaticWebpRgbaProfile(IOptimizableStaticProfile):
    name = "WEBP_RGBA"

    def is_optimized(self) -> bool:
        return False

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_image_editor()

        if not utils.has_translucent_alpha(self._image):
            self._image_editor.convert_mode("RGB")
            self._image_editor.save(output, **save_options["JPEG"])
        else:
            self._image_editor.save(output, **save_options["PNG"])


class StaticPngRgbProfile(IOptimizableStaticProfile):
    name = "PNG_RGB"

    def is_optimized(self) -> bool:
        return False

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_image_editor()
        self._image_editor.save(output, **save_options["JPEG"])


class StaticPngRgbaProfile(IOptimizableStaticProfile):
    name = "PNG_RGBA"

    def is_optimized(self) -> bool:
        return utils.has_translucent_alpha(self._image)

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_image_editor()

        self._image_editor.convert_mode("RGB")
        self._image_editor.save(output, **save_options["JPEG"])


class IAnimatedImageProfile(ABC):
    _image_editor: editor.AnimatedImageEditor
    name: str

    def __init__(self, image: PIL.Image.Image) -> None:
        self._image: PIL.Image.Image = image

    @abstractmethod
    def is_optimized(self) -> bool:
        pass

    @abstractmethod
    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        pass

    def get_image_editor(self) -> editor.AnimatedImageEditor:
        if not hasattr(self, "_image_editor"):
            self._image_editor = editor.AnimatedImageEditor(self._image)
        return self._image_editor

    def get_image_for_color_clustering(self) -> PIL.Image.Image:
        self.get_image_editor()
        return self._image.convert(self._image_editor.actual_mode)


class AnimatedGifPProfile(IAnimatedImageProfile):
    name = "GIF_P"

    def is_optimized(self) -> bool:
        return getattr(self._image, "is_animated", False)

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        if not "transparency" in self._image.info:
            self._image_editor.save(**save_options["JPEG"])
        else:
            self._image_editor.save(**save_options["PNG"])

        return self._image_editor.result


class AnimatedWebpRgbaProfile(IAnimatedImageProfile):
    name = "WEBP_RGBA"

    def is_optimized(self) -> bool:
        return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options["GIF"])
        return self._image_editor.result


class AnimatedWebpRgbProfile(IAnimatedImageProfile):
    name = "WEBP_RGB"

    def is_optimized(self) -> bool:
        return False

    def optimize(self, save_options: dict[str, dict]) -> _TemporaryFileWrapper:
        self.get_image_editor()

        self._image_editor.save(**save_options["GIF"])
        return self._image_editor.result
