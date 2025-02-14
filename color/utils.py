from __future__ import annotations
from binascii import hexlify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from color.palette import _RGB, _RGBA, _HSLA, _HSL, _HEX


def rgb_or_rgba_to_hex(color: _RGB | _RGBA) -> _HEX:
    return "#" + hexlify(bytearray(color)).decode("ascii")
