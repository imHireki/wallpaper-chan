from abc import ABC, abstractmethod
from typing import Union, Generator
from dataclasses import dataclass
import tempfile

import PIL.Image, PIL.ImageSequence


def get_named_temporary_file() -> tempfile.NamedTemporaryFile:
    temporary_file = tempfile.NamedTemporaryFile(delete=False)
    temporary_file.close()
    return temporary_file


class IImageEditor(ABC):
    @property
    @abstractmethod
    def result(self) -> tempfile.NamedTemporaryFile: pass

    @abstractmethod
    def resize_image(self) -> None: pass

    @abstractmethod
    def save_resized_image(self) -> None: pass


class StaticImageEditor(IImageEditor):
    def __init__(self, image: PIL.Image.Image) -> None:
        self._image: PIL.Image.Image = image
        self._result: tempfile.NamedTemporaryFile = get_named_temporary_file()

    @property
    def result(self) -> tempfile.NamedTemporaryFile:
        return self._result

    def resize_image(self, size: tuple[int, int], resample: int, reducing_gap: int) -> None:
        self._image = self._image.resize(size=size, resample=resample, reducing_gap=reducing_gap)

    def save_resized_image(self, quality: int, format: str) -> None:
        with open(self._result.name, 'wb') as temporary_file:
            self._image.save(temporary_file, quality=quality, format=format)


class AnimatedImageEditor(IImageEditor):
    _frames: Generator[PIL.Image.Image, None, None]

    def __init__(self, image: PIL.Image.Image) -> None:
        self._image: PIL.Image.Image = image
        self._result: tempfile.NamedTemporaryFile = get_named_temporary_file()

    @property
    def result(self) -> tempfile.NamedTemporaryFile:
        return self._result

    def resize_image(self, size: tuple[int, int], resample: int, reducing_gap: int) -> None:
        self._frames = (frame.resize(size=size, resample=resample, reducing_gap=reducing_gap)
                        for frame in PIL.ImageSequence.Iterator(self._image))
        self._image = next(self._frames)

    def save_resized_image(self, quality: int, format: str) -> None:
        with open(self._result.name, 'wb') as temporary_file:
            self._image.save(
                temporary_file, quality=quality, format=format,
                loop=0, save_all=True, append_images=self._frames
            )


class BulkImageEditor(IImageEditor):
    _image_editor_generator: Generator[IImageEditor, None, None]
    _current_image_editor: IImageEditor

    def __init__(self, image_editor_generator: Generator[IImageEditor, None, None]) -> None:
        self._image_editor_generator = image_editor_generator

    def __next__(self) -> tempfile.NamedTemporaryFile:
        self._current_image_editor = next(self._image_editor_generator)
        self.resize_image()
        self.save_resized_image()
        return self.result

    @property
    def result(self) -> tempfile.NamedTemporaryFile:
        return self._current_image_editor.result

    def resize_image(self) -> None:
        self._current_image_editor.resize_image()

    def save_resized_image(self) -> None:
        self._current_image_editor.save_resized_image()
