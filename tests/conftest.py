import pytest


@pytest.fixture
def editor_options_mock(mocker):
    resize_options = {"size": (512, 512), "resample": 2, "reducing_gap": 2}
    save_options = {"quality": 75, "format": "WEBP"}
    return mocker.Mock(resize_options=resize_options, save_options=save_options)
