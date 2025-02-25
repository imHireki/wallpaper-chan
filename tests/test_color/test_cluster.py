from color import cluster


def test_sorted_color_cluster(mocker):
    color = mocker.Mock(
        get_color_bands=lambda: [],
        structure_palette=lambda _: ["blue", "blue", "blue", "red", "white", "red"],
    )

    color_cluster = cluster.SortedColorCluster(color)
    palette = color_cluster.get_palette()

    assert palette == ["blue", "red", "white"]
