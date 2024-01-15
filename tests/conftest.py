import pytest


@pytest.fixture
def editor_options():
    return {
        "resize_options": {
            "size": (512, 512), "resample": 1, "reducing_gap": 2
        },
        "convert_mode_options": {"mode": "rgb"},
        "save_options": {"format": "webp", "quality": 75}
    }

SAVE_OPTIONS = {
    "GIF": {
        "format": "GIF",
        "optimize": True,
        "disposal": 2,
        "background": (0,0,0,0),
        "save_all": True
    },
    "JPEG": {
        "format": "JPEG",
        "optimize": True,
        "quality": 75
    },
    "PNG": {
        "format": "PNG",
        "optimize": True
    },
}
