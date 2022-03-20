#!/usr/bin/env python3
from numpy import asarray, product, histogram, argmax
from binascii import hexlify
from scipy import cluster


class ImageColor:
    def __init__(self, image, clusters):
        self.image_array = self._image_array(image)
        self.color_cluster = self._color_cluster(clusters)

    def _image_array(self, image):
        ar = asarray(image)
        return ar.reshape(product(ar.shape[:2]), ar.shape[2]).astype(float)

    def _color_cluster(self, clusters):
        return cluster.vq.kmeans2(self.image_array, clusters)[0]

    @property
    def incidences(self):
        """ Return the color's incidences """
        vecs = cluster.vq.vq(self.image_array, self.color_cluster)[0]
        return histogram(vecs, len(self.color_cluster))[0]

    def hexify_rgb_array(self, rgb):
        # remove bytearray problems
        rgb_list = [int(value) for value in rgb if 256 > int(value) > 0]
        if len(rgb_list) != 3:
            return None
        return hexlify(bytearray(rgb_list)).decode('ascii')

    def hex_color(self, cluster=None):
        # Remove None
        return [
            f'#{hex_rgb}' for rgb in cluster or self.color_cluster
            for hex_rgb in [self.hexify_rgb_array(rgb)] if hex_rgb
        ]

    def dominant_color(self, color_incidences):
        """ Return the most common color """
        return self.color_cluster[argmax(color_incidences)]

    def colors_incidences(self, colors, incidences):
        """ Return list with colors and its incidences
        Put it all back together as [ ('color', 'incidences'), ]
        """
        return map(self.attach_colors_incidences, colors, incidences)

    @staticmethod
    def attach_colors_incidences(colors, incidences):
         return (colors, incidences)

    @staticmethod
    def sorted_colors(color_incidences):
        """ Return sorted colors by its incidences """
        return [
            _[0]
            for _ in sorted(color_incidences, key=lambda x: x[1], reverse=True)
        ]


class Colors:
    def __init__(self, image, clusters=10):
        self.ic = ImageColor(image=image, clusters=clusters)

    def palette(self):
        """ Return the color palette """
        return self.ic.sorted_colors(
            self.ic.colors_incidences(self.ic.hex_color(), self.ic.incidences)
        )

    def dominant_color(self):
        """ Return the most common color """
        return self.ic.hex_color(
            [self.ic.dominant_color(self.ic.incidences)]
        )[0]

