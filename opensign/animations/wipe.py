# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Wipe animations."""

import time

from . import Animation


class Wipe(Animation):
    """Reveal or conceal messages by cropping from a direction."""

    def _draw_crop(self, message, box, x, y):
        image = message.get_image().crop(box=box)
        self.draw_message_image(message, image, x, y)

    def in_from_left(self, message, duration=1, **_kwargs):
        x, y = self.centered_position(message)
        for width in range(1, message.width + 1):
            start_time = time.monotonic()
            self._draw_crop(message, (0, 0, width, message.height), x, y)
            self.wait_for_steps(start_time, duration, message.width)
        self.position = (x, y)

    def in_from_right(self, message, duration=1, **_kwargs):
        x, y = self.centered_position(message)
        for width in range(1, message.width + 1):
            start_time = time.monotonic()
            left = message.width - width
            self._draw_crop(
                message,
                (left, 0, message.width, message.height),
                x + left,
                y,
            )
            self.wait_for_steps(start_time, duration, message.width)
        self.position = (x, y)

    def in_from_top(self, message, duration=1, **_kwargs):
        x, y = self.centered_position(message)
        for height in range(1, message.height + 1):
            start_time = time.monotonic()
            self._draw_crop(message, (0, 0, message.width, height), x, y)
            self.wait_for_steps(start_time, duration, message.height)
        self.position = (x, y)

    def in_from_bottom(self, message, duration=1, **_kwargs):
        x, y = self.centered_position(message)
        for height in range(1, message.height + 1):
            start_time = time.monotonic()
            top = message.height - height
            self._draw_crop(
                message,
                (0, top, message.width, message.height),
                x,
                y + top,
            )
            self.wait_for_steps(start_time, duration, message.height)
        self.position = (x, y)

    def out_to_left(self, message, duration=1, **_kwargs):
        x, y = self.position
        for width in range(message.width, 0, -1):
            start_time = time.monotonic()
            self._draw_crop(message, (0, 0, width, message.height), x, y)
            self.wait_for_steps(start_time, duration, message.width)
        self.draw(message, x, y, opacity=0)

    def out_to_right(self, message, duration=1, **_kwargs):
        x, y = self.position
        for width in range(message.width, 0, -1):
            start_time = time.monotonic()
            left = message.width - width
            self._draw_crop(
                message,
                (left, 0, message.width, message.height),
                x + left,
                y,
            )
            self.wait_for_steps(start_time, duration, message.width)
        self.draw(message, x, y, opacity=0)

    def out_to_top(self, message, duration=1, **_kwargs):
        x, y = self.position
        for height in range(message.height, 0, -1):
            start_time = time.monotonic()
            self._draw_crop(message, (0, 0, message.width, height), x, y)
            self.wait_for_steps(start_time, duration, message.height)
        self.draw(message, x, y, opacity=0)

    def out_to_bottom(self, message, duration=1, **_kwargs):
        x, y = self.position
        for height in range(message.height, 0, -1):
            start_time = time.monotonic()
            top = message.height - height
            self._draw_crop(
                message,
                (0, top, message.width, message.height),
                x,
                y + top,
            )
            self.wait_for_steps(start_time, duration, message.height)
        self.draw(message, x, y, opacity=0)
