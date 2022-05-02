#!/usr/bin/env python3
from typing import List

import PIL.Image

from . import image


def has_translucent_alpha(image) -> bool:
    """Return wether or not the alpha channel is translucent."""

    return True if image.getextrema()[-1][0] < 255 else False

def open(fp, mode="r", formats=None) -> PIL.Image.Image:
    """Open and identify the given image."""

    return PIL.Image.open(fp, mode, formats)

def is_animated(image) -> bool:
    """Return whether or not the image has multiple frames."""

    return getattr(image, 'is_animated', False)

def patch_alpha(image) -> PIL.Image.Image:
    """Return the image without the alpha layer."""

    return PIL.Image.alpha_composite(
        im1=PIL.Image.new('RGBA', image.size, '#ffffff'),
        im2=image
    )


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
            if isinstance(obj, image.AnimatedIcon):
                self.resize_save_animated(obj)
            else:
                self.resize_save(obj)
            yield obj.fp

