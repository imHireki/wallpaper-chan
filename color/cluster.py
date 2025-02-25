from color.palette import ColorBands, ColorIterator, Color, IColor


class SortedColorCluster:
    def __init__(self, color: IColor) -> None:
        self.color = color

    def get_palette(self) -> list[Color]:
        color_bands = self.get_color_bands()
        raw_palette = self.structure_palette(color_bands)

        color_counts = self._count_colors(raw_palette)
        sorted_palette = self._sort_colors_by_count(color_counts)

        return sorted_palette

    def get_color_bands(self) -> ColorBands:
        return self.color.get_color_bands()

    def structure_palette(self, color_bands: ColorBands) -> ColorIterator:
        return self.color.structure_palette(color_bands)

    @staticmethod
    def _count_colors(raw_palette: ColorIterator) -> dict[Color, int]:
        color_counts: dict[Color, int] = {}

        for color in raw_palette:
            color_counts[color] = color_counts.get(color, 0) + 1
        return color_counts

    @staticmethod
    def _sort_colors_by_count(color_counts: dict[Color, int]) -> list[Color]:
        return sorted(color_counts, key=lambda key: color_counts[key], reverse=True)
