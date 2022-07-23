import os

from image import editor


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


def test_bulk_image_editor(mocker):
    resize_image_mock = mocker.Mock()
    save_resized_image_mock = mocker.Mock()
    result_mock = mocker.Mock()

    image_editor_mock = mocker.Mock(resize_image=resize_image_mock,
                                    save_resized_image=save_resized_image_mock,
                                    result=result_mock)

    bulk_image_editor = editor.BulkImageEditor((editor for editor in [image_editor_mock]))

    image_editor_result = next(bulk_image_editor)

    assert resize_image_mock.called
    assert save_resized_image_mock.called
    assert image_editor_result is result_mock

