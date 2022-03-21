#!/usr/bin/env python3
from typing import Tuple, Dict, List, Union, Generator
from io import BytesIO

import PIL.Image, PIL.ImageSequence

from exception import ImageSupportError


def open(fp, mode="r", formats=None):
    """Open and identify the given image."""

    return PIL.Image.open(fp, mode, formats)

def is_animated(image):
    """Return whether or not the image has multiple frames."""

    return getattr(image, 'is_animated', False)


class Options:
    RESAMPLE:int = 0
    REDUCING_GAP:float = 0.0
    QUALITY:int = 100
    SUPPORTED_IMAGES:Dict[str, tuple] = {}

    def add_defaults(self, options):
        self.RESAMPLE = getattr(options, 'RESAMPLE', self.RESAMPLE)
        self.REDUCING_GAP = getattr(options, 'REDUCING_GAP', self.REDUCING_GAP)
        self.QUALITY = getattr(options, 'QUALITY', self.QUALITY)
        self.SUPPORTED_IMAGES = getattr(
            options, 'SUPPORTED_IMAGES', self.SUPPORTED_IMAGES
        )

    def supported_modes(self) -> list[str]:
        """Return the supported modes from the SUPPORTED_IMAGES constant."""

        return list(self.SUPPORTED_IMAGES.keys())

    def supported_formats(self) -> List[str]:
        """Return the supported formats from the SUPPORTED_IMAGES constant."""

        return self.SUPPORTED_IMAGES.get(self.image.mode)


class Info:
    def is_supported(self) -> bool:
        """Return whether or not the image is supported."""

        if not self.image.mode in self.supported_modes():
            return False

        if self.image.format:
            if not self.image.format in self.supported_formats():
                return False
        return True

    def is_animated(self) -> bool:
        """Return whether or not the image has multiple frames."""

        return is_animated(self.image)

    def has_translucent_alpha(self) -> bool:
        """Return wether or not the alpha channel is translucent."""

        return True if self.image.getextrema()[-1][0] < 255 else False


class Image(Options, Info):
    """Manage the image.

    Check whether the class has support for the image.
    Perform resize, save and convert the format and mode, if necessary.

    Args:
        image (PIL.Image.Image): An opened image with `open()`.
        size (Tuple[int, int]): The size to resize the image.
        format (str): The format to save the image. Default to 'WEBP'.
        fp (Union[str, BytesIO]): The file path to save the image or a
            BytesIO object. Default to None.

    Attributes:
        size (Tuple[int, int]): The size to resize the image.
    """

    def __init__(self, image, size, format='WEBP', fp=None):
        self.add_defaults(self)
        self.image = image
        self.size = size
        self.format = format
        self.fp = fp

    @property
    def image(self) -> PIL.Image.Image:
        """The image to perform the actions."""

        return self._image

    @image.setter
    def image(self, image):
        self._image = image
        if not self.is_supported():
            raise ImageSupportError(
                f'Image {self.image.format, self.image.mode}'
                f'not in {self.SUPPORTED_IMAGES}'
                )

        # Has alpha channel without using translucency.
        if self.image.mode == 'RGBA' and not self.has_translucent_alpha():
            self.image = self.image.convert(mode='RGB')

    @property
    def fp(self) -> Union[str, BytesIO]:
        """The file path or BytesIO object to save the image."""

        return self._fp

    @fp.setter
    def fp(self, fp):
        self._fp = fp if fp else BytesIO()

    @property
    def format(self) -> str:
        """The format to save the image."""

        return self._format

    @format.setter
    def format(self, format):
        # Set the best format, if more than one was specified.
        if isinstance(format, (tuple, list)) and len(format) > 1:
            if self.is_animated() and 'GIF' in format:
                self._format = 'GIF'
            elif self.image.mode == 'RGBA' and 'PNG' in format:
                self._format = 'PNG'
            elif self.image.mode == 'RGB' and 'JPEG' in format:
                self._format = 'JPEG'
            else:
                self._format = 'WEBP'
        else:
            self._format = format

    def resize(self):
        """Perform resize on the image.

        Use `size`, `RESAMPLE` and `REDUCING_GAP` attr as parameters to
        resize the `image`.
        """

        self.image = self.image.resize(
            self.size, self.RESAMPLE, reducing_gap=self.REDUCING_GAP
            )

    def save(self, **params):
        """Save the image.

        Use `fp`, `format`, `QUALITY` and params, if present, to save
        the image.

        Args:
            params: The extra kwargs to save the image.
        """

        self.image.save(
            self.fp, self.format, quality=self.QUALITY, optimize=True, **params
            )


class Wallpaper(Image):
    """Wallpaper options."""
    RESAMPLE = 2
    REDUCING_GAP = 2.0

    QUALITY = 75

    SUPPORTED_IMAGES = {
        'RGB': ('JPEG', 'PNG'),
        'RGBA': ('PNG',),
    }


class Icon(Image):
    """Icon options."""

    RESAMPLE = 1
    REDUCING_GAP = 2.0

    QUALITY = 70

    SUPPORTED_IMAGES = {
        'RGB': ('JPEG', 'PNG', 'WEBP', 'GIF'),
        'RGBA': ('PNG', 'GIF', 'WEBP'),
        'P': ('GIF',)
    }


class AnimatedIcon(Icon):
    """Add support to images with multiple frames."""

    def resize_frames(self):
        """Generate the frame sequence resized."""
        for frame in PIL.ImageSequence.Iterator(self.image):
            self.image = frame
            self.resize()
            yield self.image

    def save_frames(self, frames:Generator):
        """Save all the frames into the first one."""
        first_image = next(frames)
        frames = list(frames)

        self.image = first_image
        self.save(loop=0, save_all=True, append_images=frames)


class BulkResize:
    """Resize all the given image objects.

    Args:
        objects: A list of images to resize.
    """

    def __init__(self, objects:List[PIL.Image.Image]):
        self.objects = objects

    def resize_save(self, obj:PIL.Image.Image):
        """Resize and save the obj."""

        obj.resize()
        obj.save()

    def resize_save_animated(self, obj:PIL.Image.Image):
        """Resize and save the obj, as multiples frames."""

        resized_frames = obj.resize_frames()
        obj.save_frames(resized_frames)

    @property
    def batch(self):
        """Return the fp of all the resized objects."""

        for obj in self.objects:
            if isinstance(obj, AnimatedIcon):
                self.resize_save_animated(obj)
            else:
                self.resize_save(obj)
            yield obj.fp




if __name__ == '__main__':
    with open('gordo.jpg') as image:

        images = BulkResize([
            Icon(image=image, size=size, format=format)
            if not is_animated(image) else
            AnimatedIcon(image=image, size=size, format=format)

            for size, format in [
                ((256, 256), 'WEBP'),
                #(image.size, ('JPEG', 'PNG', 'GIF'))
                ]
        ]).batch

        # for x in images:
        #     with open(x) as i:
        #         i.show(0)

        print([x for x in images])
