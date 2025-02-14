from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Iterator

from PIL.Image import Image

if TYPE_CHECKING:
    from color.palette import ColorBands, ColorIterator, Color, IColor


SplitRGB = list[list[int]]
RGB = tuple[int, ...]


class ColorCluster:
    def __init__(self, image: Image) -> None:
        self._image: Image = image

    def get_colors(self) -> list[RGB]:
        rgb_sequences = self._get_rgb_sequences()
        colors = self._make_colors(rgb_sequences)
        colors_with_incidences = self._calculate_color_incidences(colors)
        return self._sort_colors_by_incidences(colors_with_incidences)

    def _get_rgb_sequences(self) -> SplitRGB:
        return [self._image.getdata(band) for band in range(3)]

    def _make_colors(self, rgb_sequences: SplitRGB) -> Iterator[RGB]:
        return map(lambda *rgb: tuple(rgb), *rgb_sequences)

    def _calculate_color_incidences(self, colors: Iterator[RGB]) -> dict[RGB, int]:
        color_with_incidences: dict[RGB, int] = {}

        for color in colors:
            color_with_incidences[color] = color_with_incidences.get(color, 0) + 1
        return color_with_incidences

    def _sort_colors_by_incidences(
        self, colors_with_incidences: dict[RGB, int]
    ) -> list[RGB]:
        return sorted(
            colors_with_incidences,
            key=lambda color_with_incidences: color_with_incidences[1],
            reverse=True,
        )


class SortedColorCluster:
    def __init__(self, color: IColor) -> None:
        self.color = color

    def get_palette(self) -> list[Color]:
        color_bands = self.get_color_bands()
        raw_palette = self.structure_raw_palette(color_bands)

        color_counts = self._count_colors(raw_palette)
        sorted_palette = self._sort_colors_by_count(color_counts)

        return sorted_palette

    def get_color_bands(self) -> ColorBands:
        return self.color.get_color_bands()

    def structure_raw_palette(self, color_bands: ColorBands) -> ColorIterator:
        return self.color.structure_raw_palette(color_bands)

    @staticmethod
    def _count_colors(raw_palette: ColorIterator) -> dict[Color, int]:
        color_counts: dict[Color, int] = {}

        for color in raw_palette:
            color_counts[color] = color_counts.get(color, 0) + 1
        return color_counts

    @staticmethod
    def _sort_colors_by_count(color_counts: dict[Color, int]) -> list[Color]:
        return sorted(color_counts, key=lambda key: color_counts[key], reverse=True)
