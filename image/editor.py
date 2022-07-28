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
    def convert_mode(self) -> None: pass

    @abstractmethod
    def resize(self) -> None: pass

    @abstractmethod
    def save(self) -> None: pass


class StaticImageEditor(IImageEditor):
    def __init__(self, image: PIL.Image.Image) -> None:
        self._image: PIL.Image.Image = image
        self._result: tempfile.NamedTemporaryFile = get_named_temporary_file()

    @property
    def result(self) -> tempfile.NamedTemporaryFile:
        return self._result

    def convert_mode(self, mode: str) -> None:
        self._image = self._image.convert(mode=mode)

    def resize(self, size: tuple[int, int], resample: int, reducing_gap: int) -> None:
        self._image = self._image.resize(size=size, resample=resample, reducing_gap=reducing_gap)

    def save(self, quality: int, format: str) -> None:
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

    def convert_mode(self, mode: str) -> None:
        self._frames = (frame.convert(mode=mode) for frame in PIL.ImageSequence.Iterator(self._image))
        self._image = next(self._frames)

    def resize(self, size: tuple[int, int], resample: int, reducing_gap: int) -> None:
        self._frames = (frame.resize(size=size, resample=resample, reducing_gap=reducing_gap)
                        for frame in PIL.ImageSequence.Iterator(self._image))
        self._image = next(self._frames)

    def save(self, quality: int, format: str) -> None:
        with open(self._result.name, 'wb') as temporary_file:
            self._image.save(
                temporary_file, quality=quality, format=format,
                loop=0, save_all=True, append_images=self._frames
            )

class BulkResizeSaveEditor(IImageEditor):
    _image_editor_generator: Generator[IImageEditor, None, None]
    _current_image_editor: IImageEditor

    def __init__(self, image_editor_generator: Generator[IImageEditor, None, None],
                 save_options: dict, resize_options: dict) -> None:
        self._image_editor_generator = image_editor_generator
        self._save_options: dict = save_options
        self._resize_options: dict = resize_options

    def __next__(self) -> tempfile.NamedTemporaryFile:
        self._current_image_editor = next(self._image_editor_generator)
        self.resize(**self._resize_options)
        self.save_resized_image(**self._save_options)
        return self.result

    @property
    def result(self) -> tempfile.NamedTemporaryFile:
        return self._current_image_editor.result

    def convert_mode(self, mode: str) -> None: pass

    def resize(self, size: tuple[int, int], resample: int, reducing_gap: int) -> None:
        self._current_image_editor.resize(size=size, resample=resample, reducing_gap=reducing_gap)

    def save_resized_image(self, quality: int, format: str) -> None:
        self._current_image_editor.save_resized_image(quality=quality, format=format)

