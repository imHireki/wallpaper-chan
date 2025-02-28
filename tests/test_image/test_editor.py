import pytest

from image import editor


class TestStaticImageEditor:
    def test_actual_mode(self, mocker):
        image_mode = "RGB"
        _editor = editor.StaticEditor(mocker.Mock(mode=image_mode))

        assert _editor.actual_mode == image_mode

    def test_convert_mode(self, mocker):
        image = mocker.Mock()
        _editor = editor.StaticEditor(image)
        _editor.convert_mode("RGBA")

        image.convert.assert_called_with(mode="RGBA")

    def test_resize(self, mocker, editor_options):
        image = mocker.Mock()
        _editor = editor.StaticEditor(image)
        _editor.resize(**editor_options["resize"])

        image.resize.assert_called_with(**editor_options["resize"])

    def test_save(self, mocker, editor_options):
        fp = mocker.Mock()

        _editor = editor.StaticEditor(mocker.Mock())
        edited_image = mocker.patch.object(_editor, "_processed_image")
        _editor.save(fp, **editor_options["save"])

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
        _editor = editor.AnimatedEditor(
            mocker.Mock(mode=mode, getextrema=lambda: extrema, info=_info)
        )
        assert _editor.actual_mode == _actual_mode

    def test_convert_mode(self, mocker):
        new_mode = "RGBA"
        image_1 = mocker.Mock(mode="P")
        image_2 = mocker.Mock(mode="RGB")
        mocker.patch(
            "image.editor.AnimatedEditor._find_actual_mode",
            lambda _: image_2.mode,
        )
        mocker.patch(
            "image.editor.AnimatedEditor._get_frames",
            lambda _: (_ for _ in [image_1, image_2]),
        )

        _editor = editor.AnimatedEditor(image_1)
        _editor.convert_mode(new_mode)
        [_ for _ in _editor._processed_frames]

        image_1.convert.assert_called_with(mode=new_mode)
        image_2.copy.assert_called()

    def test_resize(self, mocker, editor_options):
        image_1_converted = mocker.Mock()
        image_1 = mocker.Mock(mode="P", convert=image_1_converted)
        image_2 = mocker.Mock(mode="RGB")
        mocker.patch(
            "image.editor.AnimatedEditor._find_actual_mode",
            lambda _: image_2.mode,
        )
        mocker.patch(
            "image.editor.AnimatedEditor._get_frames",
            lambda _: (_ for _ in [image_1, image_2]),
        )

        _editor = editor.AnimatedEditor(image_1)
        _editor.resize(**editor_options["resize"])
        [_ for _ in _editor._processed_frames]

        image_1.convert.assert_called_with(image_2.mode)
        image_1_converted().resize.assert_called_with(**editor_options["resize"])
        image_2.resize.assert_called_with(**editor_options["resize"])

    def test_save(self, mocker, editor_options):
        editor_options["save"].update({"save_all": True})
        image_1, image_2 = mocker.Mock(), mocker.Mock()
        mocker.patch("image.editor.AnimatedEditor._find_actual_mode", lambda _: "RGB")
        mocker.patch("image.editor.AnimatedEditor.convert_mode")
        output = mocker.Mock()

        _editor = editor.AnimatedEditor(image_1)
        _editor._processed_frames = (_ for _ in [image_1, image_2])
        _editor.save(output, **editor_options["save"])

        editor_options["save"].update({"append_images": [image_2]})
        image_1.save.assert_called_with(output, **editor_options["save"])
