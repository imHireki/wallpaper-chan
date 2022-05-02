#!/usr/bin/env python3
from typing import List, Union, Mapping, Generator, Dict, Tuple, Iterable
from binascii import hexlify

import PIL.Image

from . import exceptions
from . import utils


class ColorCluster:
    """Manage the image's color cluster.

    Args:
        image (PIL.Image.Image): The image to extract the colors.

    Attributes:
        image (PIL.Image.Image): The image to extract the colors.
    """

    def __init__(self, image):
        self.image = image

    @property
    def image_rgb(self) -> Tuple[Iterable]:
        """The red, green and blue iterable for each image's pixels."""

        red, green, blue = [self.image.getdata(band) for band in range(3)]
        return red, green, blue

    @property
    def cluster(self) -> Mapping[Tuple[Iterable], Tuple[int]]:
        """The color cluster of the image."""

        return map(lambda r, g, b: (r, g, b), *self.image_rgb)

    def color_incidences(self) -> Dict[Tuple[int], int]:
        """Return the RGB assigned to its incidences."""

        color_incidences = {}

        for rgb in self.cluster:
            if rgb not in color_incidences:
                color_incidences[rgb] = 1
            else:
                color_incidences[rgb] += 1
        return color_incidences

    def sorted_colors(self) -> List[Tuple[int]]:
        """Return the colors sorted by its incidences."""

        return [
            ci[0] for ci in sorted(self.color_incidences().items(),
                                   key=lambda ci: ci[1],
                                   reverse=True)
        ]

    def hexlify_rgb(self, rgb:Tuple[int]) -> str:
        """Return the RGB converted to HEX.

        Args:
            rgb: A tuple with red, green and blue values.
        """

        return hexlify(bytearray(rgb)).decode('ascii')

    def hexlify_cluster(self, cluster) -> List[str]:
        """Return a list with the HEX from the cluster's RGBs.

        Args:
            cluster List[Tuple[int]]: A list with RGBs.
        """

        return [f'#{hex}' for rgb in cluster for hex in [self.hexlify_rgb(rgb)]]


class Colors:
    """Control a ColorCluster object to get image's colors.

    Attributes:
        _image (PIL.Image.Image): The image to extract the colors.
        cc (ColorCluster): The object to get the colors.
    """

    def __init__(self, image):
        self._image = image
        self.cc = self.image

    @property
    def image(self):
        """Return a valid image."""

        if self._image.mode == 'P':
            self._image = self._image.convert('RGBA')
        return self._image

    @property
    def cc(self):
        """Return a ColorCluster object for the image."""

        return self._cc

    @cc.setter
    def cc(self, image):
        self._cc = ColorCluster(image)

    def palette(self) -> List[str]:
        """Return the color palette."""

        return self.cc.hexlify_cluster(self.cc.sorted_colors()[:25:5])

    def dominant_color(self) -> str:
        """Return the most common color."""

        return self.cc.hexlify_cluster([self.cc.sorted_colors()[0]])

