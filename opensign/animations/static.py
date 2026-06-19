# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Static and opacity animations."""

import time

from . import Animation


class Static(Animation):
    """Animations that do not move the message."""

    def show(self, message, **_kwargs):
        x, y = self.position
        self.draw(message, x, y)

    def hide(self, message, **_kwargs):
        x, y = self.position
        self.draw(message, x, y, opacity=0)

    def blink(self, message, count=3, duration=1, **_kwargs):
        delay = duration / count / 2
        for _ in range(count):
            start_time = time.monotonic()
            self.hide(message)
            start_time = self.wait(start_time, delay)
            self.show(message)
            self.wait(start_time, delay)

    def flash(self, message, count=3, duration=1, **_kwargs):
        delay = duration / count / 2
        steps = max(1, 50 // count)
        from .fade import Fade

        fade = Fade(self._sign)
        for _ in range(count):
            fade.out(message, duration=delay, steps=steps)
            fade.in_(message, duration=delay, steps=steps)
