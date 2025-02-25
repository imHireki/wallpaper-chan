import pytest


@pytest.fixture
def editor_options():
    return {
        "resize": {"size": (512, 512), "resample": 1, "reducing_gap": 2},
        "convert_mode": {"mode": "rgb"},
        "save": {"format": "webp", "quality": 75},
    }


SAVE_OPTIONS = {
    "GIF": {
        "format": "GIF",
        "optimize": True,
        "disposal": 2,
        "background": (0, 0, 0, 0),
        "save_all": True,
    },
    "JPEG": {"format": "JPEG", "optimize": True, "quality": 75},
    "PNG": {"format": "PNG", "optimize": True},
}


@pytest.fixture
def rgba_bands():
    return [
        [1, 2],  # R
        [1, 2],  # G
        [1, 2],  # B
        [1, 2],  # A
    ]
