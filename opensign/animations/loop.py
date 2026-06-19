# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Loop animations."""

import time


class Loop:
    """Loop messages across the display."""

    @staticmethod
    def left(sign, message, duration=1, count=1, **_kwargs):
        current_x, current_y = sign._position
        distance = max(message.width, sign.width)
        loop_image = sign._create_loop_image(message.get_image(), distance, 0)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_x -= 1
                if current_x < -message.width:
                    current_x += distance
                sign._draw_image(
                    loop_image,
                    current_x,
                    current_y,
                    message.opacity,
                    message.shadow_intensity,
                    message.shadow_offset,
                )
                sign._wait(start_time, duration / distance / count)

    @staticmethod
    def right(sign, message, duration=1, count=1, **_kwargs):
        current_x, current_y = sign._position
        distance = max(message.width, sign.width)
        loop_image = sign._create_loop_image(message.get_image(), distance, 0)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_x += 1
                if current_x > 0:
                    current_x -= distance
                sign._draw_image(
                    loop_image,
                    current_x,
                    current_y,
                    message.opacity,
                    message.shadow_intensity,
                    message.shadow_offset,
                )
                sign._wait(start_time, duration / distance / count)

    @staticmethod
    def up(sign, message, duration=0.5, count=1, **_kwargs):
        current_x, current_y = sign._position
        distance = max(message.height, sign.height)
        loop_image = sign._create_loop_image(message.get_image(), 0, distance)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_y -= 1
                if current_y < -message.height:
                    current_y += distance
                sign._draw_image(
                    loop_image,
                    current_x,
                    current_y,
                    message.opacity,
                    message.shadow_intensity,
                    message.shadow_offset,
                )
                sign._wait(start_time, duration / distance / count)

    @staticmethod
    def down(sign, message, duration=0.5, count=1, **_kwargs):
        current_x, current_y = sign._position
        distance = max(message.height, sign.height)
        loop_image = sign._create_loop_image(message.get_image(), 0, distance)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_y += 1
                if current_y > 0:
                    current_y -= distance
                sign._draw_image(
                    loop_image,
                    current_x,
                    current_y,
                    message.opacity,
                    message.shadow_intensity,
                    message.shadow_offset,
                )
                sign._wait(start_time, duration / distance / count)
