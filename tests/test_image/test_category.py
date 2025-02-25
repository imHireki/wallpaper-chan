import pytest

from image import category


def test_static_category(mocker):
    profile_class = mocker.Mock()
    supported_images = {"STATIC": {"JPEG_RGB": profile_class}}
    image = mocker.Mock(format="JPEG", mode="RGB")

    _category = category.StaticCategory(image, supported_images)
    profile = _category.get_profile()

    assert profile is profile_class.return_value
    profile_class.assert_called_with(image)


def test_animated_category(mocker):
    profile_class = mocker.Mock()
    supported_images = {"ANIMATED": {"GIF_P": profile_class}}
    image = mocker.Mock(format="GIF", mode="P")

    _category = category.AnimatedCategory(image, supported_images)
    profile = _category.get_profile()

    assert profile is profile_class.return_value
    profile_class.assert_called_with(image)


class TestImageCategoryProxy:
    @pytest.mark.parametrize(
        "is_animated, format, category_patch",
        [
            [True, "GIF", "image.category.AnimatedCategory"],
            [False, "JPEG", "image.category.StaticCategory"],
            [False, "GIF", "image.category.AnimatedCategory"],
        ],
    )
    def test_determine_category(self, mocker, is_animated, format, category_patch):
        category_patch = mocker.patch(category_patch)
        image = mocker.Mock(is_animated=is_animated, format=format)
        proxy = category.ImageCategoryProxy(image, {})

        _category = proxy._determine_category()

        assert _category is category_patch.return_value

    def test_get_category(self, mocker):
        proxy = category.ImageCategoryProxy(mocker.Mock(), {})
        _category = proxy.get_category()
        _category_2 = proxy.get_category()

        assert _category is proxy._image_category
        assert _category_2 is _category

    def test_get_profile(self, mocker):
        proxy = category.ImageCategoryProxy(mocker.Mock(), {})
        mocker.patch.object(proxy, "get_category")
        proxy._image_category = mocker.Mock()

        _profile = proxy.get_profile()
        _profile_2 = proxy.get_profile()

        assert _profile is proxy._image_profile
        assert _profile_2 is _profile
