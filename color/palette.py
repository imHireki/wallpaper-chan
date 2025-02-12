from abc import ABC, abstractmethod
from binascii import hexlify
from typing import Iterator, Union

import PIL.Image

from color.cluster import ColorCluster, RGB
from . import utils


_HSL = tuple[int, int, int]
_HSLA = tuple[int, int, int, int]
_RGBA = _HSLA
_RGB = _HSL
_HEX = str

ColorIterator = Iterator[_HEX | _RGB | _RGBA | _HSL | _HSLA]
Color = Union[_HEX | _RGB | _RGBA | _HSL | _HSLA]
ColorBands = list[list[int]]


class IColorPalette(ABC):
    def __init__(self, color_cluster: ColorCluster):
        self._color_cluster: ColorCluster = color_cluster

    @staticmethod
    def _hexlify_rgb(rgb: RGB) -> str:
        return "#" + hexlify(bytearray(rgb)).decode("ascii")

    @abstractmethod
    def get_palette_data(self):
        pass

    @abstractmethod
    def get_palette_data_as_hex(self):
        pass


class DominantColor(IColorPalette):
    def get_palette_data(self) -> tuple[int, ...]:
        return self._color_cluster.get_colors()[0]

    def get_palette_data_as_hex(self) -> str:
        return self._hexlify_rgb(self.get_palette_data())


class RangeColorPalette(IColorPalette):
    def get_palette_data(self, stop: int, start: int = 0, step: int = 1) -> list[RGB]:
        return self._color_cluster.get_colors()[start:stop:step]

    def get_palette_data_as_hex(
        self, stop: int, start: int = 0, step: int = 1
    ) -> list[str]:
        return [
            self._hexlify_rgb(color)
            for color in self.get_palette_data(stop, start, step)
        ]


class IColor(ABC):
    """
    c = HexRGB(image)
    c.get_color_bands()
    c.make_palette()
    """

    def __init__(self, image: PIL.Image.Image) -> None:
        self.image = image

    @abstractmethod
    def get_color_bands(self) -> ColorBands:
        pass

    @staticmethod
    @abstractmethod
    def structure_raw_palette(color_bands: ColorBands) -> ColorIterator:
        pass


class HexRGB(IColor):
    def get_color_bands(self) -> ColorBands:
        return [self.image.getdata(band) for band in range(3)]

    @staticmethod
    def structure_raw_palette(color_bands: ColorBands) -> Iterator[_HEX]:
        return map(lambda *RGB: utils.rgb_to_hex(RGB), *color_bands)


class RGBA(IColor):
    def get_color_bands(self) -> ColorBands:
        return [self.image.getdata(band) for band in range(4)]

    @staticmethod
    def structure_raw_palette(color_bands: ColorBands) -> Iterator[_RGBA]:
        return map(lambda *rgba: tuple(rgba), *color_bands)
