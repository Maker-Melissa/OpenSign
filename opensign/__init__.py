# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

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

import os
import time

from PIL import Image, ImageChops
from rgbmatrix import RGBMatrix, RGBMatrixOptions

from .animations import animate as dispatch_animation
from .colors import parse_color
from .fontpool import FontPool
from .message import Message

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/Maker-Melissa/PyOpenSign.git"


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

        # Eagerly register PIL image-format plugins (JPEG, PNG, etc.) before
        # RGBMatrix initializes. The matrix library drops root privileges to
        # `nobody`, after which the venv is unreadable and PIL can no longer
        # lazy-load its format plugins - causing later Image.open() calls to
        # raise UnidentifiedImageError.
        Image.init()

        self._matrix = RGBMatrix(options=options)
        self._buffer = self._matrix.CreateFrameCanvas()
        self._background = (0, 0, 0)
        self._position = (0, 0)
        self.fonts = FontPool()
        self._last_canvas = None
        # pylint: enable=too-many-locals

    def add_font(self, name, file, size=None):
        """Add a font to the shared font pool.

        Fonts registered here are available to any canvas created via this sign.

        :param string name: A unique name key for looking up this font later.
        :param string file: Path to the font file (TrueType or bitmap).
        :param int size: (optional) Font size for TrueType fonts. Omit for bitmap fonts.
        """
        return self.fonts.add_font(name, file, size)

    def _resolve_canvas(self, target, **kwargs):
        """Return a Message for a renderable target or text string."""
        if isinstance(target, Message):
            self._last_canvas = target
            return target

        if target is None:
            if self._last_canvas is None:
                raise ValueError("No message has been created yet.")
            return self._last_canvas

        if not isinstance(target, str):
            raise TypeError("Target must be a Message, string, or None.")

        font = kwargs.get("font")
        if isinstance(font, str):
            font = self.fonts.get(font)
            if font is None:
                raise ValueError("Font name not found.")

        message = Message(font=font, opacity=kwargs.get("opacity", 1.0))
        stroke_width = kwargs.get("stroke_width")
        if stroke_width is not None:
            message.set_stroke(stroke_width, kwargs.get("stroke_color"))

        if kwargs.get("shadow_intensity") is not None or kwargs.get("shadow_offset") is not None:
            message.set_shadow(
                intensity=kwargs.get("shadow_intensity", 0.5),
                offset=kwargs.get("shadow_offset", 1),
            )

        image_path = kwargs.get("image")
        if image_path is not None:
            message.add_image(image_path)
        message.add_text(target, color=kwargs.get("color", (255, 0, 0)))

        self._last_canvas = message
        return message

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
    def _add_background(self, image, x, y, opacity=1.0, shadow_intensity=0, shadow_offset=1):
        """Combine the foreground and background images and apply any shadow and opacity effects."""
        if isinstance(self._background, tuple):
            combined_image = Image.new(
                "RGBA", (self._matrix.width, self._matrix.height), self._background
            )
        else:
            combined_image = Image.new("RGBA", (self._matrix.width, self._matrix.height))
            combined_image.alpha_composite(self._background)

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
            foreground_image.alpha_composite(image, dest=(x, y), source=(source_x, source_y))

        alpha = foreground_image.split()[-1]

        if opacity == 1:
            opacity_mask = ImageChops.invert(alpha)
        elif opacity == 0:
            opacity_mask = Image.new("L", (self._matrix.width, self._matrix.height), 255)
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
            shadow_shifted = Image.new("L", (self._matrix.width, self._matrix.height), 0)
            shadow_shifted.paste(shadow_mask, box=(shadow_offset, shadow_offset))
            shadow_shifted = ImageChops.invert(shadow_shifted)
            combined_image = Image.composite(combined_image, shadow_image, shadow_shifted)

        return Image.composite(combined_image, foreground_image, opacity_mask).convert("RGB")

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
        self._background = parse_color(color)

    def set_background_image(self, file):
        """Sets the background to an image

        The image is loaded into memory immediately so it remains available
        even after the matrix library drops root privileges.

        :param string file: The file location of the image to display.
        """
        if not os.path.exists(file):
            raise ValueError(f"Specified background file {file} was not found")
        self._background = Image.open(file).convert("RGBA")

    def animate(self, target, class_name, method_name, **kwargs):
        """Animate a Message or text string."""
        message_kwargs = {
            key: kwargs.pop(key)
            for key in (
                "font",
                "color",
                "stroke_width",
                "stroke_color",
                "shadow_intensity",
                "shadow_offset",
                "opacity",
                "image",
            )
            if key in kwargs
        }
        message = self._resolve_canvas(target, **message_kwargs)
        return dispatch_animation(self, message, class_name, method_name, **kwargs)

    def scroll_in(self, target, from_="left", **kwargs):
        """Scroll a target onto the display."""
        return self.animate(target, "Scroll", f"in_from_{from_}", **kwargs)

    def scroll_out(self, target=None, to="left", **kwargs):
        """Scroll a target off the display."""
        return self.animate(target, "Scroll", f"out_to_{to}", **kwargs)

    def loop(self, target=None, direction="left", **kwargs):
        """Loop a target across the display."""
        return self.animate(target, "Loop", direction, **kwargs)

    def join_in(self, target, direction="horizontally", **kwargs):
        """Join split halves of a target onto the display."""
        return self.animate(target, "Split", f"join_in_{direction}", **kwargs)

    def split_out(self, target=None, direction="horizontally", **kwargs):
        """Split a target off the display."""
        return self.animate(target, "Split", f"split_out_{direction}", **kwargs)

    def show(self, target=None, **kwargs):
        """Show a target at the current position."""
        return self.animate(target, "Static", "show", **kwargs)

    def hide(self, target=None, **kwargs):
        """Hide the current target."""
        return self.animate(target, "Static", "hide", **kwargs)

    def blink(self, target=None, count=3, duration=1, **kwargs):
        """Blink a target on and off."""
        return self.animate(target, "Static", "blink", count=count, duration=duration, **kwargs)

    def flash(self, target=None, count=3, duration=1, **kwargs):
        """Fade a target in and out."""
        return self.animate(target, "Static", "flash", count=count, duration=duration, **kwargs)

    def fade_in(self, target=None, duration=1, steps=50, **kwargs):
        """Fade a target in."""
        return self.animate(target, "Static", "fade_in", duration=duration, steps=steps, **kwargs)

    def fade_out(self, target=None, duration=1, steps=50, **kwargs):
        """Fade a target out."""
        return self.animate(target, "Static", "fade_out", duration=duration, steps=steps, **kwargs)

    @staticmethod
    def _wait(start_time, duration):
        """Uses time.monotonic() to wait from the start time for a specified duration"""
        while time.monotonic() < (start_time + duration):
            pass
        return time.monotonic()
