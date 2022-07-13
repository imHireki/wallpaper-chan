from color import palette


def test_dominant_color(mocker):
    sorted_colors = [(255, 255, 255), (0, 0, 0)]
    color_cluster = mocker.Mock(sort_colors_by_incidences=lambda: sorted_colors)

    dominant_color = palette.DominantColor(color_cluster)

    dominant_color_as_hex = dominant_color._hexlify_rgb(sorted_colors[0])

    assert dominant_color.get_palette_data() == sorted_colors[0]
    assert dominant_color.get_palette_data_as_hex() == dominant_color_as_hex
