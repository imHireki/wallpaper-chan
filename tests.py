#!/usr/bin/env python3
import unittest

import PIL.Image
from sys import stdout
from io import BytesIO
from image import Icon, Image
from exceptions import ImageSupportError


class DummyImage:
    def create_image(self, mode, format):
        image = PIL.Image.new(mode, (25, 25))
        obj = BytesIO()
        image.save(obj, format)
        return obj

    def create_animated_image(self, mode, format):
        frames = (PIL.Image.new(mode, (25, 25)) for x in range(5))
        image = next(frames)
        obj = BytesIO()
        image.save(obj, 'GIF', append_images=list(frames), save_all=True, loop=0)
        if format != 'GIF':
            image.save(obj, format)
        return obj

    def animated_image(self):
        return self.create_animated_image('RGBA', 'GIF')

    def supported_image(self):
        return self.create_image('RGB', 'JPEG')

    def unsupported_image(self):
        return self.create_image('L', 'PNG')


class TestImage(unittest.TestCase):
    def setUp(self):
        """Add and open the images to run the tests."""

        dummy = DummyImage()

        self.animated_image = PIL.Image.open(dummy.animated_image())
        self.supported_image = PIL.Image.open(dummy.supported_image())
        self.unsupported_image = PIL.Image.open(dummy.unsupported_image())

    def tearDown(self):
        """Close the images."""

        self.animated_image.close()
        self.supported_image.close()
        self.unsupported_image.close()

    def test_image_support(self):
        """Test the image support using the Icon options."""

        supported = Icon(self.supported_image, (10, 10))
        self.assertTrue(supported.is_supported())

        with self.assertRaises(ImageSupportError) as exc:
            unsupported = Icon(self.unsupported_image, (10, 10))

        self.assertIsInstance(exc.exception, ImageSupportError)

    def test_resize_save(self):
        new_size = (10, 10)
        new_format = 'WEBP'

        image = Icon(self.supported_image, new_size, new_format)

        image.resize()
        image.save()

        with PIL.Image.open(image.fp) as saved_image:
            self.assertEqual(new_size, saved_image.size)
            self.assertEqual(new_format, saved_image.format)

    def test_resize_save_aniated(self): pass

    def test_bulk_resize(self): pass


if __name__ == '__main__':
    unittest.main()
