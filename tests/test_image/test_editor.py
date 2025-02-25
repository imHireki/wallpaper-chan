import pytest

from image import editor


class TestStaticImageEditor:
    def test_actual_mode(self, mocker):
        image_mode = "RGB"
        image_editor = editor.StaticImageEditor(mocker.Mock(mode=image_mode))

        assert image_editor.actual_mode == image_mode

    def test_convert_mode(self, mocker):
        image_editor = editor.StaticImageEditor(mocker.Mock())
        image_editor.convert_mode("RGBA")

        assert image_editor._original_image.convert.call_args.kwargs == {"mode": "RGBA"}

    def test_resize(self, mocker, editor_options):
        image_mock = mocker.Mock()

        image_editor = editor.StaticImageEditor(image_mock)
        image_editor.resize(**editor_options["resize"])

        assert image_mock.resize.call_args.kwargs == editor_options["resize"]

    def test_save(self, mocker, editor_options):
        fp = mocker.Mock()

        image_editor = editor.StaticImageEditor(mocker.Mock())
        edited_image = mocker.patch.object(image_editor, "_processed_image")

        image_editor.save(fp, **editor_options["save"])

        edited_image.save.assert_called_with(fp, **editor_options["save"])


class TestAnimatedImageEditor:
    @pytest.mark.parametrize(
        "mode, _info, extrema, _actual_mode",
        [
            ["P", {}, 0, "RGB"],
            ["P", {"transparency": 1}, 0, "RGBA"],
            ["RGBA", {}, [(), (), (), (255, 255)], "RGB"],
            ["RGBA", {}, [(), (), (), (0, 255)], "RGBA"],
        ],
    )
    def test_actual_mode(self, mocker, mode, _info, extrema, _actual_mode):
        image_editor = editor.AnimatedImageEditor(
            mocker.Mock(mode=mode, getextrema=lambda: extrema, info=_info)
        )

        assert image_editor.actual_mode == _actual_mode

    def test_convert_mode(self, mocker):
        new_mode = "RGBA"
        image_mock_1 = mocker.Mock(mode="P")
        image_mock_2 = mocker.Mock(mode="RGB")
        mocker.patch(
            "image.editor.AnimatedImageEditor._find_actual_mode",
            lambda self: image_mock_2.mode,
        )
        mocker.patch(
            "image.editor.AnimatedImageEditor._get_frames",
            lambda self: (_ for _ in [image_mock_1, image_mock_2]),
        )

        image_editor = editor.AnimatedImageEditor(image_mock_1)
        image_editor.convert_mode(new_mode)
        [_ for _ in image_editor._processed_frames]

        assert image_mock_1.convert.call_args.kwargs == {"mode": new_mode}
        assert image_mock_2.copy.called

    def test_resize(self, mocker, editor_options):
        image_mock_1_converted = mocker.Mock()
        image_mock_1 = mocker.Mock(mode="P", convert=image_mock_1_converted)
        image_mock_2 = mocker.Mock(mode="RGB")
        mocker.patch(
            "image.editor.AnimatedImageEditor._find_actual_mode",
            lambda self: image_mock_2.mode,
        )
        mocker.patch(
            "image.editor.AnimatedImageEditor._get_frames",
            lambda self: (_ for _ in [image_mock_1, image_mock_2]),
        )

        image_editor = editor.AnimatedImageEditor(image_mock_1)
        image_editor.resize(**editor_options["resize"])
        [_ for _ in image_editor._processed_frames]

        assert image_mock_1.convert.call_args.args[0] == image_mock_2.mode
        assert (
            image_mock_1_converted.return_value.resize.call_args.kwargs
            == editor_options["resize"]
        )
        assert image_mock_2.resize.call_args.kwargs == editor_options["resize"]

    def test_save(self, mocker, editor_options):
        editor_options["save"].update({"save_all": True})
        image_mock_1, image_mock_2 = mocker.Mock(), mocker.Mock()
        mocker.patch(
            "image.editor.AnimatedImageEditor._find_actual_mode", lambda self: "RGB"
        )
        mocker.patch("image.editor.AnimatedImageEditor.convert_mode")
        output = mocker.Mock()

        image_editor = editor.AnimatedImageEditor(image_mock_1)
        image_editor._processed_frames = (_ for _ in [image_mock_1, image_mock_2])
        image_editor.save(output, **editor_options["save"])

        editor_options["save"].update({"append_images": [image_mock_2]})
        image_mock_1.save.assert_called_with(output, **editor_options["save"])
