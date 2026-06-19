# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Scroll animations."""

import time


class Scroll:
    """Move messages on or off the display."""

    @staticmethod
    def from_to(sign, message, duration, start_x, start_y, end_x, end_y):
        steps = max(abs(end_x - start_x), abs(end_y - start_y))
        if not steps:
            return
        increment_x = (end_x - start_x) / steps
        increment_y = (end_y - start_y) / steps
        for i in range(steps + 1):
            start_time = time.monotonic()
            current_x = start_x + round(i * increment_x)
            current_y = start_y + round(i * increment_y)
            sign._draw(message, current_x, current_y)
            if i <= steps:
                sign._wait(start_time, duration / steps)

    @staticmethod
    def in_from_left(sign, message, duration=1, x=0, **_kwargs):
        center_x, center_y = sign._get_centered_position(message)
        Scroll.from_to(sign, message, duration, -message.width, center_y, center_x + x, center_y)

    @staticmethod
    def in_from_right(sign, message, duration=1, x=0, **_kwargs):
        center_x, center_y = sign._get_centered_position(message)
        Scroll.from_to(sign, message, duration, sign.width, center_y, center_x + x, center_y)

    @staticmethod
    def in_from_top(sign, message, duration=1, y=0, **_kwargs):
        center_x, center_y = sign._get_centered_position(message)
        Scroll.from_to(sign, message, duration, center_x, -message.height, center_x, center_y + y)

    @staticmethod
    def in_from_bottom(sign, message, duration=1, y=0, **_kwargs):
        center_x, center_y = sign._get_centered_position(message)
        Scroll.from_to(sign, message, duration, center_x, sign.height, center_x, center_y + y)

    @staticmethod
    def out_to_left(sign, message, duration=1, **_kwargs):
        current_x, current_y = sign._position
        Scroll.from_to(sign, message, duration, current_x, current_y, -message.width, current_y)

    @staticmethod
    def out_to_right(sign, message, duration=1, **_kwargs):
        current_x, current_y = sign._position
        Scroll.from_to(sign, message, duration, current_x, current_y, sign.width, current_y)

    @staticmethod
    def out_to_top(sign, message, duration=1, **_kwargs):
        current_x, current_y = sign._position
        Scroll.from_to(sign, message, duration, current_x, current_y, current_x, -message.height)

    @staticmethod
    def out_to_bottom(sign, message, duration=1, **_kwargs):
        current_x, current_y = sign._position
        Scroll.from_to(sign, message, duration, current_x, current_y, current_x, sign.height)
