from color import cluster


def test_sorted_color_cluster(mocker):
    color = mocker.Mock(
        get_color_bands=lambda: [],
        structure_raw_palette=lambda _: ["blue", "blue", "blue", "red", "white", "red"],
    )

    pixel_cluster = cluster.SortedColorCluster(color)
    palette = pixel_cluster.get_palette()

    assert palette == ["blue", "red", "white"]
