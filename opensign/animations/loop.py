# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Loop animations."""

import time

from . import Animation


class Loop(Animation):
    """Loop messages across the display."""

    def left(self, message, duration=1, count=1, **_kwargs):
        current_x, current_y = self.position
        distance = max(message.width, self.width)
        loop_image = self.create_loop_image(message.get_image(), distance, 0)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_x -= 1
                if current_x < -message.width:
                    current_x += distance
                self.draw_message_image(message, loop_image, current_x, current_y)
                self.wait(start_time, duration / distance / count)

    def right(self, message, duration=1, count=1, **_kwargs):
        current_x, current_y = self.position
        distance = max(message.width, self.width)
        loop_image = self.create_loop_image(message.get_image(), distance, 0)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_x += 1
                if current_x > 0:
                    current_x -= distance
                self.draw_message_image(message, loop_image, current_x, current_y)
                self.wait(start_time, duration / distance / count)

    def up(self, message, duration=0.5, count=1, **_kwargs):
        current_x, current_y = self.position
        distance = max(message.height, self.height)
        loop_image = self.create_loop_image(message.get_image(), 0, distance)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_y -= 1
                if current_y < -message.height:
                    current_y += distance
                self.draw_message_image(message, loop_image, current_x, current_y)
                self.wait(start_time, duration / distance / count)

    def down(self, message, duration=0.5, count=1, **_kwargs):
        current_x, current_y = self.position
        distance = max(message.height, self.height)
        loop_image = self.create_loop_image(message.get_image(), 0, distance)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_y += 1
                if current_y > 0:
                    current_y -= distance
                self.draw_message_image(message, loop_image, current_x, current_y)
                self.wait(start_time, duration / distance / count)
