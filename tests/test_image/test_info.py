import pytest

from image import info


class TestStaticJpegRgbInfo:
    def test_name(self):
        assert info.StaticJpegRgbInfo.name == 'JPEG_RGB'

    def test_is_optimized(self, mocker):
        assert info.StaticJpegRgbInfo(mocker.Mock()).is_optimized() is True

    def test_optimize(self, mocker):
        assert not info.StaticJpegRgbInfo(mocker.Mock()).optimize()

    def test_get_image_editor(self, mocker):
        image_editor_mock = mocker.patch('image.editor.StaticImageEditor')
        image_info = info.StaticJpegRgbInfo(mocker.Mock())

        assert image_info.get_image_editor()
        assert image_editor_mock.call_args.args[0] == image_info._image

    def test_get_image_for_color_clustering(self, mocker):
        image_info = info.StaticJpegRgbInfo(mocker.Mock())

        image = image_info.get_image_for_color_clustering()

        assert image == image_info._image


class TestStaticWebpRgbInfo:
    def test_name(self):
        assert info.StaticWebpRgbInfo.name == 'WEBP_RGB'

    def test_is_optimized(self, mocker):
        assert info.StaticWebpRgbInfo(mocker.Mock()).is_optimized() is False

    def test_optimize(self, mocker):
        mocker.patch('image.editor.StaticImageEditor')

        image_info = info.StaticWebpRgbInfo(mocker.Mock())
        optimized_image = image_info.optimize()

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == info.SAVE_OPTIONS['JPEG'])


class TestStaticWebpRgbaInfo:
    def test_name(self):
        assert info.StaticWebpRgbaInfo.name == 'WEBP_RGBA'

    def test_is_optimized(self, mocker):
        assert info.StaticWebpRgbaInfo(mocker.Mock()).is_optimized() is False

    @pytest.mark.parametrize('extrema, save_options', [
        [(0, 0, 0, (255, 255)), info.SAVE_OPTIONS['JPEG']],
        [(0, 0, 0, (0  , 255)), info.SAVE_OPTIONS['PNG']]
    ])
    def test_optimize(self, mocker, extrema, save_options):
        mocker.patch('image.editor.StaticImageEditor')
        image_mock = mocker.Mock(getextrema=lambda: extrema)

        image_info = info.StaticWebpRgbaInfo(image_mock)
        optimized_image = image_info.optimize()

        assert optimized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args.kwargs == save_options


class TestStaticPngRgbInfo:
    def test_name(self):
        assert info.StaticPngRgbInfo.name == 'PNG_RGB'

    def test_is_optimized(self, mocker):
        assert info.StaticPngRgbInfo(mocker.Mock()).is_optimized() is False

    def test_optimize(self, mocker):
        mocker.patch('image.editor.StaticImageEditor')

        image_info = info.StaticPngRgbInfo(mocker.Mock())
        optimized_image = image_info.optimize()

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == info.SAVE_OPTIONS['JPEG'])


class TestStaticPngRgbaInfo:
    def test_name(self):
        assert info.StaticPngRgbaInfo.name == 'PNG_RGBA'

    @pytest.mark.parametrize('extrema, is_translucent', [
        [(0, 0, 0, (255, 255)), False],
        [(0, 0, 0, (0, 255)), True],
    ])
    def test_is_optimized(self, mocker, extrema, is_translucent):
        image_mock = mocker.Mock(getextrema=lambda: extrema)

        is_optimized = info.StaticPngRgbaInfo(image_mock).is_optimized()

        assert is_optimized is is_translucent

    def test_optimize(self, mocker):
        mocker.patch('image.editor.StaticImageEditor')

        image_info = info.StaticPngRgbaInfo(mocker.Mock())
        optimized_image = image_info.optimize()

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == info.SAVE_OPTIONS['JPEG'])


class TestAnimatedGifPInfo:
    def test_name(self):
        assert info.AnimatedGifPInfo.name == 'GIF_P'

    @pytest.mark.parametrize('is_animated', [True, False])
    def test_is_optimized(self, mocker, is_animated):
        image_mock = mocker.Mock(is_animated=is_animated)

        is_optimized = info.AnimatedGifPInfo(image_mock).is_optimized()

        assert is_optimized is is_animated

    @pytest.mark.parametrize('_info, save_options', [
        [{"transparency": 1}, info.SAVE_OPTIONS['PNG']],
        [{}, info.SAVE_OPTIONS['JPEG']]
    ])
    def test_optimize(self, mocker, _info, save_options):
        mocker.patch('image.editor.AnimatedImageEditor')
        image_mock = mocker.Mock(info=_info)

        image_info = info.AnimatedGifPInfo(image_mock)
        optimized_image = image_info.optimize()

        assert optimized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args.kwargs == save_options

    def test_get_image_editor(self, mocker):
        image_editor_mock = mocker.patch('image.editor.AnimatedImageEditor')
        image_mock = mocker.Mock()

        image_info = info.AnimatedGifPInfo(image_mock)

        assert image_info.get_image_editor()
        assert image_editor_mock.call_args.args[0] == image_mock

    def test_get_image_for_color_clustering(self, mocker):
        mocker.patch('image.editor.AnimatedImageEditor')
        image_mock = mocker.Mock()

        image_info = info.AnimatedGifPInfo(image_mock)
        image = image_info.get_image_for_color_clustering()

        assert image
        assert (image_mock.convert.call_args.args[0]
                == image_info._image_editor.actual_mode)


class TestAnimatedWebpRgbaInfo:
    def test_name(self):
        assert info.AnimatedWebpRgbaInfo.name == 'WEBP_RGBA'

    def test_is_optimized(self, mocker):
        is_optimized = info.AnimatedWebpRgbaInfo(
            mocker.Mock()).is_optimized()
        assert is_optimized is False

    def test_optimize(self, mocker):
        mocker.patch('image.editor.AnimatedImageEditor')

        image_info = info.AnimatedWebpRgbaInfo(mocker.Mock())
        optimized_image = image_info.optimize()

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == info.SAVE_OPTIONS['GIF'])


class TestAnimatedWebpRgbInfo:
    def test_name(self):
        assert info.AnimatedWebpRgbInfo.name == 'WEBP_RGB'

    def test_is_optimized(self, mocker):
        is_optimized = info.AnimatedWebpRgbInfo(
            mocker.Mock()).is_optimized()
        assert is_optimized is False

    def test_optimize(self, mocker):
        mocker.patch('image.editor.AnimatedImageEditor')

        image_info = info.AnimatedWebpRgbInfo(mocker.Mock())
        optimized_image = image_info.optimize()

        assert optimized_image is image_info._image_editor.result
        assert (image_info._image_editor.save.call_args.kwargs
                == info.SAVE_OPTIONS['GIF'])
