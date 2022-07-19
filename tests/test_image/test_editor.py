import os

from image import editor


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

    os.remove(static_image_editor.result.name)

    assert image_resize_mock.call_args.kwargs == editor_options_mock.resize_options
    assert image_save_mock.call_args.kwargs == editor_options_mock.save_options


def test_animated_image_editor(mocker, editor_options_mock):
    image_resize_mock = mocker.Mock()

    image_sequence_iterator_mock = mocker.patch(
        'PIL.ImageSequence.Iterator',
        lambda _: (frame for frame in [mocker.Mock(resize=image_resize_mock)])
    )

    animated_image_editor = editor.AnimatedImageEditor(mocker.Mock(), editor_options_mock)
    animated_image_editor.resize_image()

    image_save_mock = mocker.patch.object(animated_image_editor._image, 'save')
    animated_image_editor.save_resized_image()

    os.remove(animated_image_editor.result.name)

    assert image_resize_mock.call_args.kwargs == editor_options_mock.resize_options
    assert set(editor_options_mock.save_options).issubset(image_save_mock.call_args.kwargs)
