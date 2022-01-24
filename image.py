#!/usr/bin/env python3
from abc import ABC, abstractmethod
from io import BytesIO
from time import time

from numpy import asarray, product, histogram, argmax
from binascii import hexlify
from scipy import cluster
import PIL.Image


class Image(ABC):
    # FIXME: support to PNG and GIF
    def __init__(self, **kwargs):
        self.img: object = kwargs.get('img', None)

        self.size: tuple = kwargs.get('size', self.img.size)
        self.quality: int = kwargs.get('quality', 100)
        self.resample: object = kwargs.get('resample', PIL.Image.LANCZOS)

        self.name: str = kwargs.get('name', self.get_name())
        self.img_format: str = kwargs.get('img_format', 'jpeg')

    def get_name(self):
        """ Return a Unix epoch time with image file extension """
        return '{}.jpg'.format(round(time()))

    @abstractmethod
    def improve_consistency(self): pass

    @abstractmethod
    def resize(self): pass

    def save(self, at):
        """ Save image, on a BytesIO object or path """
        self.img.save(at,
                      format=self.img_format,
                      quality=self.quality,
                      optimize=True)


class Icon(Image):
    def improve_consistency(self):
        """ Improve the image's consistency to avoid problems
        TODO: call other functions from here, maybe also check the image here
        """

        # Create a white image with the same size as the image
        white_background = PIL.Image.new(
            mode='RGBA',
            size=self.img.size,
            color=(255, 255, 255)
            )

        # Patch the alpha layer with the white_background and convert to RGB
        self.img = PIL.Image.alpha_composite(
            im1=white_background,
            im2=self.img
            ).convert('RGB')

    def resize(self):
        """ Perform the resize of the image """
        self.img = self.img.resize(
            size=self.size,
            resample=self.resample,
            reducing_gap=2.0
            )


class Wallpaper(Image): pass


class ImageFactory:
    """ Factory of Image classes """

    @staticmethod
    def for_icon(**kwargs):
        """ Return icon instance """
        return Icon(**kwargs)

    @staticmethod
    def for_wallpaper(): pass


class ImageColor:
    def __init__(self, **kwargs):
        self.img = kwargs.get('img', None)
        self.img_asarray = self.get_image_asarray()
        self.color_cluster = self.get_color_cluster(kwargs.get('clusters'))

    def get_image_asarray(self):
        """ Return the image as array """
        ar = asarray(self.img)
        shape = ar.shape
        return ar.reshape(product(shape[:2]),
                          shape[2]).astype(float)

    def get_color_cluster(self, clusters:int):
        """ Return the cluster of colors """
        return cluster.vq.kmeans(self.img_asarray, clusters)[0]

    def get_dominant_color(self, color_incidences):
        """ Return the most common color """
        index_max = argmax(color_incidences)
        peak = self.color_cluster[index_max]
        return peak

    def get_incidences(self):
        """ Return the color's incidences """
        vecs = cluster.vq.vq(self.img_asarray, self.color_cluster)[0]
        return histogram(vecs, len(self.color_cluster))[0]

    def get_hex(self, cluster=None) -> list:
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
    def get_colors_incidences(colors, incidences):
        """ Return list with colors and its incidences """

        # Put it all back together as [ ('color', 'incidences'), ]
        return [ (x, y)
                 for a, b in enumerate(colors)
                 for x, y in [
                     (colors[a], incidences[a])
                     ]
                 ]

    @staticmethod
    def get_sorted_colors(color_incidences):
        """ Return sorted colors by its incidences """

        # sort color_incidences by its numbers of incidences
        sorted_color_incidences = sorted(color_incidences,
                                         key=lambda x: x[1],
                                         reverse=True)
        # Return just the colors
        return [_[0] for _ in sorted_color_incidences]


class GetColors:
    def __init__(self, image, clusters=5):
        self.ic = ImageColor(img=image, clusters=clusters)

    def get_palette(self):
        """ Return the color palette """
        hex_colors = self.ic.get_hex()
        incidences = self.ic.get_incidences()
        colors_incidences = self.ic.get_colors_incidences(hex_colors, incidences)
        return self.ic.get_sorted_colors(colors_incidences)

    def get_dominant_color(self):
        """ Return the most common color """
        incidences = self.ic.get_incidences()
        dominant = self.ic.get_dominant_color(incidences)
        return self.ic.get_hex([dominant])[0]


if __name__ == '__main__':
    with PIL.Image.open('xd') as img:
        # # -- Color --
        # color = GetColors(img)
        # palette = color.get_palette()
        # dc = color.get_dominant_color()

        # # -- Resize --
        # icon = ImageFactory.for_icon(img=img, size=(512,512))
        # if img.mode == 'RGBA':
        #     icon.improve_consistency()
        # icon.resize()

        # # -- Save To Stream --
        # b_img = BytesIO()
        # icon.save(b_img)

        # # -- Save To File --
        # icon.save('path/to/file.jpg')
        ...
