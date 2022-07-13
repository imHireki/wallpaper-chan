from color import palette


def test_dominant_color(mocker):
    sorted_colors = [(255, 255, 255), (0, 0, 0)]
    color_cluster = mocker.Mock(sort_colors_by_incidences=lambda: sorted_colors)

    dominant_color = palette.DominantColor(color_cluster)

    dominant_color_as_hex = dominant_color._hexlify_rgb(sorted_colors[0])

    assert dominant_color.get_palette_data() == sorted_colors[0]
    assert dominant_color.get_palette_data_as_hex() == dominant_color_as_hex


def test_range_color_palette(mocker):
    sorted_colors = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]
    color_cluster = mocker.Mock(sort_colors_by_incidences=lambda: sorted_colors)

    range_color_palette = palette.RangeColorPalette(color_cluster)

    sorted_colors_as_hex = [range_color_palette._hexlify_rgb(color)
                            for color in sorted_colors]

    assert range_color_palette.get_palette_data(5, 3, 2) == sorted_colors[3:5:2]
    assert range_color_palette.get_palette_data_as_hex(2) == sorted_colors_as_hex[:2]
