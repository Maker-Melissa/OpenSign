# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Fade animations."""

import time

from . import Animation


class Fade(Animation):
    """Fade messages in or out as a whole."""

    def in_(self, message, duration=1, steps=50, **_kwargs):
        """Fade the message in."""
        current_x, current_y = self.centered_position(message)
        delay = duration / (steps + 1)
        for opacity in range(steps + 1):
            start_time = time.monotonic()
            self.draw(message, current_x, current_y, opacity=opacity / steps)
            self.wait(start_time, delay)

    def out(self, message, duration=1, steps=50, **_kwargs):
        """Fade the message out."""
        delay = duration / (steps + 1)
        for opacity in range(steps + 1):
            start_time = time.monotonic()
            self.draw(
                message,
                self.position[0],
                self.position[1],
                opacity=(steps - opacity) / steps,
            )
            self.wait(start_time, delay)
