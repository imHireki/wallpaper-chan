from typing import Sequence, Mapping

import PIL.Image


class ColorCluster:
    _image: PIL.Image.Image
    _rgb_sequences: tuple[Sequence]
    _colors: Mapping[tuple[Sequence], tuple[int]]

    def __init__(self, image: PIL.Image.Image) -> None:
        self._image = image
        self._rgb_sequences = self._get_rgb_sequences()
        self._colors = self._extract_colors()

    def _get_rgb_sequences(self) -> tuple[Sequence]:
        return [self._image.getdata(band) for band in range(3)]

    def _extract_colors(self) -> Mapping[tuple[Sequence], tuple[int]]:
        return map(lambda *rgb: tuple(rgb), *self._rgb_sequences)

    def _calculate_color_incidences(self) -> dict[tuple[int], int]:
        color_with_incidences: dict[tuple[int], int] = {}

        for color in self._colors:
            if color not in color_with_incidences:
                color_with_incidences[color] = 1
            else:
                color_with_incidences[color] += 1
        return color_with_incidences

    def sort_colors_by_incidences(self) -> list[tuple[int]]:
        return sorted(self._calculate_color_incidences(),
                      key=lambda color_with_incidences: color_with_incidences[1],
                      reverse=True)
