# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Wipe animations."""

import time


class Wipe:
    """Reveal or conceal messages by cropping from a direction."""

    @staticmethod
    def _wait(sign, start_time, duration, steps):
        if steps:
            sign._wait(start_time, duration / steps)

    @staticmethod
    def _draw_crop(sign, message, box, x, y):
        image = message.get_image().crop(box=box)
        sign._draw_image(
            image,
            x,
            y,
            message.opacity,
            message.shadow_intensity,
            message.shadow_offset,
        )

    @staticmethod
    def in_from_left(sign, message, duration=1, **_kwargs):
        x, y = sign._get_centered_position(message)
        for width in range(1, message.width + 1):
            start_time = time.monotonic()
            Wipe._draw_crop(sign, message, (0, 0, width, message.height), x, y)
            Wipe._wait(sign, start_time, duration, message.width)
        sign._position = (x, y)

    @staticmethod
    def in_from_right(sign, message, duration=1, **_kwargs):
        x, y = sign._get_centered_position(message)
        for width in range(1, message.width + 1):
            start_time = time.monotonic()
            left = message.width - width
            Wipe._draw_crop(
                sign,
                message,
                (left, 0, message.width, message.height),
                x + left,
                y,
            )
            Wipe._wait(sign, start_time, duration, message.width)
        sign._position = (x, y)

    @staticmethod
    def in_from_top(sign, message, duration=1, **_kwargs):
        x, y = sign._get_centered_position(message)
        for height in range(1, message.height + 1):
            start_time = time.monotonic()
            Wipe._draw_crop(sign, message, (0, 0, message.width, height), x, y)
            Wipe._wait(sign, start_time, duration, message.height)
        sign._position = (x, y)

    @staticmethod
    def in_from_bottom(sign, message, duration=1, **_kwargs):
        x, y = sign._get_centered_position(message)
        for height in range(1, message.height + 1):
            start_time = time.monotonic()
            top = message.height - height
            Wipe._draw_crop(
                sign,
                message,
                (0, top, message.width, message.height),
                x,
                y + top,
            )
            Wipe._wait(sign, start_time, duration, message.height)
        sign._position = (x, y)

    @staticmethod
    def out_to_left(sign, message, duration=1, **_kwargs):
        x, y = sign._position
        for width in range(message.width, 0, -1):
            start_time = time.monotonic()
            Wipe._draw_crop(sign, message, (0, 0, width, message.height), x, y)
            Wipe._wait(sign, start_time, duration, message.width)
        sign._draw(message, x, y, opacity=0)

    @staticmethod
    def out_to_right(sign, message, duration=1, **_kwargs):
        x, y = sign._position
        for width in range(message.width, 0, -1):
            start_time = time.monotonic()
            left = message.width - width
            Wipe._draw_crop(
                sign,
                message,
                (left, 0, message.width, message.height),
                x + left,
                y,
            )
            Wipe._wait(sign, start_time, duration, message.width)
        sign._draw(message, x, y, opacity=0)

    @staticmethod
    def out_to_top(sign, message, duration=1, **_kwargs):
        x, y = sign._position
        for height in range(message.height, 0, -1):
            start_time = time.monotonic()
            Wipe._draw_crop(sign, message, (0, 0, message.width, height), x, y)
            Wipe._wait(sign, start_time, duration, message.height)
        sign._draw(message, x, y, opacity=0)

    @staticmethod
    def out_to_bottom(sign, message, duration=1, **_kwargs):
        x, y = sign._position
        for height in range(message.height, 0, -1):
            start_time = time.monotonic()
            top = message.height - height
            Wipe._draw_crop(
                sign,
                message,
                (0, top, message.width, message.height),
                x,
                y + top,
            )
            Wipe._wait(sign, start_time, duration, message.height)
        sign._draw(message, x, y, opacity=0)
