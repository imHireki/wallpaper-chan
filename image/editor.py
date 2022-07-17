from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union
from io import BytesIO

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

