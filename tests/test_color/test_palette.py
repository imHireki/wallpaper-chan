from color import palette


class TestHexRGB:
    def test_get_color_bands(self, mocker, rgba_bands):
        image = mocker.Mock(getdata=lambda band: rgba_bands[band])
        color = palette.HexRGB(image)
        assert color.get_color_bands() == rgba_bands[:3]

    def test_structure_raw_palette(self, mocker, rgba_bands):
        rgb_to_hex = mocker.patch("color.utils.rgb_to_hex", return_value="#ffffff")
        color = palette.HexRGB(mocker.Mock())

        rp = list(color.structure_raw_palette(rgba_bands[:3]))

        rgb_to_hex.assert_any_call((1, 1, 1))
        rgb_to_hex.assert_any_call((2, 2, 2))
        assert rp == ["#ffffff"] * 2


class TestRGBA:
    def test_get_color_bands(self, mocker, rgba_bands):
        image = mocker.Mock(getdata=lambda band: rgba_bands[band])
        color = palette.RGBA(image)
        assert color.get_color_bands() == rgba_bands

    def test_structure_raw_palette(self, mocker, rgba_bands):
        color = palette.RGBA(mocker.Mock())
        rp = list(color.structure_raw_palette(rgba_bands))
        assert rp == [(1, 1, 1, 1), (2, 2, 2, 2)]
