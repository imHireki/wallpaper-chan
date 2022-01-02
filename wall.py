#!env/bin/python3

from PIL import Image
from numpy import asarray, product, histogram, argmax
from binascii import hexlify
from scipy import cluster


class WallpaperHandler:
    def __init__(self, fp):
        self.wallpaper_fp = fp

    @staticmethod
    def resize_img(img) -> object:

        # Generator
        size = ((round(x * 0.2))
                 for x in img.size)

        return img.resize(size, resample=Image.HAMMING)

    def get_color_palette(self) -> list:
        # TODO: receive a gradient
        with Image.open(self.wallpaper_fp) as wall_pil:
            wall_pil = self.resize_img(wall_pil)

            # Cluster
            ar =  asarray(wall_pil)
            shape = ar.shape
            ar = ar.reshape(product(shape[:2]),
                            shape[2]
                            ).astype(float)

            CLUSTERS = 10
            codes = cluster.vq.kmeans(ar, CLUSTERS)[0]

            # TODO
            palette = [
                    '#' + str(
                        hexlify(
                            bytearray(
                                (int(_) for _ in code)
                            )
                        ).decode('ascii')
                    )
                    for code in codes
                ]



if __name__ == '__main__':
    wallpaper_fp = ''
    w = WallpaperHandler(wallpaper_fp)
    w.get_color_palette()
