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

A Library to facilitate easy RGB Matrix Sign Animations.

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
from PIL import Image, ImageDraw, ImageFont, ImageChops
from rgbmatrix import RGBMatrix, RGBMatrixOptions

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/makermelissa/OpenSign.git"

# pylint: disable=too-many-public-methods
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
        pixel_mapper=""
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

    # pylint: disable=no-self-use
    def sleep(self, value):
        """Sleep for the specified time. Mainly a shortcut, so
        you don't need to import time.

        :param float value: The time to sleep in seconds.
        """
        time.sleep(value)

    # pylint: enable=no-self-use

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
        """Attach a copy of an image by a certain offset so it can be looped.
        """
        loop_image = Image.new(
            "RGBA", (image.width + x_offset, image.height + y_offset), (0, 0, 0, 0)
        )
        loop_image.alpha_composite(image, dest=(0, 0))
        loop_image.alpha_composite(image, dest=(x_offset, y_offset))
        return loop_image

    # pylint: enable=no-self-use

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

        :param file: The file location of the image to display.
        """
        if os.path.exists(file):
            self._background = file
        else:
            raise ValueError("Specified background file {} was not found".format(file))

    # pylint: disable=no-self-use
    def _wait(self, start_time, duration):
        """Uses time.monotonic() to wait from the start time for a specified duration"""
        while time.monotonic() < (start_time + duration):
            pass
        return time.monotonic()

    # pylint: enable=no-self-use

    def scroll_in_from_left(self, canvas, duration=1, x=0):
        """Scroll a canvas in from the left side of the display over a certain period of
        time. The final position is centered."""
        current_x = 0 - canvas.width
        current_y = int(self._matrix.height / 2 - canvas.height / 2)
        self._draw(canvas, current_x, current_y)
        distance = int(self._matrix.width / 2 - canvas.width / 2) - current_x + x
        for i in range(distance):
            start_time = time.monotonic()
            current_x = i - canvas.width + 1
            self._draw(canvas, current_x, current_y)
            self._wait(start_time, duration / distance)

    def scroll_in_from_right(self, canvas, duration=1, x=0):
        """Scroll a canvas in from the right side of the display over a certain period of
        time. The final position is centered."""
        current_x = self._matrix.width
        current_y = int(self._matrix.height / 2 - canvas.height / 2)
        self._draw(canvas, current_x, current_y)
        distance = current_x - int(self._matrix.width / 2 - canvas.width / 2) + x
        for i in range(distance):
            start_time = time.monotonic()
            current_x = self._matrix.width - i - 1
            self._draw(canvas, current_x, current_y)
            self._wait(start_time, duration / distance)

    def scroll_in_from_top(self, canvas, duration=1, y=0):
        """Scroll a canvas in from the top side of the display over a certain period of
        time. The final position is centered."""
        current_x = int(self._matrix.width / 2 - canvas.width / 2)
        current_y = 0 - canvas.height
        self._draw(canvas, current_x, current_y)
        distance = int(self._matrix.height / 2 - canvas.height / 2) - current_y + y
        for i in range(distance):
            start_time = time.monotonic()
            current_y = i - canvas.height + 1
            self._draw(canvas, current_x, current_y)
            self._wait(start_time, duration / distance)

    def scroll_in_from_bottom(self, canvas, duration=1, y=0):
        """Scroll a canvas in from the bottom side of the display over a certain period of
        time. The final position is centered."""
        current_x = int(self._matrix.width / 2 - canvas.width / 2)
        current_y = self._matrix.height
        self._draw(canvas, current_x, current_y)
        distance = current_y - int(self._matrix.height / 2 - canvas.height / 2) + y
        for i in range(distance):
            start_time = time.monotonic()
            current_y = self._matrix.height - i - 1
            self._draw(canvas, current_x, current_y)
            self._wait(start_time, duration / distance)

    def scroll_out_to_left(self, canvas, duration=1):
        """Scroll a canvas off the display from its current position towards the left
        over a certain period of time."""
        current_x, current_y = self._position
        distance = current_x + canvas.width
        while current_x + canvas.width > 0:
            start_time = time.monotonic()
            current_x = current_x - 1
            self._draw(canvas, current_x, current_y)
            self._wait(start_time, duration / distance)

    def scroll_out_to_right(self, canvas, duration=1):
        """Scroll a canvas off the display from its current position towards the right
        over a certain period of time."""
        current_x, current_y = self._position
        distance = self._matrix.width - current_x
        while current_x < self._matrix.width:
            start_time = time.monotonic()
            current_x = current_x + 1
            self._draw(canvas, current_x, current_y)
            self._wait(start_time, duration / distance)

    def scroll_out_to_top(self, canvas, duration=1):
        """Scroll a canvas off the display from its current position towards the top
        over a certain period of time."""
        current_x, current_y = self._position
        distance = current_y + canvas.height
        while current_y + canvas.height > 0:
            start_time = time.monotonic()
            current_y = current_y - 1
            self._draw(canvas, current_x, current_y)
            self._wait(start_time, duration / distance)

    def scroll_out_to_bottom(self, canvas, duration=1):
        """Scroll a canvas off the display from its current position towards the bottom
        over a certain period of time."""
        current_x, current_y = self._position
        distance = self._matrix.height - current_y
        while current_y < self._matrix.height:
            start_time = time.monotonic()
            current_y = current_y + 1
            self._draw(canvas, current_x, current_y)
            self._wait(start_time, duration / distance)

    def set_position(self, canvas, x=0, y=0):
        """Instantly move the canvas to a specific location."""
        self._draw(canvas, x, y)

    def show(self, canvas):
        """Show the canvas at its current position."""
        x, y = self._position
        self._draw(canvas, x, y)

    def hide(self, canvas):
        """Hide the canvas at its current position."""
        x, y = self._position
        self._draw(canvas, x, y, opacity=0)

    def blink(self, canvas, count=1, duration=1):
        """Blink the foreground on and off a centain number of
        times over a certain period of time."""
        delay = duration / count / 2
        for _ in range(count):
            start_time = time.monotonic()
            self.hide(canvas)
            start_time = self._wait(start_time, delay)
            self.show(canvas)
            self._wait(start_time, delay)

    def flash(self, canvas, count=1, duration=1):
        """Fade the foreground in and out a centain number of
        times over a certain period of time."""
        delay = duration / count / 2
        steps = 50 // count
        for _ in range(count):
            self.fade_out(canvas, duration=delay, steps=steps)
            self.fade_in(canvas, duration=delay, steps=steps)

    def fade_in(self, canvas, duration=1, steps=50):
        """Fade the foreground in over a certain period of time
        by a certain number of steps."""
        current_x = int(self._matrix.width / 2 - canvas.width / 2)
        current_y = int(self._matrix.height / 2 - canvas.height / 2)
        delay = duration / (steps + 1)
        for opacity in range(steps + 1):
            start_time = time.monotonic()
            self._draw(canvas, current_x, current_y, opacity=opacity / steps)
            self._wait(start_time, delay)

    def fade_out(self, canvas, duration=1, steps=50):
        """Fade the foreground out over a certain period of time
        by a certain number of steps."""
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
        over a certain period of time."""
        current_x = int(self._matrix.width / 2 - canvas.width / 2)
        current_y = int(self._matrix.height / 2 - canvas.height / 2)
        image = canvas.get_image()
        left_image = image.crop(box=(0, 0, image.width // 2 + 1, image.height))
        right_image = image.crop(
            box=(image.width // 2 + 1, 0, image.width, image.height)
        )
        distance = self._matrix.width // 2
        for i in range(distance):
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
        over a certain period of time."""
        current_x = int(self._matrix.width / 2 - canvas.width / 2)
        current_y = int(self._matrix.height / 2 - canvas.height / 2)
        image = canvas.get_image()
        top_image = image.crop(box=(0, 0, image.width, image.height // 2 + 1))
        bottom_image = image.crop(
            box=(0, image.height // 2 + 1, image.width, image.height)
        )
        distance = self._matrix.height // 2
        for i in range(distance):
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
        over a certain period of time."""
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
        over a certain period of time."""
        current_x, current_y = self._position
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
        starting position."""
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
        starting position."""
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
        starting position."""
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
        starting position."""
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


# pylint: enable=too-many-public-methods


class OpenSignCanvas:
    """The Canvas is an empty image that you add text and graphics to. It will automatically
    expand as you add content. You can then display the canvas on the sign and use the animation
    functions to convey it."""

    def __init__(self):
        self._fonts = {}
        self._current_font = None
        self._current_color = (255, 0, 0, 255)
        self._image = Image.new("RGBA", (0, 0), (0, 0, 0, 0))
        self._draw = ImageDraw.Draw(self._image)
        self._cursor = [0, 0]
        self._stroke_width = 0
        self._stroke_color = None
        self._shadow_intensity = 0
        self._shadow_offset = 0
        self._opacity = 1.0

    def add_font(self, name, file, size=None, use=False):
        """Add a font to the font pool. If there is no current font set,
        then the new font will automatically become the current font"""
        if size is not None:
            self._fonts[name] = ImageFont.truetype(file, size)
        else:
            self._fonts[name] = ImageFont.load(file)
        if use or self._current_font is None:
            self._current_font = self._fonts[name]

    def set_font(self, fontname):
        """Set the current font"""
        if self._fonts.get(fontname) is None:
            raise ValueError("Font name not found.")
        self._current_font = self._fonts[fontname]

    def set_stroke(self, width, color=None):
        """Set the text stroke width and color"""
        self._stroke_width = width
        if color is not None:
            self._stroke_color = self._convert_color(color)
        else:
            self._stroke_color = None

    # pylint: disable=no-self-use
    def _convert_color(self, color):
        if isinstance(color, (tuple, list)):
            if len(color) == 3:
                return (color[0], color[1], color[2], 255)
            if len(color) == 4:
                return tuple(color)
        if isinstance(color, int):
            return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF, 255)
        raise ValueError("Color should be an integer or 3 or 4 value tuple or list.")

    # pylint: enable=no-self-use

    def _enlarge_canvas(self, width, height):
        if self._cursor[0] + width >= self._image.width:
            new_width = self._cursor[0] + width
        else:
            new_width = self._image.width
        if self._cursor[1] + height >= self._image.height:
            new_height = self._cursor[1] + height
        else:
            new_height = self._image.height
        new_image = Image.new("RGBA", (new_width, new_height))
        new_image.alpha_composite(self._image)
        self._image = new_image
        self._draw = ImageDraw.Draw(self._image)

    def set_color(self, color):
        """Set the current text color"""
        self._current_color = self._convert_color(color)

    def set_shadow(self, intensity=0.5, offset=1):
        """Set the canvas to display a shadow of the content. To turn shadow off, set
        the intensity to 0. The shadow is global for the entire canvas."""
        if intensity < 0:
            intensity = 0
        if intensity > 1:
            intensity = 1
        if offset < 0:
            offset = 0
        self._shadow_intensity = intensity
        self._shadow_offset = offset

    # pylint: disable=too-many-arguments
    def add_text(
        self,
        text,
        color=None,
        font=None,
        stroke_width=None,
        stroke_color=None,
        x_offset=0,
        y_offset=0,
    ):
        """Add text to the canvas"""
        if font is not None:
            font = self._fonts[font]
        else:
            font = self._current_font
        if font is None:
            font = ImageFont.load_default()
        x, y = self._cursor

        if color is None:
            color = self._current_color
        else:
            color = self._convert_color(color)

        if stroke_color is None:
            stroke_color = self._stroke_color
        else:
            stroke_color = self._convert_color(stroke_color)

        if stroke_width is None:
            stroke_width = self._stroke_width

        (text_width, text_height) = font.getsize(text, stroke_width=self._stroke_width)
        self._enlarge_canvas(text_width, text_height)
        # Draw the text
        self._draw.text(
            (x + x_offset, y + y_offset),
            text,
            font=font,
            fill=color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color,
        )
        # Get size and add to cursor
        self._cursor[0] += text_width

    # pylint: enable=too-many-arguments

    def add_image(self, file):
        """Add an image to the canvas."""
        x, y = self._cursor
        new_image = Image.open(file).convert("RGBA")
        self._enlarge_canvas(new_image.width, new_image.height)
        self._image.alpha_composite(new_image, dest=(x, y))
        self._cursor[0] += new_image.width

    def clear(self):
        """Clear the canvas content, but retain all of the style settings"""
        self._image = Image.new("RGBA", (0, 0), (0, 0, 0, 0))
        self._cursor = [0, 0]

    def get_image(self):
        """Get the canvas content as an image"""
        return self._image

    @property
    def width(self):
        """Get the current canvas width in pixels"""
        return self._image.width

    @property
    def height(self):
        """Get the current canvas height in pixels"""
        return self._image.height

    @property
    def shadow_offset(self):
        """Get or set the current shadow offset in pixels"""
        return self._shadow_offset

    @shadow_offset.setter
    def shadow_offset(self, value):
        if not isinstance(value, int):
            raise TypeError("Shadow offset must be an integer")
        if value < 0:
            value = 0
        self._shadow_offset = value

    @property
    def shadow_intensity(self):
        """Get or set the current shadow intensity where 0 is
        no shadow and 1 is a fully opaque shadow."""
        return self._shadow_intensity

    @shadow_intensity.setter
    def shadow_intensity(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Shadow intensity must be an integer or float")
        value = max(0, min(1.0, value))
        self._shadow_intensity = value

    @property
    def opacity(self):
        """Get or set the maximum opacity of the canvas where 0 is
        no transparent and 1 is opaque."""
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Opacity must be an integer or float")
        value = max(0, min(1.0, value))
        self._opacity = value

    @property
    def cursor(self):
        """Get or set the current cursor position in pixels with the top left
        being (0, 0)."""
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        if isinstance(value, (tuple, list)) and len(value) >= 2:
            self._cursor = [value[0], value[1]]
        else:
            raise TypeError("Value must be a tuple or list")
