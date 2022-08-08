from abc import ABC, abstractmethod
from typing import Union, Generator, Any
import tempfile

import PIL.ImageSequence
import PIL.Image


def get_named_temporary_file() -> tempfile.NamedTemporaryFile:
    temporary_file = tempfile.NamedTemporaryFile(delete=False)
    temporary_file.close()
    return temporary_file


class IImageEditor(ABC):
    @property
    @abstractmethod
    def actual_mode(self) -> str: pass

    @property
    @abstractmethod
    def result(self) -> tempfile.NamedTemporaryFile: pass

    @abstractmethod
    def convert_mode(self, mode: str) -> None: pass

    @abstractmethod
    def resize(self, size: tuple[int, int], resample: int, reducing_gap: int) -> None: pass

    @abstractmethod
    def save(self, format: str, **extra_options: dict[str, Any]) -> None: pass


class StaticImageEditor(IImageEditor):
    def __init__(self, image: PIL.Image.Image) -> None:
        self._original_image: PIL.Image.Image = image
        self._edited_image: PIL.Image.Image = None
        self._result: tempfile.NamedTemporaryFile = get_named_temporary_file()

    @property
    def actual_mode(self) -> str:
        return self._original_image.mode

    @property
    def result(self) -> tempfile.NamedTemporaryFile:
        return self._result

    def convert_mode(self, mode: str) -> None:
        self._edited_image = self._original_image.convert(mode=mode)

    def resize(self, size: tuple[int, int], resample: int, reducing_gap: int) -> None:
        self._edited_image = self._original_image.resize(size=size, resample=resample,
                                                         reducing_gap=reducing_gap)

    def save(self, format: str, **extra_options: dict[str, Any]) -> None:
        if not self._edited_image:
            self.convert_mode(self.actual_mode)

        with open(self._result.name, 'wb') as temporary_file:
            self._edited_image.save(temporary_file, format=format, **extra_options)

        self._edited_image = None


class AnimatedImageEditor(IImageEditor):
    def __init__(self, image: PIL.Image.Image) -> None:
        self._original_image: PIL.Image.Image = image
        self._edited_frames: Generator[PIL.Image.Image, None, None] = None
        self._result: tempfile.NamedTemporaryFile = get_named_temporary_file()
        self._actual_mode: str = self._find_actual_mode()

    @property
    def actual_mode(self) -> str:
        return self._actual_mode

    @property
    def result(self) -> tempfile.NamedTemporaryFile:
        return self._result

    def convert_mode(self, mode: str) -> None:
        self._edited_frames = (frame.convert(mode=mode)
                               if frame.mode != self.actual_mode else
                               frame.copy()
                               for frame in self._get_frames())

    def resize(self, size: tuple[int, int], resample: int, reducing_gap: int) -> None:
        resize_options = {"size": size, "resample": resample, "reducing_gap": reducing_gap}

        self._edited_frames = (frame.convert(self.actual_mode).resize(**resize_options)
                               if frame.mode != self.actual_mode else
                               frame.resize(**resize_options)
                               for frame in self._get_frames())

    def save(self, format: str, **extra_options: dict[str, Any]) -> None:
        if not self._edited_frames:
            self.convert_mode(self.actual_mode)

        first_frame = next(self._edited_frames)

        if 'save_all' in extra_options:
            extra_options.update(append_images=list(self._edited_frames))

        self._edited_frames = None

        with open(self._result.name, 'wb') as temporary_file:
            first_frame.save(temporary_file, format=format, **extra_options)

    def _find_actual_mode(self) -> str:
        if self._original_image.mode == 'RGBA':
            return 'RGBA' if self._original_image.getextrema()[-1][0] < 255 else 'RGB'
        return 'RGB' if not 'transparency' in self._original_image.info else 'RGBA'

    def _get_frames(self) -> PIL.ImageSequence.Iterator:
        return PIL.ImageSequence.Iterator(self._original_image)


class BulkResizeSaveEditor(IImageEditor):
    _image_editor_generator: Generator[IImageEditor, None, None]
    _current_image_editor: IImageEditor

    def __init__(self, image_editor_generator: Generator[IImageEditor, None, None],
                 save_options: dict[str, Any], resize_options: dict[str, Any]) -> None:
        self._image_editor_generator = image_editor_generator
        self._save_options: dict[str, Any] = save_options
        self._resize_options: dict[str, Any] = resize_options

    def __next__(self) -> tempfile.NamedTemporaryFile:
        self._current_image_editor = next(self._image_editor_generator)
        self.resize(**self._resize_options)
        self.save(**self._save_options)
        return self.result

    @property
    def actual_mode(self) -> str:
        return self._current_image_editor.actual_mode

    @property
    def result(self) -> tempfile.NamedTemporaryFile:
        return self._current_image_editor.result

    def convert_mode(self, mode: str) -> None: pass

    def resize(self, size: tuple[int, int], resample: int, reducing_gap: int) -> None:
        self._current_image_editor.resize(size=size, resample=resample, reducing_gap=reducing_gap)

    def save(self, format: str, **extra_options) -> None:
        self._current_image_editor.save(format=format, **extra_options)
