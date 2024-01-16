from tempfile import NamedTemporaryFile, _TemporaryFileWrapper
from typing import Generator, Any, Literal, Iterator
from abc import ABC, abstractmethod

import PIL.ImageSequence
import PIL.Image


Resample = PIL.Image.Resampling | Literal[0, 1, 2, 3, 4, 5] | None

def get_named_temporary_file() -> _TemporaryFileWrapper:
    temporary_file = NamedTemporaryFile(delete=False)
    temporary_file.close()
    return temporary_file


class IImageEditor(ABC):
    @property
    @abstractmethod
    def actual_mode(self) -> str: pass

    @property
    @abstractmethod
    def result(self) -> _TemporaryFileWrapper: pass

    @result.deleter
    @abstractmethod
    def result(self) -> None: pass

    @abstractmethod
    def convert_mode(self, mode: str) -> None: pass

    @abstractmethod
    def resize(self, size: tuple[int, int], resample: Resample,
               reducing_gap: int) -> None: pass

    @abstractmethod
    def save(self, format: str, **extra_options: Any) -> None: pass


class StaticImageEditor(IImageEditor):
    def __init__(self, image: PIL.Image.Image) -> None:
        self._original_image: PIL.Image.Image = image
        self._edited_image: PIL.Image.Image | None = None
        self._result: _TemporaryFileWrapper = get_named_temporary_file()

    @property
    def actual_mode(self) -> str:
        return self._original_image.mode

    @property
    def result(self) -> _TemporaryFileWrapper:
        return self._result

    @result.deleter
    def result(self) -> None:
        self._result = get_named_temporary_file()

    def convert_mode(self, mode: str) -> None:
        self._edited_image = self._original_image.convert(mode=mode)

    def resize(self, size: tuple[int, int],
               resample: Resample, reducing_gap: int) -> None:
        self._edited_image = self._original_image.resize(
            size=size, resample=resample, reducing_gap=reducing_gap)

    def save(self, format: str, **extra_options: Any) -> None:
        if not self._edited_image:
            self.convert_mode(self.actual_mode)

        with open(self._result.name, 'wb') as temporary_file:
            self._edited_image.save(  # type: ignore
                temporary_file, format=format, **extra_options)
        self._edited_image = None


class AnimatedImageEditor(IImageEditor):
    _edited_frames: Generator[PIL.Image.Image, None, None]

    def __init__(self, image: PIL.Image.Image) -> None:
        self._original_image: PIL.Image.Image = image
        self._result: _TemporaryFileWrapper = get_named_temporary_file()
        self._actual_mode: str = self._find_actual_mode()

    @property
    def actual_mode(self) -> str:
        return self._actual_mode

    @property
    def result(self) -> _TemporaryFileWrapper:
        return self._result

    @result.deleter
    def result(self) -> None:
        self._result = get_named_temporary_file()

    def convert_mode(self, mode: str) -> None:
        self._edited_frames = (
            frame.convert(mode=mode)
            if frame.mode != self.actual_mode else
            frame.copy()
            for frame in self._get_frames()
        )

    def resize(self, size: tuple[int, int], resample: Resample,
               reducing_gap: int) -> None:
        resize_options = {
            "size": size,
            "resample": resample,
            "reducing_gap": reducing_gap
        }
        self._edited_frames = (
            frame.convert(self.actual_mode).resize(**resize_options)
            if frame.mode != self.actual_mode else
            frame.resize(**resize_options)
            for frame in self._get_frames()
        )

    def save(self, format: str, **extra_options: Any) -> None:
        if not self._edited_frames:
            self.convert_mode(self.actual_mode)
        first_frame = next(self._edited_frames)

        if 'save_all' in extra_options:
            extra_options.update(append_images=list(self._edited_frames))
        del self._edited_frames 

        with open(self._result.name, 'wb') as temporary_file:
            first_frame.save(temporary_file, format=format, **extra_options)

    def _find_actual_mode(self) -> str:
        if self._original_image.mode == 'RGBA':
            alpha_value = self._original_image.getextrema()[-1][0]
            return 'RGBA' if alpha_value < 255 else 'RGB'

        has_transparency = 'transparency' in self._original_image.info
        return 'RGB' if not has_transparency else 'RGBA'

    def _get_frames(self) -> PIL.ImageSequence.Iterator:
        return PIL.ImageSequence.Iterator(self._original_image)


def bulk_resize(editor: IImageEditor, resize_save_options: list[dict]):
    for options in resize_save_options:
        editor.resize(**options['resize'])
        editor.save(**options['save'])
        result = editor.result
        del editor.result
        yield result


class BulkResizeSaveEditor(IImageEditor):
    def __init__(self, editor: IImageEditor,
                 resize_save_options: list[dict]):
        self._editor: IImageEditor = editor
        self._options: Iterator = iter(resize_save_options)

    def __next__(self) -> _TemporaryFileWrapper:
        options = next(self._options)
        self.resize(**options.get('resize'))
        self.save(**options.get('save'))
        result = self.result
        del self.result
        return result

    @property
    def actual_mode(self) -> str:
        return self._editor.actual_mode

    @property
    def result(self) -> _TemporaryFileWrapper:
        return self._editor.result

    @result.deleter
    def result(self) -> None: pass

    def convert_mode(self, mode: str) -> None: pass

    def resize(self, size: tuple[int, int], resample: Resample,
               reducing_gap: int) -> None:
        self._editor.resize(
            size=size, resample=resample, reducing_gap=reducing_gap)

    def save(self, format: str, **extra_options) -> None:
        self._editor.save(format=format, **extra_options)

