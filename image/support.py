from abc import ABC, abstractmethod
from typing import Union

import PIL.Image

from image import info


ImageInfo = Union[info.IStaticImageInfo, info.IAnimatedImageInfo]


class IImageSupport(ABC):
    def __init__(self, image: PIL.Image.Image, supported_images: dict[str, ImageInfo]):
        self._image: PIL.Image.Image = image
        self._supported_images: dict[str, ImageInfo] = supported_images

    @abstractmethod
    def get_image_info(self) -> ImageInfo: pass

