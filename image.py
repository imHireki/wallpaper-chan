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
        return '{}.jpg'.format(round(time()))

    @abstractmethod
    def handle_rgba(self) -> None: pass

    @abstractmethod
    def resize(self) -> None: pass

    def save(self, at) -> None:
        """ Save image, on a BytesIO object or path """
        self.img.save(at,
                      format=self.img_format,
                      quality=self.quality,
                      optimize=True)


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


class Wallpaper(Image): pass


class ImageFactory:
    """ Image Factory returns a specific Image class """

    @staticmethod
    def for_icon(**kwargs):
        return Icon(**kwargs)

    @staticmethod
    def for_wallpaper(): pass


class ImageColor:
    def __init__(self, **kwargs):
        self.img = kwargs.get('img', None)
        self.img_asarray = self.get_image_asarray()
        self.color_cluster = self.get_color_cluster(kwargs.get('clusters'))

    def get_image_asarray(self):
        ar = asarray(self.img)
        shape = ar.shape
        return ar.reshape(product(shape[:2]),
                          shape[2]).astype(float)

    def get_color_cluster(self, clusters:int):
        return cluster.vq.kmeans(self.img_asarray, clusters)[0]

    def get_dominant_color(self, color_incidences):
        index_max = argmax(color_incidences)
        peak = self.color_cluster[index_max]
        return peak

    def get_incidences(self):
        vecs = cluster.vq.vq(self.img_asarray, self.color_cluster)[0]
        return histogram(vecs, len(self.color_cluster))[0]

    def get_hex(self, cluster=None) -> list:
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


class GetColors:
    def __init__(self, image, clusters=5):
        self.ic = ImageColor(img=image, clusters=clusters)

    def get_palette(self):
        hex_colors = self.ic.get_hex()
        incidences = self.ic.get_incidences()
        colors_incidences = self.ic.get_colors_incidences(hex_colors, incidences)
        return self.ic.get_sorted_colors(colors_incidences)

    def get_dominant_color(self):
        incidences = self.ic.get_incidences()
        dominant = self.ic.get_dominant_color(incidences)
        return self.ic.get_hex([dominant])


if __name__ == '__main__':
    with PIL.Image.open(':D') as img:
        """
        -- Color --
        color = GetColors(img)
        palette = color.get_palette()
        dc = color.get_dominant_color()

        -- Resize --
        icon = ImageFactory.for_icon(img=img)
        if img.mode == 'RGBA':
            icon.handle_rgba()
        icon.resize()

            -- Save To Stream --
            b_img = BytesIO()
            icon.save(b_img)

            -- Save To File --
            icon.save('path/to/file.jpg')
        """
