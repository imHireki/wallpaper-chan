from typing import Sequence, Mapping

import PIL.Image


RGBSequences = tuple[Sequence]
RGB = tuple[int]


class ColorCluster:
    def __init__(self, image: PIL.Image.Image) -> None:
        self._image: PIL.Image.Image = image

    def get_colors(self) -> list[RGB]:
        rgb_sequences = self._get_rgb_sequences()
        colors = self._extract_colors(rgb_sequences)
        colors_with_incidences = self._calculate_color_incidences(colors)
        return self._sort_colors_by_incidences(colors_with_incidences)

    def _get_rgb_sequences(self) -> RGBSequences:
        return [self._image.getdata(band) for band in range(3)]

    def _extract_colors(self, rgb_sequences: RGBSequences
                        ) -> Mapping[RGBSequences, RGB]:
        return map(lambda *rgb: tuple(rgb), *rgb_sequences)

    def _calculate_color_incidences(
            self, colors: Mapping[RGBSequences, RGB]) -> dict[RGB, int]:
        color_with_incidences: dict[RGB, int] = {}

        for color in colors:
            if color not in color_with_incidences:
                color_with_incidences[color] = 1
            else:
                color_with_incidences[color] += 1
        return color_with_incidences

    def _sort_colors_by_incidences(
            self, colors_with_incidences: dict[RGB, int]) -> list[RGB]:
        return sorted(
            colors_with_incidences,
            key=lambda color_with_incidences: color_with_incidences[1],
            reverse=True)
