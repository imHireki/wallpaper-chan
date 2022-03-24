#!/usr/bin/env python3
from typing import List, Union, Mapping
from io import BytesIO

from numpy import asarray, product, histogram, ndarray
from binascii import hexlify
from scipy import cluster
import PIL.Image

from utils import has_translucent_alpha, patch_alpha


class ColorCluster:
    """Manage image's color cluster.

    Args:
        image (PIL.Image.Image): The image to extract the colors.
        clusters (int): The amount of color cluster to split the image.

    Attributes:
        image_array (numpy.ndarray): The image as array.
        color_cluster (numpy.ndarray): A cluster with colors from the image.
    """

    def __init__(self, image, clusters):
        self.image_array = self.image_array(image)
        self.color_cluster = self.color_cluster(clusters)

    @property
    def incidences(self) -> ndarray:
        """Return the incidences of the cluster's colors."""

        vecs = cluster.vq.vq(self.image_array, self.color_cluster)[0]
        return histogram(vecs, len(self.color_cluster))[0]

    def image_array(self, image) -> ndarray:
        """Return the image as array."""

        ar = asarray(image)
        return ar.reshape(product(ar.shape[:2]), ar.shape[2]).astype(float)

    def color_cluster(self, clusters:int) -> ndarray:
        """Return a cluster with colors from the image."""

        return cluster.vq.kmeans2(self.image_array, clusters)[0]

    def hexify_rgb_array(self, rgb:ndarray) -> str:
        """Return the hex of the given rgb."""

        rgb_list = [int(value) for value in rgb if 256 > int(value) > 0]
        if len(rgb_list) != 3:
            return None
        return hexlify(bytearray(rgb_list)).decode('ascii')

    def hex_color(self, color_cluster=None) -> List[str]:
        """Return a list with the hex from the color cluster.

        If color_cluster wasn't specified, return the hex
        from `self.color_cluster`.

        Args:
            color_cluster (ndarray): The color cluster to be transformed as
                hex colors.
        """

        return [
            f'#{hex_rgb}' for rgb in color_cluster or self.color_cluster
            for hex_rgb in [self.hexify_rgb_array(rgb)] if hex_rgb
        ]

    @staticmethod
    def colors_incidences(colors, incidences) -> Mapping[str, int]:
        """Return a mapping with color and its incidences.

        Args:
            colors (List[str]): A list with hex colors.
            incidences (ndarray): The incidences of each hex color.
        """
        return map(lambda c, i: (c, i), colors, incidences)

    @staticmethod
    def sorted_colors(color_incidences:map) -> List[str]:
        """Return the colors sorted by its incidences.

        Args:
            color_incidences (Mapping[str, int]): The colors and
                its incidences.
        """
        return [
            _[0] for _ in sorted(
                color_incidences, key=lambda x: x[1], reverse=True
            )
        ]


class Colors:
    """Handle an ColorCluster object to get image's colors.

    Args:
        fp (Union[str, BytesIO]): The image to extract the colors.
        clusters (int): The amount of color cluster to split the image.

    Attributes:
        cc (ColorCluster): The object to get the colors.
    """

    def __init__(self, fp, clusters=5):
        self.cc = self.cc(self.image(fp), clusters)

    def cc(self, fp, clusters):
        """Return a ColorCluster object using fp and clusters."""

        with PIL.Image.open(fp) as image:
            return ColorCluster(image=image, clusters=clusters)

    def image(self, fp) -> Union[BytesIO, str]:
        """Return the fp/bytes of the image.

        Perform some validations.
        - Use the first frame of animated image.
        - Convert to RGB. Patch the alpha layer if necessary.

        FIXME: Low precision with a patched alpha layer.
        """

        with PIL.Image.open(fp) as image:
            if image.mode in ['RGBA', 'P']:

                if image.mode == 'P':
                    image = image.convert('RGBA')

                if has_translucent_alpha(image):
                    image = patch_alpha(image)

                image = image.convert('RGB')

            if image.format != 'JPEG':
                fp = BytesIO()
                image.save(fp, 'JPEG')

        return fp

    @property
    def palette(self) -> List[str]:
        """Return the color palette based on the number of clusters."""

        return self.cc.sorted_colors(
            self.cc.colors_incidences(self.cc.hex_color(), self.cc.incidences)
        )

    @property
    def dominant_color(self) -> str:
        """Return the most common color."""

        return self.palette[0]

