from color import palette


def test_dominant_color(mocker):
    sorted_colors = [(255, 255, 255), (0, 0, 0)]
    color_cluster_mock = mocker.Mock(get_colors=lambda: sorted_colors)

    dominant_color = palette.DominantColor(color_cluster_mock)
    palette_data = dominant_color.get_palette_data()
    palette_data_as_hex = dominant_color.get_palette_data_as_hex()

    assert palette_data_as_hex == dominant_color._hexlify_rgb(sorted_colors[0])
    assert palette_data == sorted_colors[0]


def test_range_color_palette(mocker):
    sorted_colors = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]
    color_cluster_mock = mocker.Mock(get_colors=lambda: sorted_colors)

    range_color_palette = palette.RangeColorPalette(color_cluster_mock)
    palette_data = range_color_palette.get_palette_data(5, 3, 2)
    palette_data_as_hex = range_color_palette.get_palette_data_as_hex(2)

    assert palette_data == sorted_colors[3:5:2]
    assert (
        palette_data_as_hex
        == [range_color_palette._hexlify_rgb(color) for color in sorted_colors][:2]
    )


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
