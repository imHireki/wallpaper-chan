import os

from image import editor


def test_static_image_editor(mocker, editor_options):
    image_resize_mock = mocker.Mock()
    static_image_editor = editor.StaticImageEditor(mocker.Mock(resize=image_resize_mock))

    static_image_editor.resize(**editor_options["resize_options"])

    image_convert_mock = mocker.patch.object(static_image_editor._image, 'convert')
    static_image_editor.convert_mode(**editor_options["convert_mode_options"])

    image_save_mock = mocker.patch.object(static_image_editor._image, 'save')
    static_image_editor.save(**editor_options["save_options"])

    os.remove(static_image_editor.result.name)

    assert image_resize_mock.call_args.kwargs == editor_options["resize_options"]
    assert image_convert_mock.call_args.kwargs == editor_options["convert_mode_options"]
    assert image_save_mock.call_args.kwargs == editor_options["save_options"]

def test_animated_image_editor(mocker, editor_options):
    image_resize_mock = mocker.Mock()
    frame_convert_mock = mocker.Mock()
    image_sequence_iterator_mock = mocker.patch(
        'PIL.ImageSequence.Iterator',
        lambda _: (frame for frame in [mocker.Mock(resize=image_resize_mock,
                                                   convert=frame_convert_mock)])
    )
    animated_image_editor = editor.AnimatedImageEditor(mocker.Mock())

    animated_image_editor.resize(**editor_options["resize_options"])

    animated_image_editor.convert_mode(**editor_options["convert_mode_options"])

    image_save_mock = mocker.patch.object(animated_image_editor._image, 'save')
    animated_image_editor.save(**editor_options["save_options"])

    os.remove(animated_image_editor.result.name)

    assert image_resize_mock.call_args.kwargs == editor_options["resize_options"]
    assert frame_convert_mock.call_args.kwargs == editor_options["convert_mode_options"]
    assert set(editor_options["save_options"]).issubset(image_save_mock.call_args.kwargs)

def test_bulk_resize_save_editor(mocker, editor_options):
    image_editor_mock = mocker.Mock()

    bulk_resize_save_editor = editor.BulkResizeSaveEditor(
        (editor for editor in [image_editor_mock]),
        save_options=editor_options["save_options"],
        resize_options=editor_options["resize_options"]
    )

    assert next(bulk_resize_save_editor) is image_editor_mock.result
    assert image_editor_mock.resize.call_args.kwargs == editor_options["resize_options"]
    assert image_editor_mock.save.call_args.kwargs == editor_options["save_options"]
