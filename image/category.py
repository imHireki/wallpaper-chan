from abc import ABC, abstractmethod

from PIL.Image import Image

from image.profile import (
    IOptimizableStaticProfile,
    IStaticProfile,
    IOptimizableAnimatedProfile,
)


Profile = IStaticProfile | IOptimizableStaticProfile | IOptimizableAnimatedProfile
SupportedImages = dict[str, dict[str, type[Profile]]]


class IImageCategory(ABC):
    def __init__(self, image: Image, supported_images: SupportedImages):
        self._image: Image = image
        self._supported_images: SupportedImages = supported_images

    @abstractmethod
    def get_image_profile(self) -> Profile | None:
        pass


class StaticImageCategory(IImageCategory):
    def get_image_profile(self) -> Profile | None:
        format_mode = "_".join([self._image.format or "", self._image.mode])
        profile_class = self._supported_images["STATIC"].get(format_mode)
        return profile_class(self._image) if profile_class else None


class AnimatedImageCategory(IImageCategory):
    def get_image_profile(self) -> Profile | None:
        format_mode = "_".join([self._image.format or "", self._image.mode])
        profile_class = self._supported_images["ANIMATED"].get(format_mode)
        return profile_class(self._image) if profile_class else None


class ImageCategoryProxy(IImageCategory):
    _image_category: IImageCategory
    _image_profile: Profile | None

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

    def get_image_profile(self) -> Profile | None:
        self.get_image_category()

        if not hasattr(self, "_image_profile"):
            self._image_profile = self._image_category.get_image_profile()
        return self._image_profile
