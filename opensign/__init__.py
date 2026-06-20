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

from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

from .animations import animate as dispatch_animation
from .colors import parse_color
from .fontpool import FontPool
from .message import Message

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/Maker-Melissa/PyOpenSign.git"
DEFAULT = "default"


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
        self.message = Message(font_pool=self.fonts, on_change=self._readjust_message_position)
        self.canvases = {DEFAULT: self.message}
        # pylint: enable=too-many-locals

    def add_font(self, name, file, size=None):
        """Add a font to the shared font pool.

        Fonts registered here are available to any canvas created via this sign.

        :param string name: A unique name key for looking up this font later.
        :param string file: Path to the font file (TrueType or bitmap).
        :param int size: (optional) Font size for TrueType fonts. Omit for bitmap fonts.
        """
        return self.fonts.add_font(name, file, size)

    def _resolve_font(self, font, font_file=None, font_size=None):
        """Return a font object from a shared name, file, or direct font object."""
        if font_file is not None:
            return Message.load_font(font_file, font_size)

        if isinstance(font, str):
            font = self.fonts.get(font)
            if font is None:
                raise ValueError("Font name not found.")

        return font

    def _resolve_canvas(self, canvas=None):
        """Return a canvas from a name, Message object, or the default message."""
        if canvas is None:
            return self.message
        if isinstance(canvas, Message):
            return canvas
        if isinstance(canvas, str):
            try:
                return self.canvases[canvas]
            except KeyError as error:
                raise ValueError(f"Canvas {canvas!r} was not found.") from error
        raise TypeError("Canvas must be a name, Message, or None.")

    def _resolve_message(self, canvas=None):
        """Return a canvas when it has content."""
        message = self._resolve_canvas(canvas)
        if not (message.width or message.height):
            raise ValueError("No message has been created yet.")
        return message

    def _readjust_message_position(self, canvas=None):
        """Recenter a canvas after its contents change."""
        message = self._resolve_canvas(canvas)
        if message.width or message.height:
            message.position = self._get_centered_position(message)
        else:
            message.position = (0, 0)
        if message is self.message:
            self._position = message.position

    def create_canvas(self, name, **kwargs):
        """Create and register a persistent canvas."""
        if name in self.canvases:
            raise ValueError(f"Canvas {name!r} already exists.")
        self.canvases[name] = Message(
            font_pool=self.fonts,
            on_change=self._readjust_message_position,
            **kwargs,
        )
        self._readjust_message_position(name)
        return self.canvases[name]

    def get_canvas(self, name):
        """Return a registered persistent canvas."""
        return self._resolve_canvas(name)

    def remove_canvas(self, name):
        """Remove a registered persistent canvas."""
        if name == DEFAULT:
            raise ValueError("The default message canvas cannot be removed.")
        del self.canvases[name]

    # pylint: disable=too-many-arguments
    def add_text(
        self,
        text,
        color=None,
        font=None,
        font_file=None,
        font_size=None,
        stroke=None,
        stroke_width=None,
        stroke_color=None,
        x_offset=0,
        y_offset=0,
        canvas=None,
    ):
        """Add text to the default canvas, or to a named canvas when provided."""
        self._resolve_canvas(canvas).add_text(
            text,
            color=color,
            font=font,
            font_file=font_file,
            font_size=font_size,
            stroke=stroke,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            x_offset=x_offset,
            y_offset=y_offset,
        )

    # pylint: enable=too-many-arguments

    def add_image(self, file, canvas=None):
        """Add an image to the default canvas, or to a named canvas when provided."""
        self._resolve_canvas(canvas).add_image(file)

    def clear(self, canvas=None):
        """Clear the default canvas, or a named canvas when provided."""
        self._resolve_canvas(canvas).clear()

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

    def _background_image(self):
        """Return a full-size RGBA background image."""
        if isinstance(self._background, tuple):
            return Image.new(
                "RGBA", (self._matrix.width, self._matrix.height), self._background
            )

        combined_image = Image.new("RGBA", (self._matrix.width, self._matrix.height))
        combined_image.alpha_composite(self._background)
        return combined_image

    def _positioned_foreground(self, image, x, y, opacity=1.0):
        """Return a full-size foreground image clipped to the display bounds."""
        source_x = max(0 - x, 0)
        source_y = max(0 - y, 0)
        dest_x = max(x, 0)
        dest_y = max(y, 0)
        visible_width = min(image.width - source_x, self._matrix.width - dest_x)
        visible_height = min(image.height - source_y, self._matrix.height - dest_y)

        foreground_image = Image.new(
            "RGBA", (self._matrix.width, self._matrix.height), (0, 0, 0, 0)
        )
        if visible_width <= 0 or visible_height <= 0:
            return foreground_image

        visible_image = image.crop(
            (
                source_x,
                source_y,
                source_x + visible_width,
                source_y + visible_height,
            )
        )
        foreground_image.alpha_composite(visible_image, dest=(dest_x, dest_y))

        opacity = max(0, min(1.0, opacity))
        if opacity < 1:
            alpha = foreground_image.split()[-1]
            foreground_image.putalpha(alpha.point(lambda value: round(value * opacity)))
        return foreground_image

    def _composite_layer(
        self,
        combined_image,
        image,
        x,
        y,
        opacity=1.0,
        shadow_intensity=0,
        shadow_offset=0,
    ):
        """Composite one image layer onto a full-size RGBA image."""
        foreground_image = self._positioned_foreground(image, x, y, opacity=opacity)

        alpha = foreground_image.split()[-1]
        if shadow_intensity:
            shadow_alpha = alpha.point(lambda value: round(value * shadow_intensity))
            shadow_shifted = Image.new("L", alpha.size, 0)
            shadow_shifted.paste(shadow_alpha, box=(shadow_offset, shadow_offset))
            shadow_image = Image.new("RGBA", combined_image.size, (0, 0, 0, 0))
            shadow_image.putalpha(shadow_shifted)
            combined_image.alpha_composite(shadow_image)

        combined_image.alpha_composite(foreground_image)
        return combined_image

    # pylint: disable=too-many-arguments
    def _add_background(self, image, x, y, opacity=1.0, shadow_intensity=0, shadow_offset=1):
        """Combine one foreground image with the background."""
        combined_image = self._background_image()
        combined_image = self._composite_layer(
            combined_image,
            image,
            x,
            y,
            opacity=opacity,
            shadow_intensity=shadow_intensity,
            shadow_offset=shadow_offset,
        )
        return combined_image.convert("RGB")

    # pylint: enable=too-many-arguments

    def _draw(self, canvas, x, y, opacity=1.0):
        """Draws a canvas to the buffer taking its current settings into account.
        It also sets the current position and performs a swap.
        """
        self._position = (x, y)
        canvas.position = (x, y)
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

    def draw_canvases(self, *canvases):
        """Draw multiple persistent canvases in order."""
        if not canvases:
            canvases = tuple(self.canvases)

        combined_image = self._background_image()
        for canvas in canvases:
            message = self._resolve_message(canvas)
            x, y = message.position
            combined_image = self._composite_layer(
                combined_image,
                message.get_image(),
                x,
                y,
                opacity=message.opacity,
                shadow_intensity=message.shadow_intensity,
                shadow_offset=message.shadow_offset,
            )

        self._buffer.SetImage(combined_image.convert("RGB"), 0, 0)
        self._update()

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

    def animate(self, class_name, method_name, *, canvas=None, **kwargs):
        """Animate a canvas."""
        message = self._resolve_message(canvas)
        self._position = message.position
        return dispatch_animation(self, message, class_name, method_name, **kwargs)

    def scroll_in(self, dir_from="left", canvas=None, **kwargs):
        """Scroll a canvas onto the display."""
        return self.animate("Scroll", f"in_from_{dir_from}", canvas=canvas, **kwargs)

    def scroll_out(self, dir_to="left", canvas=None, **kwargs):
        """Scroll a canvas off the display."""
        return self.animate("Scroll", f"out_to_{dir_to}", canvas=canvas, **kwargs)

    def wipe_in(self, dir_from="left", canvas=None, **kwargs):
        """Wipe a canvas onto the display."""
        return self.animate("Wipe", f"in_from_{dir_from}", canvas=canvas, **kwargs)

    def wipe_out(self, dir_to="left", canvas=None, **kwargs):
        """Wipe a canvas off the display."""
        return self.animate("Wipe", f"out_to_{dir_to}", canvas=canvas, **kwargs)

    def loop(self, dir="left", canvas=None, **kwargs):
        """Loop a canvas across the display."""
        return self.animate("Loop", dir, canvas=canvas, **kwargs)

    def join_in(self, dir="horizontally", canvas=None, **kwargs):
        """Join split halves of a canvas onto the display."""
        return self.animate("Split", f"join_in_{dir}", canvas=canvas, **kwargs)

    def split_out(self, dir="horizontally", canvas=None, **kwargs):
        """Split a canvas off the display."""
        return self.animate("Split", f"split_out_{dir}", canvas=canvas, **kwargs)

    def show(self, canvas=None, **kwargs):
        """Show a canvas at its current position."""
        return self.animate("Static", "show", canvas=canvas, **kwargs)

    def hide(self, canvas=None, **kwargs):
        """Hide a canvas."""
        return self.animate("Static", "hide", canvas=canvas, **kwargs)

    def blink(self, count=3, duration=1, canvas=None, **kwargs):
        """Blink a canvas on and off."""
        return self.animate(
            "Static", "blink", canvas=canvas, count=count, duration=duration, **kwargs
        )

    def flash(self, count=3, duration=1, canvas=None, **kwargs):
        """Fade a canvas in and out."""
        return self.animate(
            "Static", "flash", canvas=canvas, count=count, duration=duration, **kwargs
        )

    def fade_in(self, duration=1, steps=50, canvas=None, **kwargs):
        """Fade a canvas in."""
        return self.animate("Fade", "in_", canvas=canvas, duration=duration, steps=steps, **kwargs)

    def fade_out(self, duration=1, steps=50, canvas=None, **kwargs):
        """Fade a canvas out."""
        return self.animate("Fade", "out", canvas=canvas, duration=duration, steps=steps, **kwargs)

    @staticmethod
    def _wait(start_time, duration):
        """Uses time.monotonic() to wait from the start time for a specified duration"""
        while time.monotonic() < (start_time + duration):
            pass
        return time.monotonic()
