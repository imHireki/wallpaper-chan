#!/usr/bin/env python3
from typing import List
import PIL.Image
from image import AnimatedIcon, Icon, is_animated, open


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

