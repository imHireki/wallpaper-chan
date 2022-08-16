from image import support


def test_static_image_support(mocker):
    supported_images_mock = {"STATIC": {"JPEG_RGB": mocker.Mock()}}
    image_mock = mocker.Mock(format='JPEG', mode='RGB')

    image_support = support.StaticImageSupport(image_mock, supported_images_mock)
    image_info = image_support.get_image_info()

    assert image_info is supported_images_mock['STATIC']['JPEG_RGB']

