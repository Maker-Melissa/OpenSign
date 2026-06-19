# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Fade animations."""

import time


class Fade:
    """Fade messages in or out as a whole."""

    @staticmethod
    def in_(sign, message, duration=1, steps=50, **_kwargs):
        """Fade the message in."""
        current_x, current_y = sign._get_centered_position(message)
        delay = duration / (steps + 1)
        for opacity in range(steps + 1):
            start_time = time.monotonic()
            sign._draw(message, current_x, current_y, opacity=opacity / steps)
            sign._wait(start_time, delay)

    @staticmethod
    def out(sign, message, duration=1, steps=50, **_kwargs):
        """Fade the message out."""
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
