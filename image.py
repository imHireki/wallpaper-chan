#!/usr/bin/env python3
from abc import ABC, abstractmethod
from io import BytesIO
from time import time

from numpy import asarray, product, histogram, argmax
from binascii import hexlify
from scipy import cluster
import PIL.Image


class _Image(ABC):
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


class Icon(_Image):
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


class Wallpaper(_Image): pass


class Image:
    """ Factory of Image classes """

    @staticmethod
    def icon(**kwargs):
        """ Return icon instance """
        return Icon(**kwargs)

    @staticmethod
    def wallpaper(): pass


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


class GetColors:
    def __init__(self, image, clusters=5):
        self.ic = ImageColor(img=image, clusters=clusters)

    def palette(self):
        """ Return the color palette """
        hex_colors = self.ic.hex_color()
        incidences = self.ic.incidences()
        colors_incidences = self.ic.colors_incidences(hex_colors, incidences)
        return self.ic.sorted_colors(colors_incidences)

    def dominant_color(self):
        """ Return the most common color """
        incidences = self.ic.incidences()
        dominant = self.ic.dominant_color(incidences)
        return self.ic.hex_color([dominant])[0]

class Bulk:
    def __init__(self, objs):
        self.objs = objs

    def resize(self, path=''):
        """ Resize image objects as a batch

        path -- the path for save the image (default: '')
        """
        batch = []

        for obj in self.objs:
            if obj.img.mode == 'RGBA':
                obj.improve_consistency()

            obj.resize()

            if path:
               obj.save('{}{}.jpg'.format(path, obj.name))

            bytes_img = BytesIO()
            obj.save(bytes_img)
            batch.append(bytes_img)

        return batch


if __name__ == '__main__':
    with PIL.Image.open('xd') as img:

        # images = Bulk([
        #     Image.icon(img=img, size=size)
        #     for size in [(512, 512),
        #                  (256, 256),
        #                  (128, 128),
        #                  (80 , 80 )]
        # ]).resize()

        # # -- Color --
        # color = GetColors(img)
        # palette = color.palette()
        # dc = color.dominant_color()

        # # -- Resize --
        # icon = Image.icon(img=img, size=(512,512))
        # if img.mode == 'RGBA':
        #     icon.improve_consistency()
        # icon.resize()

        # -- Save To Stream --
        # b_img = BytesIO()
        # icon.save(b_img)
        # -- Save To File --
        # icon.save('k.jpg')
        ...
