from io import BytesIO

from PIL import Image

from color import cluster, palette
from example_settings import SAVE_OPTIONS, SUPPORTED_IMAGES
from image.category import CategoryProxy
from image.utils import bulk_resize


def get_palette(image_name):
    with Image.open(image_name) as image:
        category = CategoryProxy(image, SUPPORTED_IMAGES)
        profile = category.get_profile()

        if not profile:
            raise Exception(f"Unsupported image type: {image.format}/{image.mode}.")

        cc_image = profile.get_color_clustering_image()
        color = palette.HexRGB(cc_image, alpha=False)
        color_cluster = cluster.SortedColorCluster(color)

        sorted_palette = color_cluster.get_palette()
        dominant_color = sorted_palette[0]
        return (dominant_color, sorted_palette)


def resize(image_name):
    def _resize_helper(editor):
        return bulk_resize(
            editor,
            [
                {
                    "resize": {"size": size, "resample": 1, "reducing_gap": 3},
                    "save": {"format": "JPEG", "optimize": True, "quality": 75},
                }
                for size in [(256, 256), (128, 128)]
            ],
        )

    original_img = Image.open(image_name)
    category = CategoryProxy(original_img, SUPPORTED_IMAGES)
    profile = category.get_profile()

    if not profile:
        raise Exception(
            f"Unsupported image type: {original_img.format}/{original_img.mode}."
        )

    editor = profile.get_editor()

    # Avoid format-related problems by resizing the optimized image
    if not profile.is_optimized():
        output = BytesIO()
        profile.optimize(output, SAVE_OPTIONS)  # type: ignore

        original_img.close()

        with Image.open(output) as optimized_image:
            optimized_category = CategoryProxy(optimized_image, SUPPORTED_IMAGES)
            optimized_profile = optimized_category.get_profile()
            resized = _resize_helper(optimized_profile.get_editor())  # type: ignore
            return [next(resized), next(resized)]

    # Resize the original image
    resized_gen = _resize_helper(editor)
    resized = [next(resized_gen), next(resized_gen)]
    original_img.close()
    return resized


if __name__ == "__main__":
    resize("example_image.png")
    get_palette("example_image.png")
