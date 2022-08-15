import pytest

from image import info


class TestStaticJpegRgbInfo:
    def test_name(self):
        assert info.StaticJpegRgbInfo.name == 'JPEG_RGB'

    def test_is_standardized(self, mocker):
        assert info.StaticJpegRgbInfo(mocker.Mock()).is_standardized() is True

    def test_standardize(self, mocker):
        assert not info.StaticJpegRgbInfo(mocker.Mock()).standardize()

    def test_get_image_editor(self, mocker):
        image_info = info.StaticJpegRgbInfo(mocker.Mock())
        image_editor_mock = mocker.patch('image.editor.StaticImageEditor')

        assert image_info.get_image_editor()
        assert image_editor_mock.call_args.args == (image_info._image,)

    def test_get_image_for_color_clustering(self, mocker):
        image_info = info.StaticJpegRgbInfo(mocker.Mock())
        assert image_info.get_image_for_color_clustering() is image_info._image


class TestStaticWebpRgbInfo:
    def test_name(self):
        assert info.StaticWebpRgbInfo.name == 'WEBP_RGB'

    def test_is_standardized(self, mocker):
        assert info.StaticWebpRgbInfo(mocker.Mock()).is_standardized() is False

    def test_standardize(self, mocker):
        mocker.patch('image.editor.StaticImageEditor')

        image_info = info.StaticWebpRgbInfo(mocker.Mock())
        standardized_image = image_info.standardize()

        assert standardized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args.kwargs == info.save_options['JPEG']


class TestStaticWebpRgbaInfo:
    def test_name(self):
        assert info.StaticWebpRgbaInfo.name == 'WEBP_RGBA'

    def test_is_standardized(self, mocker):
        assert info.StaticWebpRgbaInfo(mocker.Mock()).is_standardized() is False

    @pytest.mark.parametrize('extrema,save_options', [
        [(0, 0, 0, (255, 255)), info.save_options['JPEG']],
        [(0, 0, 0, (0  , 255)), info.save_options['PNG']]
    ])
    def test_standardize(self, mocker, extrema, save_options):
        image_mock = mocker.Mock(getextrema=lambda: extrema)
        mocker.patch('image.editor.StaticImageEditor')

        image_info = info.StaticWebpRgbaInfo(image_mock)
        standardized_image = image_info.standardize()

        assert standardized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args == (save_options,)


class TestStaticPngRgbInfo:
    def test_name(self):
        assert info.StaticPngRgbInfo.name == 'PNG_RGB'

    def test_is_standardized(self, mocker):
        assert info.StaticPngRgbInfo(mocker.Mock()).is_standardized() is False

    def test_standardize(self, mocker):
        mocker.patch('image.editor.StaticImageEditor')

        image_info = info.StaticPngRgbInfo(mocker.Mock())
        standardized_image = image_info.standardize()

        assert standardized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args.kwargs == info.save_options['JPEG']


class TestStaticPngRgbaInfo:
    def test_name(self):
        assert info.StaticPngRgbaInfo.name == 'PNG_RGBA'

    @pytest.mark.parametrize('extrema, is_translucent', [
        [(0, 0, 0, (255, 255)), False],
        [(0, 0, 0, (0, 255)), True],
    ])
    def test_is_standardized(self, mocker, extrema, is_translucent):
        image_mock = mocker.Mock(getextrema=lambda: extrema)
        assert info.StaticPngRgbaInfo(image_mock).is_standardized() is is_translucent

    def test_standardize(self, mocker):
        mocker.patch('image.editor.StaticImageEditor')

        image_info = info.StaticPngRgbaInfo(mocker.Mock())
        standardized_image = image_info.standardize()

        assert standardized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args.kwargs == info.save_options['JPEG']


class TestAnimatedGifPInfo:
    def test_name(self):
        assert info.AnimatedGifPInfo.name == 'GIF_P'

    @pytest.mark.parametrize('is_animated', [True, False])
    def test_is_standardized(self, mocker, is_animated):
        image_mock = mocker.Mock(is_animated=is_animated)
        assert info.AnimatedGifPInfo(image_mock).is_standardized() is is_animated

    @pytest.mark.parametrize('_info,save_options', [
        [{"transparency": 1}, info.save_options['PNG']], [{}, info.save_options['JPEG']]
    ])
    def test_standardize(self, mocker, _info, save_options):
        image_mock = mocker.Mock(info=_info)
        mocker.patch('image.editor.AnimatedImageEditor')

        image_info = info.AnimatedGifPInfo(image_mock)
        standardized_image = image_info.standardize()

        assert standardized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args.kwargs == save_options

    def test_get_image_editor(self, mocker):
        image_mock = mocker.Mock()
        image_editor_mock = mocker.patch('image.editor.AnimatedImageEditor')

        image_info = info.AnimatedGifPInfo(image_mock)

        assert image_info.get_image_editor()
        assert image_editor_mock.call_args.args == (image_mock,)

    def test_get_image_for_color_clustering(self, mocker):
        mocker.patch('image.editor.AnimatedImageEditor')
        image_mock = mocker.Mock()

        image_info = info.AnimatedGifPInfo(image_mock)

        assert image_info.get_image_for_color_clustering()
        assert image_mock.convert.call_args.args == (image_info._image_editor.actual_mode,)


class TestAnimatedWebpRgbaInfo:
    def test_name(self):
        assert info.AnimatedWebpRgbaInfo.name == 'WEBP_RGBA'

    def test_is_standardized(self, mocker):
        assert info.AnimatedWebpRgbaInfo(mocker.Mock()).is_standardized() is False

    def test_standardize(self, mocker):
        mocker.patch('image.editor.AnimatedImageEditor')

        image_info = info.AnimatedWebpRgbaInfo(mocker.Mock())
        standardized_image = image_info.standardize()

        assert standardized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args.kwargs == info.save_options['GIF']


class TestAnimatedWebpRgbInfo:
    def test_name(self):
        assert info.AnimatedWebpRgbInfo.name == 'WEBP_RGB'

    def test_is_standardized(self, mocker):
        assert info.AnimatedWebpRgbInfo(mocker.Mock()).is_standardized() is False

    @pytest.mark.parametrize('is_animated,save_options', [
        [True, info.save_options['GIF']],
        [False, info.save_options['JPEG']]
    ])
    def test_standardize(self, mocker, is_animated, save_options):
        mocker.patch('image.editor.AnimatedImageEditor')

        image_info = info.AnimatedWebpRgbInfo(mocker.Mock(is_animated=is_animated))
        standardized_image = image_info.standardize()

        assert standardized_image is image_info._image_editor.result
        assert image_info._image_editor.save.call_args.kwargs == save_options
