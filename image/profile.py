from abc import ABC, abstractmethod

from PIL.Image import Image

from image import editor
from image import utils


class IStaticProfile(ABC):
    _editor: editor.StaticEditor
    name: str

    def __init__(self, image: Image) -> None:
        self._image: Image = image

    @abstractmethod
    def is_optimized(self) -> bool:
        pass

    def get_editor(self) -> editor.StaticEditor:
        if not hasattr(self, "_editor"):
            self._editor = editor.StaticEditor(self._image)
        return self._editor

    def get_color_clustering_image(self) -> Image:
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
        self.get_editor()
        self._editor.save(output, **save_options["JPEG"])


class StaticWebpRgbaProfile(IOptimizableStaticProfile):
    name = "WEBP_RGBA"

    def is_optimized(self) -> bool:
        return False

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_editor()

        if not utils.has_translucent_alpha(self._image):
            self._editor.convert_mode("RGB")
            self._editor.save(output, **save_options["JPEG"])
        else:
            self._editor.save(output, **save_options["PNG"])


class StaticPngRgbProfile(IOptimizableStaticProfile):
    name = "PNG_RGB"

    def is_optimized(self) -> bool:
        return False

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_editor()
        self._editor.save(output, **save_options["JPEG"])


class StaticPngRgbaProfile(IOptimizableStaticProfile):
    name = "PNG_RGBA"

    def is_optimized(self) -> bool:
        return utils.has_translucent_alpha(self._image)

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_editor()

        self._editor.convert_mode("RGB")
        self._editor.save(output, **save_options["JPEG"])


class IAnimatedProfile(ABC):
    _editor: editor.AnimatedEditor
    name: str

    def __init__(self, image: Image) -> None:
        self._image: Image = image

    @abstractmethod
    def is_optimized(self) -> bool:
        pass

    def get_editor(self) -> editor.AnimatedEditor:
        if not hasattr(self, "_editor"):
            self._editor = editor.AnimatedEditor(self._image)
        return self._editor

    def get_color_clustering_image(self) -> Image:
        self.get_editor()
        # only the 1st frame in its actual mode
        return self._image.convert(self._editor.actual_mode)


class IOptimizableAnimatedProfile(IAnimatedProfile):
    @abstractmethod
    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        pass


class AnimatedGifPProfile(IOptimizableAnimatedProfile):
    name = "GIF_P"

    def is_optimized(self) -> bool:
        return getattr(self._image, "is_animated", False)

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_editor()

        if not "transparency" in self._image.info:
            self._editor.save(output, **save_options["JPEG"])
        else:
            self._editor.save(output, **save_options["PNG"])


class AnimatedWebpRgbaProfile(IOptimizableAnimatedProfile):
    name = "WEBP_RGBA"

    def is_optimized(self) -> bool:
        return False

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_editor()
        self._editor.save(output, **save_options["GIF"])


class AnimatedWebpRgbProfile(IOptimizableAnimatedProfile):
    name = "WEBP_RGB"

    def is_optimized(self) -> bool:
        return False

    def optimize(self, output: editor.File, save_options: dict[str, dict]) -> None:
        self.get_editor()
        self._editor.save(output, **save_options["GIF"])
