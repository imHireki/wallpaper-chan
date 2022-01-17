#!/usr/bin/env python3
from django.core.files.images import File, ImageFile
from io import BytesIO
from abc import ABC, abstractmethod
from time import time

from numpy import asarray, product, histogram, argmax
from binascii import hexlify
from scipy import cluster
import PIL.Image


class Image(ABC):
    # FIXME: add support to PNG and GIF
    def __init__(self, **kwargs):
        self.img: object = kwargs.get('img', None)

        self.size: tuple = kwargs.get('size', (512, 512))
        self.quality: int = kwargs.get('quality', 100)
        self.resample: object = kwargs.get('resample', PIL.Image.LANCZOS)

        self.name: str = kwargs.get('name', self.get_name())
        self.img_format: str = kwargs.get('img_format', 'jpeg')

    @staticmethod
    def get_name():
        return '{}.jpg'.format(round(time()))

    @abstractmethod
    def handle_rgba(self) -> None: pass

    @abstractmethod
    def resize(self) -> None: pass

    @abstractmethod
    def save(self) -> File: pass

    def perform_actions(self) -> File:
        """ Perform actions without modify other funcitions
            - mainly used to get dominant color when resizing
              the smaller image

        TODO: add full support to RGBA images
        """
        if self.img.mode == 'RGBA':
            self.handle_rgba()
        self.resize()
        return self.save() # File


class Icon(Image):
    def handle_rgba(self) -> None:
        """ Add opaque white background to the alpha layer """
        white_background = PIL.Image.new(
            mode='RGBA',
            size=self.img.size,
            color=(255, 255, 255)
            )

        self.img = PIL.Image.alpha_composite(
            im1=white_background,
            im2=self.img
            ).convert('RGB')

    def resize(self) -> None:
        """ Resize self.image with `self.size` & `self.resample` """
        self.img = self.img.resize(
            size=self.size,
            resample=self.resample,
            reducing_gap=2.0
            )

    def save(self) -> File:
        """ Save `self.image` & return its File
            FIXME: return & handle a better object than django's File
        """
        img_io = BytesIO()
        img_file = File(img_io, name=self.name)

        self.img.save(img_io,
                      format=self.img_format,
                      quality=self.quality,
                      optimize=True)

        return img_file


class Wallpaper(Image): pass


class ImageFactory:
    """ Image Factory returns a specific Image class """

    @staticmethod
    def for_icon(**kwargs): return Icon(**kwargs)

    @staticmethod
    def for_wallpaper(): pass


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

        icon = ImageFactory.for_icon(img=img,
                                     size=(128, 128))
        icon.perform_actions()
