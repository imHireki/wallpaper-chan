import pytest


@pytest.fixture
def editor_options():
    return {
        "resize_options": {
            "size": (512, 512), "resample": 1, "reducing_gap": 2
        },
        "convert_mode_options": {"mode": "rgb"},
        "save_options": {"quality": 75, "format": "webp"}
    }
