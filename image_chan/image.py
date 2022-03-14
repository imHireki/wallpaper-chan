#!/usr/bin/env python3
from typing import Tuple, Dict, List, Union
from abc import ABC, abstractmethod
from io import BytesIO

import PIL.Image, PIL.ImageSequence

from .exception import ImageSupportError


def open(fp, mode="r", formats=None):
    return PIL.Image.open(fp, mode, formats)

def is_animated(image):
    return getattr(image, 'is_animated', False)


class Image:
    def __init__(self, image, size, format='WEBP', fp=None):
        self.image = image
        self.size = size
        self.format = format
        self.fp = fp

    @property
    def fp(self):
        return self._fp

    @fp.setter
    def fp(self, fp):
        self._fp = fp if fp else BytesIO()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

        if not self.is_supported:
            raise ImageSupportError(
                f'Image {self.image.format, self.image.mode}'
                f'not in {self.SUPPORTED_IMAGES}'
                )

        # Has alpha channel without using translucency.
        if self.image.mode == 'RGBA' and not self.has_translucent_alpha:
            self.image = self.image.convert(mode='RGB')

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, format):
        if isinstance(format, (tuple, list)) and len(format) > 1:
            # Set the best format, if more than one was specified.
            if self.is_animated and 'GIF' in format:
                self._format = 'GIF'

            elif self.image.mode == 'RGBA' and 'PNG' in format:
                self._format = 'PNG'

            elif self.image.mode == 'RGB' and 'JPEG' in format:
                self._format = 'JPEG'
        else:
            self._format = format

    @property
    def is_supported(self):
        if not self.image.mode in self.SUPPORTED_MODES:
            return False

        if self.image.format:
            if not self.image.format in self.SUPPORTED_FORMATS:
                return False

        return True

    @property
    def is_animated(self):
        return is_animated(self.image)

    @property
    def has_translucent_alpha(self):
        """Return True if alpha isn't opaque."""
        return True if self.image.getextrema()[-1][0] < 255 else False

    def resize(self):
        """Resize the image."""
        self.image = self.image.resize(
            self.size, self.RESAMPLE, reducing_gap=self.REDUCING_GAP
            )

    def save(self, **params):
        """Save the image on a BytesIO object or path."""
        self.image.save(
            self.fp, self.format, quality=self.QUALITY, optimize=True, **params
            )


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


class Bulk:
    def __init__(self, objs):
        self.objs = objs

    def resize(self, path=''):
        """ Resize image objects as a batch
        Return its bytes objects, if path is specified, also save it.

        path -- the path for save the image (default: '')
        """
        batch = []

        for obj in self.objs:
            if obj.img.mode == 'RGBA':
                obj.improve_consistency()

            obj.resize()

            if path:
               obj.save('{}{}'.format(path, obj.name))

            bytes_img = BytesIO()
            obj.save(bytes_img)
            batch.append(bytes_img)

        return batch

