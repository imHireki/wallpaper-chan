import pytest

from color import palette


@pytest.mark.parametrize("alpha", [True, False])
class TestHexRGB:
    def test_get_color_bands(self, mocker, rgba_bands, alpha):
        image = mocker.Mock(getdata=lambda band: rgba_bands[band])
        color = palette.HexRGB(image, alpha)
        assert color.get_color_bands() == rgba_bands[: 3 + 1 if alpha else 3]

    def test_structure_palette(self, mocker, rgba_bands, alpha):
        rgb_to_hex = mocker.patch(
            "color.utils.rgb_or_rgba_to_hex", return_value="#ffffff"
        )
        color = palette.HexRGB(mocker.Mock(), alpha)

        p = list(color.structure_palette(rgba_bands[: 3 + 1 if alpha else 3]))

        rgb_to_hex.assert_any_call((1, 1, 1, 1) if alpha else (1, 1, 1))
        rgb_to_hex.assert_any_call((2, 2, 2, 2) if alpha else (2, 2, 2))
        assert p == ["#ffffff"] * 2


@pytest.mark.parametrize("alpha", [True, False])
class TestRGB:
    def test_get_color_bands(self, mocker, rgba_bands, alpha):
        image = mocker.Mock(getdata=lambda band: rgba_bands[band])
        color = palette.RGB(image, alpha)
        assert color.get_color_bands() == rgba_bands[: 3 + 1 if alpha else 3]

    def test_structure_palette(self, mocker, rgba_bands, alpha):
        color = palette.RGB(mocker.Mock(), alpha)
        p = list(color.structure_palette(rgba_bands[: 3 + 1 if alpha else 3]))
        assert p == [(1, 1, 1, 1), (2, 2, 2, 2)] if alpha else [(1, 1, 1), (2, 2, 2)]
