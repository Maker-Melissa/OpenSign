# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Scroll animations."""

import time

from . import Animation


class Scroll(Animation):
    """Move messages on or off the display."""

    def from_to(self, message, duration, start_x, start_y, end_x, end_y):
        """Scroll the message between two positions."""
        steps = max(abs(end_x - start_x), abs(end_y - start_y))
        if not steps:
            return
        increment_x = (end_x - start_x) / steps
        increment_y = (end_y - start_y) / steps
        for i in range(steps + 1):
            start_time = time.monotonic()
            current_x = start_x + round(i * increment_x)
            current_y = start_y + round(i * increment_y)
            self.draw(message, current_x, current_y)
            if i <= steps:
                self.wait(start_time, duration / steps)

    def in_from_left(self, message, duration=1, x=0, **_kwargs):
        center_x, center_y = self.centered_position(message)
        self.from_to(message, duration, -message.width, center_y, center_x + x, center_y)

    def in_from_right(self, message, duration=1, x=0, **_kwargs):
        center_x, center_y = self.centered_position(message)
        self.from_to(message, duration, self.width, center_y, center_x + x, center_y)

    def in_from_top(self, message, duration=1, y=0, **_kwargs):
        center_x, center_y = self.centered_position(message)
        self.from_to(message, duration, center_x, -message.height, center_x, center_y + y)

    def in_from_bottom(self, message, duration=1, y=0, **_kwargs):
        center_x, center_y = self.centered_position(message)
        self.from_to(message, duration, center_x, self.height, center_x, center_y + y)

    def out_to_left(self, message, duration=1, **_kwargs):
        current_x, current_y = self.position
        self.from_to(message, duration, current_x, current_y, -message.width, current_y)

    def out_to_right(self, message, duration=1, **_kwargs):
        current_x, current_y = self.position
        self.from_to(message, duration, current_x, current_y, self.width, current_y)

    def out_to_top(self, message, duration=1, **_kwargs):
        current_x, current_y = self.position
        self.from_to(message, duration, current_x, current_y, current_x, -message.height)

    def out_to_bottom(self, message, duration=1, **_kwargs):
        current_x, current_y = self.position
        self.from_to(message, duration, current_x, current_y, current_x, self.height)
