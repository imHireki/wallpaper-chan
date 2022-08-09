from image import info


class TestStaticJpegRgbInfo:
    def test_name(self, mocker):
        assert info.StaticJpegRgbInfo(mocker.Mock()).name == 'JPEG_RGB'

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

