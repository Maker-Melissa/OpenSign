# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Color parsing helpers for PyOpenSign."""

from PIL import ImageColor


def _validate_channel(value):
    if not isinstance(value, int):
        raise ValueError("Color channels must be integers.")
    if not 0 <= value <= 255:
        raise ValueError("Color channels must be in the range 0-255.")
    return value


def parse_color(color):
    """Return *color* as an ``(R, G, B)`` tuple.

    Accepted values are CSS color names, hex strings, RGB/RGBA tuples or lists,
    and CircuitPython-style ``0xRRGGBB`` integers.
    """
    if isinstance(color, str):
        try:
            parsed = ImageColor.getrgb(color)
        except ValueError as error:
            raise ValueError(f"Unknown color: {color}") from error
        return parsed[:3]

    if isinstance(color, int):
        if not 0 <= color <= 0xFFFFFF:
            raise ValueError("Integer colors must be in the range 0x000000-0xFFFFFF.")
        return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)

    if isinstance(color, (tuple, list)) and len(color) in {3, 4}:
        return tuple(_validate_channel(channel) for channel in color[:3])

    raise ValueError("Color should be a CSS name, hex string, integer, or RGB tuple/list.")


def parse_color_alpha(color):
    """Return *color* as an ``(R, G, B, A)`` tuple."""
    if isinstance(color, (tuple, list)) and len(color) == 4:
        return (*parse_color(color[:3]), _validate_channel(color[3]))
    return (*parse_color(color), 255)
