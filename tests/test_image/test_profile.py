import pytest

from tests.conftest import SAVE_OPTIONS
from image import profile


class TestStaticJpegRgbProfile:
    def test_name(self):
        assert profile.StaticJpegRgbProfile.name == "JPEG_RGB"

    def test_is_optimized(self, mocker):
        assert profile.StaticJpegRgbProfile(mocker.Mock()).is_optimized() is True

    def test_get_editor(self, mocker):
        editor = mocker.patch("image.editor.StaticEditor")
        _profile = profile.StaticJpegRgbProfile(mocker.Mock())

        assert _profile.get_editor()
        assert editor.call_args.args[0] == _profile._image

    def test_get_color_clustering_image(self, mocker):
        _profile = profile.StaticJpegRgbProfile(mocker.Mock())
        image = _profile.get_color_clustering_image()

        assert image == _profile._image


class TestStaticWebpRgbProfile:
    def test_name(self):
        assert profile.StaticWebpRgbProfile.name == "WEBP_RGB"

    def test_is_optimized(self, mocker):
        assert profile.StaticWebpRgbProfile(mocker.Mock()).is_optimized() is False

    def test_optimize(self, mocker):
        mocker.patch("image.editor.StaticEditor")
        output = mocker.Mock()

        _profile = profile.StaticWebpRgbProfile(mocker.Mock())
        editor = _profile._editor = mocker.Mock()
        _profile.optimize(output, SAVE_OPTIONS)

        editor.save.assert_called_with(output, **SAVE_OPTIONS["JPEG"])


class TestStaticWebpRgbaProfile:
    def test_name(self):
        assert profile.StaticWebpRgbaProfile.name == "WEBP_RGBA"

    def test_is_optimized(self, mocker):
        assert profile.StaticWebpRgbaProfile(mocker.Mock()).is_optimized() is False

    @pytest.mark.parametrize(
        "extrema, save_options",
        [
            [((0, 255), (0, 255), (0, 255), (255, 255)), SAVE_OPTIONS["JPEG"]],
            [((0, 255), (0, 255), (0, 255), (0, 255)), SAVE_OPTIONS["PNG"]],
        ],
    )
    def test_optimize(self, mocker, extrema, save_options):
        image = mocker.Mock(getextrema=lambda: extrema)
        output = mocker.Mock()

        _profile = profile.StaticWebpRgbaProfile(image)
        editor = _profile._editor = mocker.Mock()

        opts = {save_options["format"]: save_options}
        _profile.optimize(output, opts)

        if save_options["format"] == "JPEG":
            editor.convert_mode.assert_called_with("RGB")
        else:
            editor.convert_mode.assert_not_called()
        editor.save.assert_called_with(output, **save_options)


class TestStaticPngRgbProfile:
    def test_name(self):
        assert profile.StaticPngRgbProfile.name == "PNG_RGB"

    def test_is_optimized(self, mocker):
        assert profile.StaticPngRgbProfile(mocker.Mock()).is_optimized() is False

    def test_optimize(self, mocker):
        mocker.patch("image.editor.StaticEditor")
        output = mocker.Mock()

        _profile = profile.StaticPngRgbProfile(mocker.Mock())
        editor = _profile._editor = mocker.Mock()
        _profile.optimize(output, SAVE_OPTIONS)

        editor.save.assert_called_with(output, **SAVE_OPTIONS["JPEG"])


class TestStaticPngRgbaProfile:
    def test_name(self):
        assert profile.StaticPngRgbaProfile.name == "PNG_RGBA"

    @pytest.mark.parametrize(
        "extrema, is_translucent",
        [
            [((0, 255), (0, 255), (0, 255), (255, 255)), False],
            [((0, 255), (0, 255), (0, 255), (0, 255)), True],
        ],
    )
    def test_is_optimized(self, mocker, extrema, is_translucent):
        image = mocker.Mock(getextrema=lambda: extrema)
        is_optimized = profile.StaticPngRgbaProfile(image).is_optimized()

        assert is_optimized == is_translucent

    def test_optimize(self, mocker):
        mocker.patch("image.editor.StaticEditor")
        output = mocker.Mock()

        _profile = profile.StaticPngRgbaProfile(mocker.Mock())
        editor = _profile._editor = mocker.Mock()
        _profile.optimize(output, SAVE_OPTIONS)

        editor.convert_mode.assert_called_with("RGB")
        editor.save.assert_called_with(output, **SAVE_OPTIONS["JPEG"])


class TestAnimatedGifPProfile:
    def test_name(self):
        assert profile.AnimatedGifPProfile.name == "GIF_P"

    @pytest.mark.parametrize("is_animated", [True, False])
    def test_is_optimized(self, mocker, is_animated):
        image = mocker.Mock(is_animated=is_animated)

        is_optimized = profile.AnimatedGifPProfile(image).is_optimized()

        assert is_optimized is is_animated

    @pytest.mark.parametrize(
        "info, save_options",
        [[{"transparency": 1}, SAVE_OPTIONS["PNG"]], [{}, SAVE_OPTIONS["JPEG"]]],
    )
    def test_optimize(self, mocker, info, save_options):
        mocker.patch("image.editor.AnimatedEditor")
        image_mock = mocker.Mock(info=info)
        output = mocker.Mock()

        _profile = profile.AnimatedGifPProfile(image_mock)
        editor = _profile._editor = mocker.Mock()
        _profile.optimize(output, SAVE_OPTIONS)

        editor.save.assert_called_with(output, **save_options)

    def test_get_editor(self, mocker):
        editor = mocker.patch("image.editor.AnimatedEditor")
        image = mocker.Mock()
        _profile = profile.AnimatedGifPProfile(image)

        assert _profile.get_editor()
        editor.assert_called_with(image)

    def test_get_color_clustering_image(self, mocker):
        mocker.patch("image.editor.AnimatedEditor")
        image = mocker.Mock()

        _profile = profile.AnimatedGifPProfile(image)
        editor = _profile._editor = mocker.Mock()
        ccimage = _profile.get_color_clustering_image()

        assert ccimage
        image.convert.assert_called_with(editor.actual_mode)


class TestAnimatedWebpRgbaProfile:
    def test_name(self):
        assert profile.AnimatedWebpRgbaProfile.name == "WEBP_RGBA"

    def test_is_optimized(self, mocker):
        is_optimized = profile.AnimatedWebpRgbaProfile(mocker.Mock()).is_optimized()
        assert is_optimized is False

    def test_optimize(self, mocker):
        mocker.patch("image.editor.AnimatedEditor")
        output = mocker.Mock()

        _profile = profile.AnimatedWebpRgbaProfile(mocker.Mock())
        editor = _profile._editor = mocker.Mock()
        _profile.optimize(output, SAVE_OPTIONS)

        editor.save.assert_called_with(output, **SAVE_OPTIONS["GIF"])


class TestAnimatedWebpRgbProfile:
    def test_name(self):
        assert profile.AnimatedWebpRgbProfile.name == "WEBP_RGB"

    def test_is_optimized(self, mocker):
        is_optimized = profile.AnimatedWebpRgbProfile(mocker.Mock()).is_optimized()
        assert is_optimized is False

    def test_optimize(self, mocker):
        mocker.patch("image.editor.AnimatedEditor")
        output = mocker.Mock()

        _profile = profile.AnimatedWebpRgbProfile(mocker.Mock())
        editor = _profile._editor = mocker.Mock()
        _profile.optimize(output, SAVE_OPTIONS)

        editor.save.assert_called_with(output, **SAVE_OPTIONS["GIF"])
