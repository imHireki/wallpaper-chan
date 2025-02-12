from color import utils


def test_rgb_to_hex():
    assert utils.rgb_to_hex((255, 255, 255)) == "#ffffff"
    assert utils.rgb_to_hex((66, 135, 245)) == "#4287f5"
