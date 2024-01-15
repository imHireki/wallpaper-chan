from abc import ABC, abstractmethod
from typing import Type

import PIL.Image

from image import info


ImageInfo = Type[info.IStaticImageInfo] | Type[info.IAnimatedImageInfo] | None
SupportedImages = dict[str, dict[str, Type[ImageInfo]]]


class IImageSupport(ABC):
    def __init__(self, image: PIL.Image.Image,
                 supported_images: SupportedImages):
        self._image: PIL.Image.Image = image
        self._supported_images: SupportedImages = supported_images

    @abstractmethod
    def get_image_info(self) -> ImageInfo: pass


class StaticImageSupport(IImageSupport):
    def get_image_info(self) -> ImageInfo:
        return self._supported_images['STATIC'].get(
            '_'.join([self._image.format or '', self._image.mode])
            )  # type: ignore


class AnimatedImageSupport(IImageSupport):
    def get_image_info(self) -> ImageInfo:
        return self._supported_images['ANIMATED'].get(
            '_'.join([self._image.format or '', self._image.mode])
            )  # type: ignore


class ImageSupportProxy(IImageSupport):
    _image_support: IImageSupport
    _image_info: ImageInfo

    def get_image_support(self) -> IImageSupport:
        if not hasattr(self, '_image_support'):
            if (not getattr(self._image, 'is_animated')
                and self._image.format != 'GIF'):
                self._image_support = StaticImageSupport(
                    self._image, self._supported_images)
            else:
                self._image_support = AnimatedImageSupport(
                    self._image, self._supported_images)

        return self._image_support

    def get_image_info(self) -> ImageInfo:
        self.get_image_support()

        if not hasattr(self, '_image_info'):
            self._image_info = self._image_support.get_image_info()
        return self._image_info

    def is_supported(self) -> bool:
        self.get_image_info()

        return self._image_info is not None
