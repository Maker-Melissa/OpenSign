# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Split and join animations."""

import time

from PIL import Image

from . import Animation


class Split(Animation):
    """Split a message apart or bring split halves together."""

    def join_in_horizontally(self, message, duration=0.5, **_kwargs):
        current_x, current_y = self.centered_position(message)
        image = message.get_image()
        left_image = image.crop(box=(0, 0, image.width // 2 + 1, image.height))
        right_image = image.crop(box=(image.width // 2 + 1, 0, image.width, image.height))
        distance = self.width // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new("RGBA", (self.width + image.width, image.height), (0, 0, 0, 0))
            effect_image.alpha_composite(left_image, dest=(i, 0))
            effect_image.alpha_composite(
                right_image, dest=(self.width + image.width // 2 - i + 1, 0)
            )
            self.draw_message_image(
                message,
                effect_image,
                current_x - self.width // 2,
                current_y,
            )
            self.wait(start_time, duration / distance)
        self.position = (current_x, current_y)

    def join_in_vertically(self, message, duration=0.5, **_kwargs):
        current_x, current_y = self.centered_position(message)
        image = message.get_image()
        top_image = image.crop(box=(0, 0, image.width, image.height // 2 + 1))
        bottom_image = image.crop(box=(0, image.height // 2 + 1, image.width, image.height))
        distance = self.height // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new(
                "RGBA", (image.width, self.height + image.height), (0, 0, 0, 0)
            )
            effect_image.alpha_composite(top_image, dest=(0, i))
            effect_image.alpha_composite(
                bottom_image, dest=(0, self.height + image.height // 2 - i + 1)
            )
            self.draw_message_image(
                message,
                effect_image,
                current_x,
                current_y - self.height // 2,
            )
            self.wait(start_time, duration / distance)
        self.position = (current_x, current_y)

    def split_out_horizontally(self, message, duration=0.5, **_kwargs):
        current_x, current_y = self.position
        image = message.get_image()
        left_image = image.crop(box=(0, 0, image.width // 2 + 1, image.height))
        right_image = image.crop(box=(image.width // 2 + 1, 0, image.width, image.height))
        distance = self.width // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new("RGBA", (self.width + image.width, image.height), (0, 0, 0, 0))
            effect_image.alpha_composite(left_image, dest=(distance - i, 0))
            effect_image.alpha_composite(right_image, dest=(distance + image.width // 2 + i + 1, 0))
            self.draw_message_image(
                message,
                effect_image,
                current_x - self.width // 2,
                current_y,
            )
            self.wait(start_time, duration / distance)
        self.position = (current_x - self.width // 2, current_y)

    def split_out_vertically(self, message, duration=0.5, **_kwargs):
        current_x, current_y = self.position
        image = message.get_image()
        top_image = image.crop(box=(0, 0, image.width, image.height // 2))
        bottom_image = image.crop(box=(0, image.height // 2, image.width, image.height))
        distance = self.height // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new(
                "RGBA", (image.width, self.height + image.height), (0, 0, 0, 0)
            )
            effect_image.alpha_composite(top_image, dest=(0, distance - i))
            effect_image.alpha_composite(
                bottom_image, dest=(0, distance + image.height // 2 + i + 1)
            )
            self.draw_message_image(
                message,
                effect_image,
                current_x,
                current_y - self.height // 2,
            )
            self.wait(start_time, duration / distance)
        self.position = (current_x, current_y - self.height // 2)
