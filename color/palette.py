from abc import ABC, abstractmethod
from binascii import hexlify

from .cluster import ColorCluster


class IColorPalette(ABC):
    _color_cluster: ColorCluster

    def __init__(self, color_cluster: ColorCluster):
        self._color_cluster = color_cluster

    @staticmethod
    def _hexlify_rgb(rgb: tuple[int]) -> str:
        return '#' + hexlify(bytearray(rgb)).decode('ascii')

    @abstractmethod
    def get_palette_data(self): pass

    @abstractmethod
    def get_palette_data_as_hex(self): pass

