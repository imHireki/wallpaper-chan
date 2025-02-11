import pytest

from image import utils


@pytest.mark.parametrize(
    "extrema, bands",
    [
        [False, (0, 255)],  # GreySlcale
        [False, ((0, 255), (0, 255), (0, 255))],  # RGB
        [True, ((0, 255), (0, 255), (0, 255), (0, 255))],  # RGBA wo translucency
        [True, ((0, 255), (0, 255), (0, 255), (0, 100))],  # RGBA w translucency
    ],
)
def test_has_translucent_alpha(mocker, bands, extrema):
    img = mocker.Mock(getextrema=lambda: bands)
    hta = utils.has_translucent_alpha(img)

    assert hta == extrema
