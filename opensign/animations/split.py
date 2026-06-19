# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Split and join animations."""

import time

from PIL import Image


class Split:
    """Split a message apart or bring split halves together."""

    @staticmethod
    def join_in_horizontally(sign, message, duration=0.5, **_kwargs):
        current_x, current_y = sign._get_centered_position(message)
        image = message.get_image()
        left_image = image.crop(box=(0, 0, image.width // 2 + 1, image.height))
        right_image = image.crop(box=(image.width // 2 + 1, 0, image.width, image.height))
        distance = sign.width // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new("RGBA", (sign.width + image.width, image.height), (0, 0, 0, 0))
            effect_image.alpha_composite(left_image, dest=(i, 0))
            effect_image.alpha_composite(
                right_image, dest=(sign.width + image.width // 2 - i + 1, 0)
            )
            sign._draw_image(
                effect_image,
                current_x - sign.width // 2,
                current_y,
                message.opacity,
                message.shadow_intensity,
                message.shadow_offset,
            )
            sign._wait(start_time, duration / distance)
        sign._position = (current_x, current_y)

    @staticmethod
    def join_in_vertically(sign, message, duration=0.5, **_kwargs):
        current_x, current_y = sign._get_centered_position(message)
        image = message.get_image()
        top_image = image.crop(box=(0, 0, image.width, image.height // 2 + 1))
        bottom_image = image.crop(box=(0, image.height // 2 + 1, image.width, image.height))
        distance = sign.height // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new(
                "RGBA", (image.width, sign.height + image.height), (0, 0, 0, 0)
            )
            effect_image.alpha_composite(top_image, dest=(0, i))
            effect_image.alpha_composite(
                bottom_image, dest=(0, sign.height + image.height // 2 - i + 1)
            )
            sign._draw_image(
                effect_image,
                current_x,
                current_y - sign.height // 2,
                message.opacity,
                message.shadow_intensity,
                message.shadow_offset,
            )
            sign._wait(start_time, duration / distance)
        sign._position = (current_x, current_y)

    @staticmethod
    def split_out_horizontally(sign, message, duration=0.5, **_kwargs):
        current_x, current_y = sign._position
        image = message.get_image()
        left_image = image.crop(box=(0, 0, image.width // 2 + 1, image.height))
        right_image = image.crop(box=(image.width // 2 + 1, 0, image.width, image.height))
        distance = sign.width // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new("RGBA", (sign.width + image.width, image.height), (0, 0, 0, 0))
            effect_image.alpha_composite(left_image, dest=(distance - i, 0))
            effect_image.alpha_composite(right_image, dest=(distance + image.width // 2 + i + 1, 0))
            sign._draw_image(
                effect_image,
                current_x - sign.width // 2,
                current_y,
                message.opacity,
                message.shadow_intensity,
                message.shadow_offset,
            )
            sign._wait(start_time, duration / distance)
        sign._position = (current_x - sign.width // 2, current_y)

    @staticmethod
    def split_out_vertically(sign, message, duration=0.5, **_kwargs):
        current_x, current_y = sign._position
        image = message.get_image()
        top_image = image.crop(box=(0, 0, image.width, image.height // 2))
        bottom_image = image.crop(box=(0, image.height // 2, image.width, image.height))
        distance = sign.height // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new(
                "RGBA", (image.width, sign.height + image.height), (0, 0, 0, 0)
            )
            effect_image.alpha_composite(top_image, dest=(0, distance - i))
            effect_image.alpha_composite(
                bottom_image, dest=(0, distance + image.height // 2 + i + 1)
            )
            sign._draw_image(
                effect_image,
                current_x,
                current_y - sign.height // 2,
                message.opacity,
                message.shadow_intensity,
                message.shadow_offset,
            )
            sign._wait(start_time, duration / distance)
        sign._position = (current_x, current_y - sign.height // 2)
