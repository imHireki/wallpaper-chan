from abc import ABC, abstractmethod
from typing import Type

import PIL.Image

from image.profile import IStaticImageProfile, IAnimatedImageProfile


ImageProfile = IStaticImageProfile | IAnimatedImageProfile | None
SupportedImages = dict[
    str, dict[str, Type[IStaticImageProfile] | Type[IAnimatedImageProfile]]
]


class IImageCategory(ABC):
    def __init__(self, image: PIL.Image.Image, supported_images: SupportedImages):
        self._image: PIL.Image.Image = image
        self._supported_images: SupportedImages = supported_images

    @abstractmethod
    def get_image_profile(self) -> ImageProfile:
        pass


class StaticImageCategory(IImageCategory):
    def get_image_profile(self) -> ImageProfile:
        format_mode = "_".join([self._image.format or "", self._image.mode])
        profile_class = self._supported_images["STATIC"].get(format_mode)
        return profile_class(self._image) if profile_class else None


class AnimatedImageCategory(IImageCategory):
    def get_image_profile(self) -> ImageProfile:
        format_mode = "_".join([self._image.format or "", self._image.mode])
        profile_class = self._supported_images["ANIMATED"].get(format_mode)
        return profile_class(self._image) if profile_class else None


class ImageCategoryProxy(IImageCategory):
    _image_category: IImageCategory
    _image_profile: ImageProfile

    def _determine_category(self) -> IImageCategory:
        if (
            getattr(self._image, "is_animated", False) is False
            and self._image.format != "GIF"
        ):
            return StaticImageCategory(self._image, self._supported_images)
        else:
            return AnimatedImageCategory(self._image, self._supported_images)

    def get_image_category(self) -> IImageCategory:
        if not hasattr(self, "_image_category"):
            self._image_category = self._determine_category()
        return self._image_category

    def get_image_profile(self) -> ImageProfile:
        self.get_image_category()

        if not hasattr(self, "_image_profile"):
            self._image_profile = self._image_category.get_image_profile()
        return self._image_profile
