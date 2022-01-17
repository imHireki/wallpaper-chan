#!/usr/bin/env python3
from numpy import asarray, product, histogram, argmax
from binascii import hexlify
from scipy import cluster
import PIL.Image


class ImageColor:
    def __init__(self, **kwargs):
        self.img = kwargs.get('img', None)

    def get_color_cluster(self, clusters:int):
        ar = asarray(self.img)
        shape = ar.shape
        ar = ar.reshape(product(shape[:2]),
                        shape[2]).astype(float)

        self.image_asarray = ar
        return cluster.vq.kmeans(ar, clusters)[0]

    def get_incidences(self, color_cluster):
        vecs = cluster.vq.vq(self.image_asarray, color_cluster)[0]
        return histogram(vecs, len(color_cluster))[0]

    @staticmethod
    def get_hex(color_cluster) -> list:
        return [
            '#' +
            str(hexlify(bytearray((int(_) for _ in color))
                        ).decode('ascii')
                )
            for color in color_cluster
        ]

    @staticmethod
    def get_colors_incidences(colors, incidences):
        # Put it all back together as [ ('color', 'incidents'), ]
        return [ (x, y)
                 for a, b in enumerate(colors)
                 for x, y in [
                     (colors[a], incidences[a])
                     ]
                 ]

    @staticmethod
    def get_sorted_colors(color_incidences):
        # Sort the color_incidences by its incidences in descending order
        sorted_color_incidences = sorted(color_incidences,
                                         key=lambda x: x[1],
                                         reverse=True)

        return [_[0] for _ in sorted_color_incidences]

    @staticmethod
    def get_dominant_color(cluster, color_incidences):
        index_max = argmax(color_incidences)
        peak = cluster[index_max]
        return peak


class GetColors:
    def __init__(self, image):
        self.ic = ImageColor(img=image)

    def get_palette(self, amount=5):
        color_cluster = self.ic.get_color_cluster(amount)

        hex_colors = self.ic.get_hex(color_cluster)
        incidences = self.ic.get_incidences(color_cluster)

        colors_incidences = self.ic.get_colors_incidences(hex_colors, incidences)
        return self.ic.get_sorted_colors(colors_incidences)

    def get_dominant_color(self, precision=5):
        color_cluster = self.ic.get_color_cluster(precision)
        incidences = self.ic.get_incidences(color_cluster)
        dominant = self.ic.get_dominant_color(color_cluster, incidences)
        return self.ic.get_hex([dominant])


if __name__ == '__main__':
    with PIL.Image.open('vimgirl.jpg') as img:
        color = GetColors(img)

        print(color.get_palette())
        print(color.get_dominant_color())
