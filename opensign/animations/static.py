# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Static and opacity animations."""

import time


class Static:
    """Animations that do not move the message."""

    @staticmethod
    def show(sign, message, **_kwargs):
        x, y = sign._position
        sign._draw(message, x, y)

    @staticmethod
    def hide(sign, message, **_kwargs):
        x, y = sign._position
        sign._draw(message, x, y, opacity=0)

    @staticmethod
    def blink(sign, message, count=3, duration=1, **_kwargs):
        delay = duration / count / 2
        for _ in range(count):
            start_time = time.monotonic()
            Static.hide(sign, message)
            start_time = sign._wait(start_time, delay)
            Static.show(sign, message)
            sign._wait(start_time, delay)

    @staticmethod
    def flash(sign, message, count=3, duration=1, **_kwargs):
        delay = duration / count / 2
        steps = max(1, 50 // count)
        for _ in range(count):
            Static.fade_out(sign, message, duration=delay, steps=steps)
            Static.fade_in(sign, message, duration=delay, steps=steps)

    @staticmethod
    def fade_in(sign, message, duration=1, steps=50, **_kwargs):
        current_x, current_y = sign._get_centered_position(message)
        delay = duration / (steps + 1)
        for opacity in range(steps + 1):
            start_time = time.monotonic()
            sign._draw(message, current_x, current_y, opacity=opacity / steps)
            sign._wait(start_time, delay)

    @staticmethod
    def fade_out(sign, message, duration=1, steps=50, **_kwargs):
        delay = duration / (steps + 1)
        for opacity in range(steps + 1):
            start_time = time.monotonic()
            sign._draw(
                message,
                sign._position[0],
                sign._position[1],
                opacity=(steps - opacity) / steps,
            )
            sign._wait(start_time, delay)
