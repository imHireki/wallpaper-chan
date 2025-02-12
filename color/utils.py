from __future__ import annotations
from binascii import hexlify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from color.palette import _RGB, _RGBA, _HSLA, _HEX


def rgb_to_hex(RGB: _RGB) -> _HEX:
    return "#" + hexlify(bytearray(RGB)).decode("ascii")
