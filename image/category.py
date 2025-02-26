from abc import ABC, abstractmethod

from PIL.Image import Image

from image.profile import (
    IOptimizableStaticProfile,
    IStaticProfile,
    IOptimizableAnimatedProfile,
)


Profile = IStaticProfile | IOptimizableStaticProfile | IOptimizableAnimatedProfile
SupportedImages = dict[str, dict[str, type[Profile]]]


class ICategory(ABC):
    def __init__(self, image: Image, supported_images: SupportedImages):
        self._image: Image = image
        self._supported_images: SupportedImages = supported_images

    @abstractmethod
    def get_profile(self) -> Profile | None:
        pass


class StaticCategory(ICategory):
    def get_profile(self) -> Profile | None:
        format_mode = "_".join([self._image.format or "", self._image.mode])
        profile_class = self._supported_images["STATIC"].get(format_mode)
        return profile_class(self._image) if profile_class else None


class AnimatedCategory(ICategory):
    def get_profile(self) -> Profile | None:
        format_mode = "_".join([self._image.format or "", self._image.mode])
        profile_class = self._supported_images["ANIMATED"].get(format_mode)
        return profile_class(self._image) if profile_class else None


class CategoryProxy(ICategory):
    _category: ICategory
    _profile: Profile | None

    def _determine_category(self) -> ICategory:
        if (
            getattr(self._image, "is_animated", False) is False
            and self._image.format != "GIF"
        ):
            return StaticCategory(self._image, self._supported_images)
        else:
            return AnimatedCategory(self._image, self._supported_images)

    def get_category(self) -> ICategory:
        if not hasattr(self, "_image_category"):
            self._image_category = self._determine_category()
        return self._image_category

    def get_profile(self) -> Profile | None:
        self.get_category()

        if not hasattr(self, "_image_profile"):
            self._image_profile = self._image_category.get_profile()
        return self._image_profile
