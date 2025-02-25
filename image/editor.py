from typing import Any, Literal, IO, Iterator
from abc import ABC, abstractmethod

from PIL._typing import StrOrBytesPath
from PIL.Image import Image, Resampling
from PIL import ImageSequence

from image import utils


Resample = Resampling | Literal[0, 1, 2, 3, 4, 5] | None
File = StrOrBytesPath | IO[bytes]


class IImageEditor(ABC):
    @property
    @abstractmethod
    def actual_mode(self) -> str:
        pass

    @abstractmethod
    def convert_mode(self, mode: str) -> None:
        pass

    @abstractmethod
    def resize(
        self, size: tuple[int, int], resample: Resample, reducing_gap: int
    ) -> None:
        pass

    @abstractmethod
    def save(self, output: File, format: str, **extra_options: Any) -> None:
        pass


class StaticImageEditor(IImageEditor):
    def __init__(self, image: Image) -> None:
        self._original_image = self._processed_image = image

    @property
    def actual_mode(self) -> str:
        return self._original_image.mode

    def convert_mode(self, mode: str) -> None:
        self._processed_image = self._original_image.convert(mode=mode)

    def resize(
        self, size: tuple[int, int], resample: Resample, reducing_gap: int
    ) -> None:
        self._processed_image = self._original_image.resize(
            size=size, resample=resample, reducing_gap=reducing_gap
        )

    def save(self, output: File, format: str, **extra_options: Any) -> None:
        self._processed_image.save(output, format=format, **extra_options)


class AnimatedImageEditor(IImageEditor):
    def __init__(self, image: Image) -> None:
        self._original_image: Image = image
        self._processed_frames: Iterator = self._get_frames()
        self._actual_mode: str = self._find_actual_mode()

    @property
    def actual_mode(self) -> str:
        return self._actual_mode

    def convert_mode(self, mode: str) -> None:
        self._processed_frames = (
            frame.convert(mode=mode) if frame.mode != self.actual_mode else frame.copy()
            for frame in self._get_frames()
        )

    def resize(
        self, size: tuple[int, int], resample: Resample, reducing_gap: int
    ) -> None:
        resize_options = {
            "size": size,
            "resample": resample,
            "reducing_gap": reducing_gap,
        }
        self._processed_frames = (
            (
                frame.convert(self.actual_mode).resize(**resize_options)
                if frame.mode != self.actual_mode
                else frame.resize(**resize_options)
            )
            for frame in self._get_frames()
        )

    def save(self, output: File, format: str, **extra_options: Any) -> None:
        first_frame = next(self._processed_frames)

        # Prepare to save all frames (to save as an animated image)
        if "save_all" in extra_options:
            extra_options.update(append_images=list(self._processed_frames))

        # Delete all the extra frames (to save as a static image)
        del self._processed_frames

        first_frame.save(output, format=format, **extra_options)

    def _find_actual_mode(self) -> str:
        if self._original_image.mode == "RGBA":
            return (
                "RGBA" if utils.has_translucent_alpha(self._original_image) else "RGB"
            )
        has_transparency = "transparency" in self._original_image.info
        return "RGB" if not has_transparency else "RGBA"

    def _get_frames(self) -> ImageSequence.Iterator:
        return ImageSequence.Iterator(self._original_image)
