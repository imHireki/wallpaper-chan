#!env/bin/python3

from PIL import Image
from numpy import asarray, product, histogram, argmax
from binascii import hexlify
from scipy import cluster


class WallpaperHandler:
    def __init__(self, fp):
        self.wallpaper_fp = fp
        self.wallpaper_pil = None
        self.image_asarray = None

    @staticmethod
    def resize_img(img, multiplier=0.25) -> object:
        """ Resize the Image to 10% of its size, return the resized image """
        size = ((round(x * multiplier))
                 for x in img.size)
        return img.resize(size, resample=Image.HAMMING)

    def open_image(self):
        """ Open image, call resize_img and set `self.wallpaper_pil` """
        img = Image.open(self.wallpaper_fp)
        self.wallpaper_pil = self.resize_img(img)

    def close_image(self):
        """ Close image and set `self.wallpaper_pil` to None """
        self.wallpaper_pil.close()
        self.wallpaper_pil = None

    def get_cluster_image_colors(self, clusters=10) -> object:
        """ Get the color CLUSTER from the `self.wallpaper_pil` object """
        ar = asarray(self.wallpaper_pil)
        shape = ar.shape
        ar = ar.reshape(product(shape[:2]),
                        shape[2]).astype(float)

        self.image_asarray = ar

        return cluster.vq.kmeans(ar, clusters)[0]

    def get_colors_hex(self, colors) -> list:
        """ Get HEX colors from a given list of colors from a CLUSTER """
        return [
            '#' +
            str(hexlify(bytearray((int(_) for _ in color))
                        ).decode('ascii')
                )
            for color in colors
            ]

    def get_sorted_colors_incidences(self, colors:list, codes) -> list:
        """ Get a sorted list of color and its incidences """

        # Make a graph with  the hex colors and its incidents
        vecs = cluster.vq.vq(self.image_asarray, codes)[0]
        counts = histogram(vecs, len(codes))[0]

        # Put it all back together as [ ('color', 'incidents'), ]
        color_incidences = [ (x, y)
                            for a, b in enumerate(colors)
                            for x, y in [
                                (colors[a], counts[a])
                                ]
                            ]
        # Sort the color_incidences by its incidences in descending order
        return sorted(color_incidences, key=lambda x: x[1], reverse=True)

    @staticmethod
    def get_sorted_colors(color_incidences:list) -> list:
        """ Get the sorted colors """
        return [_[0] for _ in color_incidences]


if __name__ == '__main__':
    wallpaper_fp = ''
    w = WallpaperHandler(wallpaper_fp)

    w.open_image()

    color_cluster = w.get_cluster_image_colors()
    hex_color_list = w.get_colors_hex(color_cluster)
    color_incidences = w.get_sorted_colors_incidences(hex_color_list,
                                                      color_cluster)
    sorted_colors = w.get_sorted_colors(color_incidences)

    w.close_image
