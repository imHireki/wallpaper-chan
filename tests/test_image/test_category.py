import pytest

from image import category


def test_static_image_category(mocker):
    profile_class = mocker.Mock()
    supported_images = {"STATIC": {"JPEG_RGB": profile_class}}
    image_mock = mocker.Mock(format="JPEG", mode="RGB")

    image_category = category.StaticImageCategory(image_mock, supported_images)
    image_profile = image_category.get_image_profile()

    assert image_profile is profile_class.return_value
    profile_class.assert_called_with(image_mock)


def test_animated_image_category(mocker):
    profile_class = mocker.Mock()
    supported_images = {"ANIMATED": {"GIF_P": profile_class}}
    image_mock = mocker.Mock(format="GIF", mode="P")

    image_category = category.AnimatedImageCategory(image_mock, supported_images)
    image_profile = image_category.get_image_profile()

    assert image_profile is profile_class.return_value
    profile_class.assert_called_with(image_mock)


class TestImageCategoryProxy:
    @pytest.mark.parametrize(
        "is_animated, format, category_patch",
        [
            [True, "GIF", "image.category.AnimatedImageCategory"],
            [False, "JPEG", "image.category.StaticImageCategory"],
            [False, "GIF", "image.category.AnimatedImageCategory"],
        ],
    )
    def test_determine_category(self, mocker, is_animated, format, category_patch):
        category_patch = mocker.patch(category_patch)
        image = mocker.Mock(is_animated=is_animated, format=format)
        proxy = category.ImageCategoryProxy(image, {})

        _category = proxy._determine_category()

        assert _category is category_patch.return_value

    def test_get_image_category(self, mocker):
        proxy = category.ImageCategoryProxy(mocker.Mock(), {})
        img_category = proxy.get_image_category()
        img_category_2 = proxy.get_image_category()

        assert img_category is proxy._image_category
        assert img_category_2 is img_category

    def test_get_image_profile(self, mocker):
        proxy = category.ImageCategoryProxy(mocker.Mock(), {})
        mocker.patch.object(proxy, "get_image_category")
        proxy._image_category = mocker.Mock()

        image_profile = proxy.get_image_profile()
        image_profile_2 = proxy.get_image_profile()

        assert image_profile is proxy._image_profile
        assert image_profile_2 is image_profile
