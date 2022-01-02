#!env/bin/python3

from PIL import Image


class WallpaperHandler:
    wallpaper_path = '~/.wallpaper.jpg'
    wallpaper = ...

    @classmethod
    def set_wallpaper(cls) -> object:
        with Image.open(cls.wallpaper_path) as wallpaper:
            cls.wallpaper = wallpaper
            return


if __name__ == '__main__':
    wall = WallpaperHandler()
    wall.set_wallpaper()
