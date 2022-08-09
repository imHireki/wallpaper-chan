from abc import ABC, abstractmethod
import tempfile

import PIL.Image

from . import editor


class IStaticImageInfo(ABC):
    _image_editor: editor.StaticImageEditor

    def __init__(self, image: PIL.Image.Image) -> None:
        self._image: PIL.Image.Image = image

    @classmethod
    @abstractmethod
    def name(cls) -> str: pass

    @abstractmethod
    def is_standardized(self) -> bool: pass

    @abstractmethod
    def standardize(self) -> tempfile.NamedTemporaryFile: pass

    def get_image_editor(self) -> editor.StaticImageEditor:
        if not hasattr(self, '_image_editor'):
            self._image_editor = editor.StaticImageEditor(self._image)
        return self._image_editor

    def get_image_for_color_clustering(self) -> PIL.Image.Image:
        return self._image
