#!env/bin/python3

from PIL import Image


class WallpaperHandler:
    wallpaper_fp = str
    image_obj = object

    def set_image_obj(self) -> object:
        with Image.open(self.wallpaper_fp) as pil_image:
            self.image_obj = pil_image
            return

    @classmethod
    def get_color_palette(cls):
        ...


if __name__ == '__main__':
    w = WallpaperHandler()
    w.wallpaper_fp = ''
    w.set_image_obj()
