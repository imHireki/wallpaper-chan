#!/usr/bin/env python3
from typing import List, Union, Mapping, Generator

from binascii import hexlify
import PIL.Image

import utils


class ColorCluster:
    """Manage image's color cluster."""

    def __init__(self, image):
        self.image_rgb = self.image_rgb(image)

    def image_rgb(self, image):
        red, green, blue = [image.getdata(band) for band in range(3)]
        return red, green, blue

    @property
    def cluster(self) -> Mapping:
        """Return a RGB color cluster."""

        return map(lambda r, g, b: (r, g, b), *self.image_rgb)

    @property
    def color_incidences(self):
        """Return the color and its incidences"""

        color_incidences = {}
        for rgb in self.cluster:
            if rgb not in color_incidences:
                color_incidences[rgb] = 1
            else:
                color_incidences[rgb] += 1
        return color_incidences

    @staticmethod
    def sorted_colors(color_incidences) -> List[str]:
        """Return the colors sorted by its incidences.

        Args:
            color_incidences (Mapping[str, int]): The colors and
                its incidences.
        """
        return [
            x[0] for x in sorted(color_incidences.items(),
                                 key=lambda x: x[1],
                                 reverse=True)
        ]

    def hexify_rgb(self, rgb) -> str:
        """Return the hex of the given rgb."""

        return hexlify(bytearray(rgb)).decode('ascii')

    def hex_color(self, cluster) -> List[str]:
        """Return a list with the hex from the color cluster.

        If color_cluster wasn't specified, return the hex
        from `self.color_cluster`.

        Args:
            color_cluster (ndarray): The color cluster to be transformed as
                hex colors.
        """

        return [
            f'#{hex_rgb}' for rgb in cluster
            for hex_rgb in [self.hexify_rgb(rgb)]
        ]


class Colors:
    """Handle an ColorCluster object to get image's colors.

    Args:
        clusters (int): The amount of color cluster to split the image.

    Attributes:
        cc (ColorCluster): The object to get the colors.
    """

    def __init__(self, image):
        self.cc = self.cc(self.image(image))

    def cc(self, image):
        """Return a ColorCluster object using fp and clusters."""

        return ColorCluster(image=image)

    def image(self, image):
        if image.mode == 'P':
            image = image.convert('RGBA')
        return image

    def palette(self, amount) -> List[str]:
        """Return the color palette based on the number of clusters."""

        x = self.cc.sorted_colors(self.cc.color_incidences)[:amount]
        return self.cc.hex_color(x)

    @property
    def dominant_color(self) -> str:
        """Return the most common color."""

        x = [self.cc.sorted_colors(self.cc.color_incidences)[0]]
        return self.cc.hex_color(x)

