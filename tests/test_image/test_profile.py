import pytest

from tests.conftest import SAVE_OPTIONS
from image import profile


class TestStaticJpegRgbProfile:
    def test_name(self):
        assert profile.StaticJpegRgbProfile.name == 'JPEG_RGB'

    def test_is_optimized(self, mocker):
        assert profile.StaticJpegRgbProfile(mocker.Mock()).is_optimized() is True

    def test_optimize(self, mocker):
        assert not profile.StaticJpegRgbProfile(mocker.Mock()).optimize()

    def test_get_image_editor(self, mocker):
        image_editor_mock = mocker.patch('image.editor.StaticImageEditor')
        image_info = profile.StaticJpegRgbProfile(mocker.Mock())

        assert image_info.get_image_editor()
        assert image_editor_mock.call_args.args[0] == image_info._image

    def test_get_image_for_color_clustering(self, mocker):
        image_info = profile.StaticJpegRgbProfile(mocker.Mock())

        image = image_info.get_image_for_color_clustering()

        assert image == image_info._image


class TestStaticWebpRgbProfile:
    def test_name(self):
        assert profile.StaticWebpRgbProfile.name == 'WEBP_RGB'

    def test_is_optimized(self, mocker):
        assert profile.StaticWebpRgbProfile(mocker.Mock()).is_optimized() is False

    def test_optimize(self, mocker):
        mocker.patch('image.editor.StaticImageEditor')

        image_info = profile.StaticWebpRgbProfile(mocker.Mock())
        optimized_image = image_info.optimize(SAVE_OPTIONS)

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == SAVE_OPTIONS['JPEG'])


class TestStaticWebpRgbaProfile:
    def test_name(self):
        assert profile.StaticWebpRgbaProfile.name == 'WEBP_RGBA'

    def test_is_optimized(self, mocker):
        assert profile.StaticWebpRgbaProfile(mocker.Mock()).is_optimized() is False

    @pytest.mark.parametrize(
        "extrema, save_options",
        [
            [((0, 255), (0, 255), (0, 255), (255, 255)), SAVE_OPTIONS["JPEG"]],
            [((0, 255), (0, 255), (0, 255), (0, 255)), SAVE_OPTIONS["PNG"]],
        ],
    )
    def test_optimize(self, mocker, extrema, save_options):
        image_mock = mocker.Mock(getextrema=lambda: extrema)

        image_info = profile.StaticWebpRgbaProfile(image_mock)
        editor = image_info._image_editor = mocker.Mock()

        opts = {save_options["format"]: save_options}
        optimized_image = image_info.optimize(opts)

        assert optimized_image is image_info._image_editor.result
        editor.save.assert_called_with(**save_options)


class TestStaticPngRgbProfile:
    def test_name(self):
        assert profile.StaticPngRgbProfile.name == 'PNG_RGB'

    def test_is_optimized(self, mocker):
        assert profile.StaticPngRgbProfile(mocker.Mock()).is_optimized() is False

    def test_optimize(self, mocker):
        mocker.patch('image.editor.StaticImageEditor')

        image_info = profile.StaticPngRgbProfile(mocker.Mock())
        optimized_image = image_info.optimize(SAVE_OPTIONS)

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == SAVE_OPTIONS['JPEG'])


class TestStaticPngRgbaProfile:
    def test_name(self):
        assert profile.StaticPngRgbaProfile.name == "PNG_RGBA"

    @pytest.mark.parametrize(
        "extrema, is_translucent",
        [
            [((0, 255), (0, 255), (0, 255), (255, 255)), False],
            [((0, 255), (0, 255), (0, 255), (0, 255)), True],
        ],
    )
    def test_is_optimized(self, mocker, extrema, is_translucent):
        image_mock = mocker.Mock(getextrema=lambda: extrema)

        is_optimized = profile.StaticPngRgbaProfile(image_mock).is_optimized()

        assert is_optimized is is_translucent

    def test_optimize(self, mocker):
        mocker.patch('image.editor.StaticImageEditor')

        image_info = profile.StaticPngRgbaProfile(mocker.Mock())
        optimized_image = image_info.optimize(SAVE_OPTIONS)

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == SAVE_OPTIONS['JPEG'])


class TestAnimatedGifPProfile:
    def test_name(self):
        assert profile.AnimatedGifPProfile.name == 'GIF_P'

    @pytest.mark.parametrize('is_animated', [True, False])
    def test_is_optimized(self, mocker, is_animated):
        image_mock = mocker.Mock(is_animated=is_animated)

        is_optimized = profile.AnimatedGifPProfile(image_mock).is_optimized()

        assert is_optimized is is_animated

    @pytest.mark.parametrize('_info, save_options', [
        [{"transparency": 1},SAVE_OPTIONS['PNG']],
        [{}, SAVE_OPTIONS['JPEG']]
    ])
    def test_optimize(self, mocker, _info, save_options):
        mocker.patch('image.editor.AnimatedImageEditor')
        image_mock = mocker.Mock(info=_info)

        image_info = profile.AnimatedGifPProfile(image_mock)
        optimized_image = image_info.optimize(SAVE_OPTIONS)

        assert optimized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args.kwargs == save_options

    def test_get_image_editor(self, mocker):
        image_editor_mock = mocker.patch('image.editor.AnimatedImageEditor')
        image_mock = mocker.Mock()

        image_info = profile.AnimatedGifPProfile(image_mock)

        assert image_info.get_image_editor()
        assert image_editor_mock.call_args.args[0] == image_mock

    def test_get_image_for_color_clustering(self, mocker):
        mocker.patch('image.editor.AnimatedImageEditor')
        image_mock = mocker.Mock()

        image_info = profile.AnimatedGifPProfile(image_mock)
        image = image_info.get_image_for_color_clustering()

        assert image
        assert (image_mock.convert.call_args.args[0]
                == image_info._image_editor.actual_mode)


class TestAnimatedWebpRgbaProfile:
    def test_name(self):
        assert profile.AnimatedWebpRgbaProfile.name == 'WEBP_RGBA'

    def test_is_optimized(self, mocker):
        is_optimized = profile.AnimatedWebpRgbaProfile(
            mocker.Mock()).is_optimized()
        assert is_optimized is False

    def test_optimize(self, mocker):
        mocker.patch('image.editor.AnimatedImageEditor')

        image_info = profile.AnimatedWebpRgbaProfile(mocker.Mock())
        optimized_image = image_info.optimize(SAVE_OPTIONS)

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == SAVE_OPTIONS['GIF'])


class TestAnimatedWebpRgbProfile:
    def test_name(self):
        assert profile.AnimatedWebpRgbProfile.name == 'WEBP_RGB'

    def test_is_optimized(self, mocker):
        is_optimized = profile.AnimatedWebpRgbProfile(
            mocker.Mock()).is_optimized()
        assert is_optimized is False

    def test_optimize(self, mocker):
        mocker.patch('image.editor.AnimatedImageEditor')

        image_info = profile.AnimatedWebpRgbProfile(mocker.Mock())
        optimized_image = image_info.optimize(SAVE_OPTIONS)

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == SAVE_OPTIONS['GIF'])
