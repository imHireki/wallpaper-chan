#!/usr/bin/env python3
from numpy import asarray, product, histogram, argmax
from binascii import hexlify
from scipy import cluster
import PIL.Image


class ImageColor:
    def __init__(self, image, clusters):
        self.image_array = self.image_array(image)
        self.color_cluster = self.color_cluster(clusters)

    @property
    def incidences(self):
        """ Return the color's incidences """
        vecs = cluster.vq.vq(self.image_array, self.color_cluster)[0]
        return histogram(vecs, len(self.color_cluster))[0]

    def image_array(self, image):
        ar = asarray(image)
        return ar.reshape(product(ar.shape[:2]), ar.shape[2]).astype(float)

    def color_cluster(self, clusters):
        return cluster.vq.kmeans2(self.image_array, clusters)[0]

    def hexify_rgb_array(self, rgb):
        rgb_list = [int(value) for value in rgb if 256 > int(value) > 0]
        if len(rgb_list) != 3:
            return None
        return hexlify(bytearray(rgb_list)).decode('ascii')

    def hex_color(self, cluster=None):
        return [
            f'#{hex_rgb}' for rgb in cluster or self.color_cluster
            for hex_rgb in [self.hexify_rgb_array(rgb)] if hex_rgb
        ]

    def dominant_color(self, color_incidences):
        """ Return the most common color """
        return self.color_cluster[argmax(color_incidences)]

    @staticmethod
    def colors_incidences(colors, incidences):
        return map(lambda c, i: (c, i), colors, incidences)

    @staticmethod
    def sorted_colors(color_incidences):
        """ Return sorted colors by its incidences """
        return [
            _[0]
            for _ in sorted(color_incidences, key=lambda x: x[1], reverse=True)
        ]


class Colors:
    """Handle an ImageColor object to get image's colors.

    Args:
        image (PIL.Image.Image): The image to extract the colors.
        clusters (int): The amount of color cluster to split the image.

    Attributes:
        ic (ImageColor): The object to get the colors.
    """

    def __init__(self, image, clusters=10):
        self.ic = ImageColor(image=image, clusters=clusters)

    @property
    def palette(self):
        """Return the color palette based on the number of clusters."""
        return self.ic.sorted_colors(
            self.ic.colors_incidences(self.ic.hex_color(), self.ic.incidences)
        )

    @property
    def dominant_color(self):
        """Return the most common color."""
        return self.ic.hex_color(
            [self.ic.dominant_color(self.ic.incidences)]
        )[0]

