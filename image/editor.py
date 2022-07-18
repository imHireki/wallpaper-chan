from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union
import tempfile

import PIL.Image


@dataclass
class EditorOptions:
    size: tuple[int, int]
    resample: int
    reducing_gap: int

    quality: int
    format: str

    @property
    def resize_options(self) -> dict[str, Union[tuple, int, int]]:
        return {
            "size": self.size,
            "resample": self.resample,
            "reducing_gap": self.reducing_gap
        }

    @property
    def save_options(self) -> dict[str, Union[int, str]]:
        return {
            "quality": self.quality,
            "format": self.format
        }


class IImageEditor(ABC):
    _editor_options: EditorOptions
    _image: PIL.Image.Image
    _result: tempfile.NamedTemporaryFile

    def __init__(self, image: PIL.Image.Image, editor_options: EditorOptions) -> None:
        self._image = image
        self._editor_options = editor_options

    def _get_named_temporary_file(self) -> tempfile.NamedTemporaryFile:
        temporary_file = tempfile.NamedTemporaryFile(delete=False)
        temporary_file.close()
        return temporary_file

    @property
    @abstractmethod
    def result(self) -> tempfile.NamedTemporaryFile: pass

    @abstractmethod
    def resize_image(self) -> None: pass

    @abstractmethod
    def save_resized_image(self) -> None: pass

