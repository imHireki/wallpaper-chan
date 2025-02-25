import pytest

from image import utils


@pytest.mark.parametrize(
    "extrema, bands",
    [
        [False, (0, 255)],  # GreySlcale
        [False, ((0, 255), (0, 255), (0, 255))],  # RGB
        [True, ((0, 255), (0, 255), (0, 255), (0, 255))],  # RGBA wo translucency
        [True, ((0, 255), (0, 255), (0, 255), (0, 100))],  # RGBA w translucency
    ],
)
def test_has_translucent_alpha(mocker, bands, extrema):
    img = mocker.Mock(getextrema=lambda: bands)
    hta = utils.has_translucent_alpha(img)

    assert hta == extrema


def test_bulk_resize(mocker, editor_options):
    editor = mocker.Mock()

    options = dict(resize=editor_options["resize"], save=editor_options["save"])
    resize_save_options = [
        dict(**options, size=size) for size in [(128, 128), (256, 256)]
    ]
    bulk_resize = utils.bulk_resize(editor, resize_save_options)

    output_1 = mocker.patch("image.utils.BytesIO").return_value
    result = next(bulk_resize)
    editor.resize.assert_called_with(**options["resize"])
    editor.save.assert_called_with(output_1, **options["save"])
    assert result == output_1

    output_2 = mocker.patch("image.utils.BytesIO").return_value
    result = next(bulk_resize)
    editor.resize.assert_called_with(**options["resize"])
    editor.save.assert_called_with(output_2, **options["save"])
    assert result == output_2


def test_bulk_resize_tempfile(mocker, editor_options):
    editor = mocker.Mock()

    options = dict(resize=editor_options["resize"], save=editor_options["save"])
    resize_save_options = [
        dict(**options, size=size) for size in [(128, 128), (256, 256)]
    ]
    bulk_resize = utils.bulk_resize_tempfile(editor, resize_save_options)

    tempfile_1 = mocker.patch("image.utils.NamedTemporaryFile").return_value
    result = next(bulk_resize)
    editor.resize.assert_called_with(**options["resize"])
    editor.save.assert_called_with(tempfile_1, **options["save"])
    tempfile_1.close.assert_called()
    assert result == tempfile_1.name

    tempfile_2 = mocker.patch("image.utils.NamedTemporaryFile").return_value
    result = next(bulk_resize)
    editor.resize.assert_called_with(**options["resize"])
    editor.save.assert_called_with(tempfile_2, **options["save"])
    tempfile_2.close.assert_called()
    assert result == tempfile_2.name
