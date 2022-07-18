import pytest
import os

from image import editor


@pytest.fixture
def editor_options_mock(mocker):
    resize_options = {"size": (512, 512), "resample": 2, "reducing_gap": 2}
    save_options = {"quality": 75, "format": "WEBP"}
    return mocker.Mock(resize_options=resize_options, save_options=save_options)

def test_editor_options():
    resize_options = {"size": (512, 512), "resample": 2, "reducing_gap": 2}
    save_options = {"quality": 75, "format": "WEBP"}

    editor_options = editor.EditorOptions(**resize_options, **save_options)

    assert editor_options.resize_options == resize_options
    assert editor_options.save_options == save_options

def test_static_image_editor(mocker, editor_options_mock):
    image_resize_mock = mocker.Mock()
    image = mocker.Mock(resize=image_resize_mock)

    static_image_editor = editor.StaticImageEditor(image, editor_options_mock)
    static_image_editor.resize_image()

    image_save_mock = mocker.patch.object(static_image_editor._image, 'save')
    static_image_editor.save_resized_image()

    assert image_resize_mock.call_args.kwargs == editor_options_mock.resize_options
    assert image_save_mock.call_args.kwargs == editor_options_mock.save_options

    # temporary file cleanup
    os.remove(static_image_editor.result.name)
