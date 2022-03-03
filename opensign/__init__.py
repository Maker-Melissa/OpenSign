# The MIT License (MIT)
#
# Copyright (c) 2020 Melissa LeBlanc-Williams
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`opensign`
================================================================================

A library to facilitate easy RGB Matrix Sign Animations.

* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Software and Dependencies:**

* Henner Zeller RGB Matrix Library:
  https://github.com/hzeller/rpi-rgb-led-matrix

* Python Imaging Library (Pillow)

"""

import time
import os
from PIL import Image, ImageChops
from rgbmatrix import RGBMatrix, RGBMatrixOptions

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/makermelissa/OpenSign.git"

# pylint: disable=too-many-public-methods, too-many-lines
class OpenSign:
    """Main class that controls the sign and graphics effects."""

    # pylint: disable=too-many-locals
    def __init__(
        self,
        *,
        rows=16,
        columns=32,
        chain=1,
        brightness=100,
        gpio_mapping="adafruit-hat",
        parallel=1,
        pwm_bits=11,
        panel_type="",
        rgb_sequence="rgb",
        show_refresh=False,
        slowdown_gpio=None,
        no_hardware_pulse=False,
        pwm_lsb_nanoseconds=130,
        row_addr_type=0,
        multiplexing=0,
        pixel_mapper="",
    ):
        options = RGBMatrixOptions()

        options.hardware_mapping = gpio_mapping
        options.rows = rows
        options.cols = columns
        options.chain_length = chain
        options.parallel = parallel
        options.pwm_bits = pwm_bits
        options.brightness = brightness
        options.panel_type = panel_type
        options.led_rgb_sequence = rgb_sequence
        options.pwm_lsb_nanoseconds = pwm_lsb_nanoseconds
        options.row_address_type = row_addr_type
        options.multiplexing = multiplexing
        options.pixel_mapper_config = pixel_mapper

        if show_refresh:
            options.show_refresh_rate = 1
        if slowdown_gpio is not None:
            options.gpio_slowdown = slowdown_gpio
        if no_hardware_pulse:
            options.disable_hardware_pulsing = True

        self._matrix = RGBMatrix(options=options)
        self._buffer = self._matrix.CreateFrameCanvas()
        self._background = (0, 0, 0)
        self._position = (0, 0)
        # pylint: enable=too-many-locals

    def _update(self):
        self._buffer = self._matrix.SwapOnVSync(self._buffer)

    @property
    def width(self):
        """Returns the width in pixels"""
        return self._matrix.width

    @property
    def height(self):
        """Returns the height in pixels"""
        return self._matrix.height

    # pylint: disable=too-many-arguments, too-many-locals
    def _add_background(
        self, image, x, y, opacity=1.0, shadow_intensity=0, shadow_offset=1
    ):
        """Combine the foreground and background images and apply any shadow and opacity effects."""
        if isinstance(self._background, tuple):
            combined_image = Image.new(
                "RGBA", (self._matrix.width, self._matrix.height), self._background
            )
        else:
            combined_image = Image.new(
                "RGBA", (self._matrix.width, self._matrix.height)
            )
            combined_image.alpha_composite(Image.open(self._background).convert("RGBA"))

        source_x = source_y = 0
        if x < 0:
            source_x = 0 - x
            x = 0
        if y < 0:
            source_y = 0 - y
            y = 0

        # Keep opacity in the range of 0-1.0
        opacity = max(0, min(1.0, opacity))

        foreground_image = Image.new(
            "RGBA", (self._matrix.width, self._matrix.height), (0, 0, 0, 0)
        )
        if source_x < image.width and source_y < image.height:
            foreground_image.alpha_composite(
                image, dest=(x, y), source=(source_x, source_y)
            )

        alpha = foreground_image.split()[-1]

        if opacity == 1:
            opacity_mask = ImageChops.invert(alpha)
        elif opacity == 0:
            opacity_mask = Image.new(
                "L", (self._matrix.width, self._matrix.height), 255
            )
        else:
            opacity_filter = Image.new(
                "L", (self._matrix.width, self._matrix.height), round(opacity * 255)
            )
            opacity_mask = ImageChops.darker(alpha, opacity_filter)
            opacity_mask = ImageChops.invert(opacity_mask)

        if shadow_intensity:
            shadow_image = Image.new("RGB", (self._matrix.width, self._matrix.height))
            shadow_filter = Image.new(
                "L",
                (self._matrix.width, self._matrix.height),
                round(shadow_intensity * opacity * 255),
            )
            shadow_mask = ImageChops.darker(alpha, shadow_filter)
            shadow_shifted = Image.new(
                "L", (self._matrix.width, self._matrix.height), 0
            )
            shadow_shifted.paste(shadow_mask, box=(shadow_offset, shadow_offset))
            shadow_shifted = ImageChops.invert(shadow_shifted)
            combined_image = Image.composite(
                combined_image, shadow_image, shadow_shifted
            )

        return Image.composite(combined_image, foreground_image, opacity_mask).convert(
            "RGB"
        )

    # pylint: enable=too-many-arguments, too-many-locals

    def _draw(self, canvas, x, y, opacity=1.0):
        """Draws a canvas to the buffer taking its current settings into account.
        It also sets the current position and performs a swap.
        """
        self._position = (x, y)
        self._buffer.SetImage(
            self._add_background(
                canvas.get_image(),
                x,
                y,
                opacity=(opacity * canvas.opacity),
                shadow_intensity=canvas.shadow_intensity,
                shadow_offset=canvas.shadow_offset,
            ),
            0,
            0,
        )
        self._update()

    # pylint: disable=too-many-arguments
    def _draw_image(self, image, x, y, opacity, shadow_intensity, shadow_offset):
        """Draws an image to the buffer. Settings are passed as additional parameters.
        It also sets the current position and performs a swap.
        """
        self._position = (x, y)
        self._buffer.SetImage(
            self._add_background(
                image,
                x,
                y,
                opacity=opacity,
                shadow_intensity=shadow_intensity,
                shadow_offset=shadow_offset,
            ),
            0,
            0,
        )
        self._update()

    # pylint: enable=too-many-arguments

    # pylint: disable=no-self-use
    def _create_loop_image(self, image, x_offset, y_offset):
        """Attach a copy of an image by a certain offset so it can be looped."""
        loop_image = Image.new(
            "RGBA", (image.width + x_offset, image.height + y_offset), (0, 0, 0, 0)
        )
        loop_image.alpha_composite(image, dest=(0, 0))
        loop_image.alpha_composite(image, dest=(x_offset, y_offset))
        return loop_image

    # pylint: enable=no-self-use

    def _get_centered_position(self, canvas):
        return int(self._matrix.width / 2 - canvas.width / 2), int(
            self._matrix.height / 2 - canvas.height / 2
        )

    def set_background_color(self, color):
        """Sets the background to a solid color. The color should be a 3 or 4 value
        tuple or list or an hexidecimal value in the format of 0xRRGGBB.

        :param color: The time to sleep in seconds.
        :type color: tuple or list or int
        """
        if isinstance(color, (tuple, list)) and len(color) == 3:
            self._background = tuple(color)
        elif isinstance(color, int):
            self._background = ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)
        else:
            raise ValueError("Color should be an integer or 3 value tuple or list.")

    def set_background_image(self, file):
        """Sets the background to an image

        :param string file: The file location of the image to display.
        """
        if os.path.exists(file):
            self._background = file
        else:
            raise ValueError(f"Specified background file {file} was not found")

    @staticmethod
    def _wait(start_time, duration):
        """Uses time.monotonic() to wait from the start time for a specified duration"""
        while time.monotonic() < (start_time + duration):
            pass
        return time.monotonic()

    # pylint: disable=too-many-arguments
    def scroll_from_to(self, canvas, duration, start_x, start_y, end_x, end_y):
        """
        Scroll the canvas from one position to another over a certain period of
        time.

        :param canvas: The canvas to animate.
        :param float duration: The period of time to perform the animation over in seconds.
        :param int start_x: The Starting X Position
        :param int start_yx: The Starting Y Position
        :param int end_x: The Ending X Position
        :param int end_y: The Ending Y Position
        :type canvas: OpenSignCanvas
        """
        steps = max(abs(end_x - start_x), abs(end_y - start_y))
        if not steps:
            return
        increment_x = (end_x - start_x) / steps
        increment_y = (end_y - start_y) / steps
        for i in range(steps + 1):
            start_time = time.monotonic()
            current_x = start_x + round(i * increment_x)
            current_y = start_y + round(i * increment_y)
            self._draw(canvas, current_x, current_y)
            if i <= steps:
                self._wait(start_time, duration / steps)

    # pylint: enable=too-many-arguments

    def scroll_in_from_left(self, canvas, duration=1, x=0):
        """Scroll a canvas in from the left side of the display over a certain period of
        time. The final position is centered.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over in seconds. (default=1)
        :param int x: (optional) The amount of x-offset from the center position (default=0)
        :type canvas: OpenSignCanvas
        """
        center_x, center_y = self._get_centered_position(canvas)
        self.scroll_from_to(
            canvas, duration, 0 - canvas.width, center_y, center_x + x, center_y
        )

    def scroll_in_from_right(self, canvas, duration=1, x=0):
        """Scroll a canvas in from the right side of the display over a certain period of
        time. The final position is centered.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over in seconds. (default=1)
        :param int x: (optional) The amount of x-offset from the center position (default=0)
        :type canvas: OpenSignCanvas
        """
        center_x, center_y = self._get_centered_position(canvas)
        self.scroll_from_to(
            canvas, duration, self._matrix.width, center_y, center_x + x, center_y
        )

    def scroll_in_from_top(self, canvas, duration=1, y=0):
        """Scroll a canvas in from the top side of the display over a certain period of
        time. The final position is centered.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over in seconds. (default=1)
        :param int y: (optional) The amount of y-offset from the center position (default=0)
        :type canvas: OpenSignCanvas
        """
        center_x, center_y = self._get_centered_position(canvas)
        self.scroll_from_to(
            canvas, duration, center_x, 0 - canvas.height, center_x, center_y + y
        )

    def scroll_in_from_bottom(self, canvas, duration=1, y=0):
        """Scroll a canvas in from the bottom side of the display over a certain period of
        time. The final position is centered.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over in seconds. (default=1)
        :param int y: (optional) The amount of y-offset from the center position (default=0)
        :type canvas: OpenSignCanvas
        """
        center_x, center_y = self._get_centered_position(canvas)
        self.scroll_from_to(
            canvas, duration, center_x, self._matrix.height, center_x, center_y + y
        )

    def scroll_out_to_left(self, canvas, duration=1):
        """Scroll a canvas off the display from its current position towards the left
        over a certain period of time.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over in seconds. (default=1)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        self.scroll_from_to(
            canvas, duration, current_x, current_y, 0 - canvas.width, current_y
        )

    def scroll_out_to_right(self, canvas, duration=1):
        """Scroll a canvas off the display from its current position towards the right
        over a certain period of time.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over in seconds. (default=1)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        self.scroll_from_to(
            canvas, duration, current_x, current_y, self._matrix.width, current_y
        )

    def scroll_out_to_top(self, canvas, duration=1):
        """Scroll a canvas off the display from its current position towards the top
        over a certain period of time.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over in seconds. (default=1)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        self.scroll_from_to(
            canvas, duration, current_x, current_y, current_x, 0 - canvas.height
        )

    def scroll_out_to_bottom(self, canvas, duration=1):
        """Scroll a canvas off the display from its current position towards the bottom
        over a certain period of time.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over in seconds. (default=1)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        self.scroll_from_to(
            canvas, duration, current_x, current_y, current_x, self._matrix.height
        )

    def set_position(self, canvas, x=0, y=0):
        """Instantly move the canvas to a specific location. (0, 0) is the top-left corner.

        :param canvas: The canvas to move.
        :param int x: (optional) The x-position to move the canvas to. (default=0)
        :param int y: (optional) The y-position to move the canvas to. (default=0)
        :type canvas: OpenSignCanvas
        """
        self._draw(canvas, x, y)

    def show(self, canvas):
        """Show the canvas at its current position.

        :param canvas: The canvas to show.
        :type canvas: OpenSignCanvas
        """
        x, y = self._position
        self._draw(canvas, x, y)

    def hide(self, canvas):
        """Hide the canvas at its current position.

        :param canvas: The canvas to hide.
        :type canvas: OpenSignCanvas
        """
        x, y = self._position
        self._draw(canvas, x, y, opacity=0)

    def blink(self, canvas, count=3, duration=1):
        """Blink the foreground on and off a centain number of
        times over a certain period of time.

        :param canvas: The canvas to animate.
        :param float count: (optional) The number of times to blink. (default=3)
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=1)
        :type canvas: OpenSignCanvas
        """
        delay = duration / count / 2
        for _ in range(count):
            start_time = time.monotonic()
            self.hide(canvas)
            start_time = self._wait(start_time, delay)
            self.show(canvas)
            self._wait(start_time, delay)

    def flash(self, canvas, count=3, duration=1):
        """Fade the foreground in and out a centain number of
        times over a certain period of time.

        :param canvas: The canvas to animate.
        :param float count: (optional) The number of times to flash. (default=3)
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=1)
        :type canvas: OpenSignCanvas
        """
        delay = duration / count / 2
        steps = 50 // count
        for _ in range(count):
            self.fade_out(canvas, duration=delay, steps=steps)
            self.fade_in(canvas, duration=delay, steps=steps)

    def fade_in(self, canvas, duration=1, steps=50):
        """Fade the foreground in over a certain period of time
        by a certain number of steps. More steps is smoother, but too high
        of a number may slow down the animation too much.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=1)
        :param float steps: (optional) The number of steps to perform the animation. (default=50)
        :type canvas: OpenSignCanvas
        """
        current_x = int(self._matrix.width / 2 - canvas.width / 2)
        current_y = int(self._matrix.height / 2 - canvas.height / 2)
        delay = duration / (steps + 1)
        for opacity in range(steps + 1):
            start_time = time.monotonic()
            self._draw(canvas, current_x, current_y, opacity=opacity / steps)
            self._wait(start_time, delay)

    def fade_out(self, canvas, duration=1, steps=50):
        """Fade the foreground out over a certain period of time
        by a certain number of steps. More steps is smoother, but too high
        of a number may slow down the animation too much.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=1)
        :param float steps: (optional) The number of steps to perform the animation. (default=50)
        :type canvas: OpenSignCanvas
        """
        delay = duration / (steps + 1)
        for opacity in range(steps + 1):
            start_time = time.monotonic()
            self._draw(
                canvas,
                self._position[0],
                self._position[1],
                opacity=(steps - opacity) / steps,
            )
            self._wait(start_time, delay)

    def join_in_horizontally(self, canvas, duration=0.5):
        """Show the effect of a split canvas joining horizontally
        over a certain period of time.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=0.5)
        :type canvas: OpenSignCanvas
        """
        current_x = int(self._matrix.width / 2 - canvas.width / 2)
        current_y = int(self._matrix.height / 2 - canvas.height / 2)
        image = canvas.get_image()
        left_image = image.crop(box=(0, 0, image.width // 2 + 1, image.height))
        right_image = image.crop(
            box=(image.width // 2 + 1, 0, image.width, image.height)
        )
        distance = self._matrix.width // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new(
                "RGBA", (self._matrix.width + image.width, image.height), (0, 0, 0, 0)
            )
            effect_image.alpha_composite(left_image, dest=(i, 0))
            effect_image.alpha_composite(
                right_image, dest=(self._matrix.width + image.width // 2 - i + 1, 0)
            )
            self._draw_image(
                effect_image,
                current_x - self._matrix.width // 2,
                current_y,
                canvas.opacity,
                canvas.shadow_intensity,
                canvas.shadow_offset,
            )
            self._wait(start_time, duration / distance)
        self._position = (current_x, current_y)

    def join_in_vertically(self, canvas, duration=0.5):
        """Show the effect of a split canvas joining vertically
        over a certain period of time.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=0.5)
        :type canvas: OpenSignCanvas
        """
        current_x = int(self._matrix.width / 2 - canvas.width / 2)
        current_y = int(self._matrix.height / 2 - canvas.height / 2)
        image = canvas.get_image()
        top_image = image.crop(box=(0, 0, image.width, image.height // 2 + 1))
        bottom_image = image.crop(
            box=(0, image.height // 2 + 1, image.width, image.height)
        )
        distance = self._matrix.height // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new(
                "RGBA", (image.width, self._matrix.height + image.height), (0, 0, 0, 0)
            )
            effect_image.alpha_composite(top_image, dest=(0, i))
            effect_image.alpha_composite(
                bottom_image, dest=(0, self._matrix.height + image.height // 2 - i + 1)
            )
            self._draw_image(
                effect_image,
                current_x,
                current_y - self._matrix.height // 2,
                canvas.opacity,
                canvas.shadow_intensity,
                canvas.shadow_offset,
            )
            self._wait(start_time, duration / distance)
        self._position = (current_x, current_y)

    def split_out_horizontally(self, canvas, duration=0.5):
        """Show the effect of a canvas splitting horizontally
        over a certain period of time.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=0.5)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        image = canvas.get_image()
        left_image = image.crop(box=(0, 0, image.width // 2 + 1, image.height))
        right_image = image.crop(
            box=(image.width // 2 + 1, 0, image.width, image.height)
        )
        distance = self._matrix.width // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new(
                "RGBA", (self._matrix.width + image.width, image.height), (0, 0, 0, 0)
            )
            effect_image.alpha_composite(left_image, dest=(distance - i, 0))
            effect_image.alpha_composite(
                right_image, dest=(distance + image.width // 2 + i + 1, 0)
            )
            self._draw_image(
                effect_image,
                current_x - self._matrix.width // 2,
                current_y,
                canvas.opacity,
                canvas.shadow_intensity,
                canvas.shadow_offset,
            )
            self._wait(start_time, duration / distance)
        self._position = (current_x - self._matrix.width // 2, current_y)

    def split_out_vertically(self, canvas, duration=0.5):
        """Show the effect of a canvas splitting vertically
        over a certain period of time.

        :param canvas: The canvas to animate.
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=0.5)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        image = canvas.get_image()
        top_image = image.crop(box=(0, 0, image.width, image.height // 2))
        bottom_image = image.crop(box=(0, image.height // 2, image.width, image.height))
        distance = self._matrix.height // 2
        for i in range(distance + 1):
            start_time = time.monotonic()
            effect_image = Image.new(
                "RGBA", (image.width, self._matrix.height + image.height), (0, 0, 0, 0)
            )
            effect_image.alpha_composite(top_image, dest=(0, distance - i))
            effect_image.alpha_composite(
                bottom_image, dest=(0, distance + image.height // 2 + i + 1)
            )
            self._draw_image(
                effect_image,
                current_x,
                current_y - self._matrix.height // 2,
                canvas.opacity,
                canvas.shadow_intensity,
                canvas.shadow_offset,
            )
            self._wait(start_time, duration / distance)
        self._position = (current_x, current_y - self._matrix.height // 2)

    def loop_left(self, canvas, duration=1, count=1):
        """Loop a canvas towards the left side of the display over a certain period of time by a
        certain number of times. The canvas will re-enter from the right and end up back a the
        starting position.

        :param canvas: The canvas to animate.
        :param float count: (optional) The number of times to loop. (default=1)
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=1)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        distance = max(canvas.width, self._matrix.width)
        loop_image = self._create_loop_image(canvas.get_image(), distance, 0)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_x -= 1
                if current_x < 0 - canvas.width:
                    current_x += distance
                self._draw_image(
                    loop_image,
                    current_x,
                    current_y,
                    canvas.opacity,
                    canvas.shadow_intensity,
                    canvas.shadow_offset,
                )
                self._wait(start_time, duration / distance / count)

    def loop_right(self, canvas, duration=1, count=1):
        """Loop a canvas towards the right side of the display over a certain period of time by a
        certain number of times. The canvas will re-enter from the left and end up back a the
        starting position.

        :param canvas: The canvas to animate.
        :param float count: (optional) The number of times to loop. (default=1)
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=1)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        distance = max(canvas.width, self._matrix.width)
        loop_image = self._create_loop_image(canvas.get_image(), distance, 0)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_x += 1
                if current_x > 0:
                    current_x -= distance
                self._draw_image(
                    loop_image,
                    current_x,
                    current_y,
                    canvas.opacity,
                    canvas.shadow_intensity,
                    canvas.shadow_offset,
                )
                self._wait(start_time, duration / distance / count)

    def loop_up(self, canvas, duration=0.5, count=1):
        """Loop a canvas towards the top side of the display over a certain period of time by a
        certain number of times. The canvas will re-enter from the bottom and end up back a the
        starting position.

        :param canvas: The canvas to animate.
        :param float count: (optional) The number of times to loop. (default=1)
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=1)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        distance = max(canvas.height, self._matrix.height)
        loop_image = self._create_loop_image(canvas.get_image(), 0, distance)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_y -= 1
                if current_y < 0 - canvas.height:
                    current_y += distance
                self._draw_image(
                    loop_image,
                    current_x,
                    current_y,
                    canvas.opacity,
                    canvas.shadow_intensity,
                    canvas.shadow_offset,
                )
                self._wait(start_time, duration / distance / count)

    def loop_down(self, canvas, duration=0.5, count=1):
        """Loop a canvas towards the bottom side of the display over a certain period of time by a
        certain number of times. The canvas will re-enter from the top and end up back a the
        starting position.

        :param canvas: The canvas to animate.
        :param float count: (optional) The number of times to loop. (default=1)
        :param float duration: (optional) The period of time to perform the animation
                               over. (default=1)
        :type canvas: OpenSignCanvas
        """
        current_x, current_y = self._position
        distance = max(canvas.height, self._matrix.height)
        loop_image = self._create_loop_image(canvas.get_image(), 0, distance)
        for _ in range(count):
            for _ in range(distance):
                start_time = time.monotonic()
                current_y += 1
                if current_y > 0:
                    current_y -= distance
                self._draw_image(
                    loop_image,
                    current_x,
                    current_y,
                    canvas.opacity,
                    canvas.shadow_intensity,
                    canvas.shadow_offset,
                )
                self._wait(start_time, duration / distance / count)
