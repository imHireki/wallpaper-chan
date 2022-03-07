#!/usr/bin/env python3
from numpy import asarray, product, histogram, argmax
from binascii import hexlify
from scipy import cluster


class ImageColor:
    def __init__(self, **kwargs):
        self.img = kwargs.get('img', None)
        self.img_asarray = self.image_as_array()
        self.color_cluster = self.color_cluster(kwargs.get('clusters'))

    def image_as_array(self):
        """ Return the image as array """
        ar = asarray(self.img)
        shape = ar.shape
        return ar.reshape(product(shape[:2]),
                          shape[2]).astype(float)

    def color_cluster(self, clusters:int):
        """ Return the cluster of colors """
        return cluster.vq.kmeans(self.img_asarray, clusters)[0]

    def dominant_color(self, color_incidences):
        """ Return the most common color """
        index_max = argmax(color_incidences)
        peak = self.color_cluster[index_max]
        return peak

    def incidences(self):
        """ Return the color's incidences """
        vecs = cluster.vq.vq(self.img_asarray, self.color_cluster)[0]
        return histogram(vecs, len(self.color_cluster))[0]

    def hex_color(self, cluster=None) -> list:
        """ Return the color cluster converted to hex """
        if not cluster: cluster = self.color_cluster
        return [
            '#' +
            str(hexlify(bytearray((int(_) for _ in color))
                        ).decode('ascii')
                )
            for color in cluster
        ]

    @staticmethod
    def colors_incidences(colors, incidences):
        """ Return list with colors and its incidences """

        # Put it all back together as [ ('color', 'incidences'), ]
        return [ (x, y)
                 for a, b in enumerate(colors)
                 for x, y in [
                     (colors[a], incidences[a])
                     ]
                 ]

    @staticmethod
    def sorted_colors(color_incidences):
        """ Return sorted colors by its incidences """

        # sort color_incidences by its numbers of incidences
        sorted_color_incidences = sorted(color_incidences,
                                         key=lambda x: x[1],
                                         reverse=True)
        # Return just the colors
        return [_[0] for _ in sorted_color_incidences]
