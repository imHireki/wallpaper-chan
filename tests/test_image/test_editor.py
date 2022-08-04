import os

from image import editor


def test_static_image_editor(mocker, editor_options):
    image_to_save_mock = mocker.Mock()
    image_mock = mocker.Mock(convert=mocker.Mock(return_value=image_to_save_mock))
    static_image_editor = editor.StaticImageEditor(image_mock)

    static_image_editor.resize(**editor_options["resize_options"])
    static_image_editor.convert_mode(**editor_options["convert_mode_options"])
    static_image_editor.save(**editor_options["save_options"])

    os.remove(static_image_editor.result.name)

    assert image_mock.resize.call_args.kwargs == editor_options["resize_options"]
    assert image_mock.convert.call_args.kwargs == editor_options["convert_mode_options"]
    assert image_to_save_mock.save.call_args.kwargs == editor_options["save_options"]

def test_animated_image_editor(mocker, editor_options):
    image_mock = mocker.Mock(mode='P')
    image_mock.convert = mocker.Mock(return_value=image_mock)
    mocker.patch('image.editor.AnimatedImageEditor._get_frames',
                 lambda _: (frame for frame in [image_mock]))
    mocker.patch('image.editor.AnimatedImageEditor._get_actual_mode', lambda _: 'RGB')

    animated_image_editor = editor.AnimatedImageEditor(image_mock)

    animated_image_editor.resize(**editor_options["resize_options"])
    animated_image_editor.save(**editor_options["save_options"])

    animated_image_editor.convert_mode(**editor_options["convert_mode_options"])
    animated_image_editor.save(**editor_options["save_options"])

    os.remove(animated_image_editor.result.name)

    assert image_mock.resize.call_args.kwargs == editor_options["resize_options"]
    assert image_mock.convert.call_args.kwargs == editor_options["convert_mode_options"]
    assert set(editor_options["save_options"]).issubset(
        animated_image_editor._original_image.save.call_args.kwargs
    )


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
