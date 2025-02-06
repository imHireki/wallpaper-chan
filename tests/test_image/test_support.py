import pytest

from image import support


def test_static_image_support(mocker):
    supported_images = {"STATIC": {"JPEG_RGB": mocker.Mock()}}
    image_mock = mocker.Mock(format='JPEG', mode='RGB')

    image_support = support.StaticImageSupport(image_mock, supported_images)
    image_profile = image_support.get_image_profile()

    assert image_profile is supported_images['STATIC']['JPEG_RGB']

def test_animated_image_support(mocker):
    supported_images = {"ANIMATED": {"GIF_P": mocker.Mock()}}
    image_mock = mocker.Mock(format='GIF', mode='P')

    image_support = support.AnimatedImageSupport(image_mock, supported_images)
    image_profile = image_support.get_image_profile()

    assert image_profile is supported_images['ANIMATED']['GIF_P']


class TestImageSupportProxy:
    @pytest.mark.parametrize('is_animated, format, support_patch', [
        [True, 'GIF', 'image.support.AnimatedImageSupport'],
        [False, 'JPEG', 'image.support.StaticImageSupport'],
        [False, 'GIF', 'image.support.AnimatedImageSupport']
    ])
    def test_get_image_support(self, mocker, is_animated,
                               format, support_patch):
        image_support_mock = mocker.patch(support_patch)

        proxy = support.ImageSupportProxy(
            mocker.Mock(is_animated=is_animated, format=format), {})
        image_support = proxy.get_image_support()

        assert image_support is image_support_mock.return_value
        assert proxy._image_support is image_support_mock.return_value

    def test_get_image_profile(self, mocker):
        proxy = support.ImageSupportProxy(mocker.Mock(), {})
        mocker.patch.object(proxy, 'get_image_support')
        proxy._image_support = mocker.Mock()

        image_profile = proxy.get_image_profile()

        assert image_profile is proxy._image_support.get_image_profile.return_value
        assert (proxy._image_profile
                is proxy._image_support.get_image_profile.return_value)

    @pytest.mark.parametrize('_image_profile', [1, 0])
    def test_is_supported(self, mocker, _image_profile):
        proxy = support.ImageSupportProxy(mocker.Mock(), {})
        mocker.patch.object(proxy, 'get_image_profile')
        proxy._image_profile = _image_profile

        is_supported = proxy.is_supported()

        assert is_supported is (_image_profile is not None)
