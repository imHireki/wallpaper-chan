import pytest

from color import cluster


def test_color_cluster(mocker):
    def get_data(band):
        vertically_align_color_bands = [(255, 255, 255, 0, 0),
                                        (255, 255, 255, 0, 0),
                                        (255, 255, 255, 0, 0)]
        return vertically_align_color_bands[band]

    sorted_colors = [(255, 255, 255), (0, 0, 0)]

    image = mocker.Mock(getdata=get_data)
    color_cluster = cluster.ColorCluster(image)

    assert color_cluster.sort_colors_by_incidences() == sorted_colors
