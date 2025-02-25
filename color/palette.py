from abc import ABC, abstractmethod
from typing import Iterator, Union

import PIL.Image

from . import utils


_HSL = tuple[int, int, int]
_HSLA = tuple[int, int, int, int]
_RGBA = _HSLA
_RGB = _HSL
_HEX = str

ColorIterator = Iterator[_HEX | _RGB | _RGBA | _HSL | _HSLA]
Color = Union[_HEX | _RGB | _RGBA | _HSL | _HSLA]
ColorBands = list[list[int]]


class IColor(ABC):
    def __init__(self, image: PIL.Image.Image, alpha: bool = False) -> None:
        self.image = image
        self.alpha = 1 if alpha else 0

    @abstractmethod
    def get_color_bands(self) -> ColorBands:
        pass

    @staticmethod
    @abstractmethod
    def structure_palette(color_bands: ColorBands) -> ColorIterator:
        pass


class HexRGB(IColor):
    def get_color_bands(self) -> ColorBands:
        return [self.image.getdata(band) for band in range(3 + self.alpha)]

    @staticmethod
    def structure_palette(color_bands: ColorBands) -> Iterator[_HEX]:
        return map(lambda *RGB: utils.rgb_or_rgba_to_hex(RGB), *color_bands)


class RGB(IColor):
    def get_color_bands(self) -> ColorBands:
        return [self.image.getdata(band) for band in range(3 + self.alpha)]

    @staticmethod
    def structure_palette(color_bands: ColorBands) -> Iterator[_RGB | _RGBA]:
        return map(lambda *RGB: tuple(RGB), *color_bands)
