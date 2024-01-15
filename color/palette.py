from abc import ABC, abstractmethod
from binascii import hexlify

from color.cluster import ColorCluster, RGB


class IColorPalette(ABC):
    def __init__(self, color_cluster: ColorCluster):
        self._color_cluster: ColorCluster = color_cluster

    @staticmethod
    def _hexlify_rgb(rgb: RGB)-> str:
        return '#' + hexlify(bytearray(rgb)).decode('ascii')

    @abstractmethod
    def get_palette_data(self): pass

    @abstractmethod
    def get_palette_data_as_hex(self): pass


class DominantColor(IColorPalette):
    def get_palette_data(self) -> tuple[int, ...]:
        return self._color_cluster.get_colors()[0]

    def get_palette_data_as_hex(self) -> str:
        return self._hexlify_rgb(self.get_palette_data())


class RangeColorPalette(IColorPalette):
    def get_palette_data(self, stop: int, start: int = 0,
                         step: int = 1) -> list[RGB]:
        return self._color_cluster.get_colors()[start:stop:step]

    def get_palette_data_as_hex(self, stop: int, start: int = 0,
                                step: int = 1) -> list[str]:
        return [
            self._hexlify_rgb(color)
            for color in self.get_palette_data(stop, start, step)
        ]
