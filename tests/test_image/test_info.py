import pytest

from image import info


class TestIStaticImageInfo:
    def test_get_image_editor(self, mocker):
        image_info = info.StaticJpegRgbInfo(mocker.Mock())
        image_editor_mock = mocker.patch('image.editor.StaticImageEditor')

        assert image_info.get_image_editor()
        assert image_editor_mock.call_args.args == (image_info._image,)

    def test_get_image_for_color_clustering(self, mocker):
        image_info = info.StaticJpegRgbInfo(mocker.Mock())
        assert image_info.get_image_for_color_clustering() is image_info._image


class TestStaticJpegRgbInfo:
    def test_name(self):
        assert info.StaticJpegRgbInfo.name == 'JPEG_RGB'

    def test_is_standardized(self, mocker):
        assert info.StaticJpegRgbInfo(mocker.Mock()).is_standardized() is True

    def test_standardize(self, mocker):
        assert not info.StaticJpegRgbInfo(mocker.Mock()).standardize()


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
