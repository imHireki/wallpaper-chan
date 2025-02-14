from color import utils


def test_rgb_or_rgba_to_hex():
    assert utils.rgb_or_rgba_to_hex((66, 135, 245)) == "#4287f5"
    assert utils.rgb_or_rgba_to_hex((4, 1, 255, 100)) == "#0401ff64"
