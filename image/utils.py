from __future__ import annotations
from tempfile import NamedTemporaryFile
from io import BytesIO

import PIL.Image

from typing import TYPE_CHECKING, Generator


if TYPE_CHECKING:
    from image.editor import IEditor


def has_translucent_alpha(image: PIL.Image.Image) -> bool:
    bands_min_max = image.getextrema()

    if isinstance(bands_min_max[0], tuple) and len(bands_min_max) == 4:  # RGBA
        return bands_min_max[3][0] < 255
    return False


def bulk_resize(editor: IEditor, resize_save_options: list[dict]) -> Generator[BytesIO]:
    for options in resize_save_options:
        editor.resize(**options["resize"])
        result = BytesIO()
        editor.save(result, **options["save"])
        yield result


def bulk_resize_tempfile(
    editor: IEditor, resize_save_options: list[dict]
) -> Generator[str]:
    for options in resize_save_options:
        editor.resize(**options["resize"])
        tempfile = NamedTemporaryFile(delete=False)
        editor.save(tempfile, **options["save"])
        tempfile.close()
        yield tempfile.name
