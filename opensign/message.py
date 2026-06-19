# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Renderable message primitives for PyOpenSign."""

from PIL import Image, ImageDraw, ImageFont

from .colors import parse_color_alpha

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/Maker-Melissa/PyOpenSign.git"


class Message:
    """A stylable renderable image that can contain text and graphics."""

    def __init__(self, font=None, opacity=1.0):
        self._fonts = {}
        self._current_font = font
        self._current_color = (255, 0, 0, 255)
        self._image = Image.new("RGBA", (0, 0), (0, 0, 0, 0))
        self._draw = ImageDraw.Draw(self._image)
        self._cursor = [0, 0]
        self._stroke_width = 0
        self._stroke_color = None
        self._shadow_intensity = 0
        self._shadow_offset = 0
        self._opacity = 1.0
        self.opacity = opacity

    def add_font(self, name, file, size=None, use=False):
        """Add a font to this message's local font pool."""
        if size is not None:
            self._fonts[name] = ImageFont.truetype(file, size)
        else:
            self._fonts[name] = ImageFont.load(file)
        if use or self._current_font is None:
            self._current_font = self._fonts[name]
        return self._fonts[name]

    def set_font(self, fontname):
        """Set the current font by local font name."""
        if self._fonts.get(fontname) is None:
            raise ValueError("Font name not found.")
        self._current_font = self._fonts[fontname]

    def set_stroke(self, width, color=None):
        """Set the text stroke width and color."""
        self._stroke_width = width
        self._stroke_color = parse_color_alpha(color) if color is not None else None

    def _convert_color(self, color):
        return parse_color_alpha(color)

    def _enlarge_canvas(self, width, height):
        new_width = max(self._cursor[0] + width, self._image.width)
        new_height = max(self._cursor[1] + height, self._image.height)
        new_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
        new_image.alpha_composite(self._image)
        self._image = new_image
        self._draw = ImageDraw.Draw(self._image)

    def set_color(self, color):
        """Set the current text color."""
        self._current_color = parse_color_alpha(color)

    def set_shadow(self, intensity=0.5, offset=1):
        """Set the global message shadow."""
        self.shadow_intensity = intensity
        self.shadow_offset = offset

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
        """Add text to the message."""
        if isinstance(font, str):
            font = self._fonts[font]
        elif font is None:
            font = self._current_font
        if font is None:
            font = ImageFont.load_default()

        x, y = self._cursor
        color = self._current_color if color is None else parse_color_alpha(color)
        stroke_color = (
            self._stroke_color if stroke_color is None else parse_color_alpha(stroke_color)
        )
        stroke_width = self._stroke_width if stroke_width is None else stroke_width

        lines = text.split("\n")
        for index, line in enumerate(lines):
            text_width, text_height = self._text_size(font, line, stroke_width=stroke_width)
            self._enlarge_canvas(text_width, text_height)
            self._draw.text(
                (x + x_offset, y + y_offset),
                line,
                font=font,
                fill=color,
                stroke_width=stroke_width,
                stroke_fill=stroke_color,
            )
            self._cursor[0] += text_width
            if index < len(lines) - 1:
                y += text_height
                self._cursor[0] = 0
                self._cursor[1] += text_height

    # pylint: enable=too-many-arguments

    @staticmethod
    def _text_size(font, text, stroke_width=0):
        """Return (width, height) of text."""
        left, top, right, bottom = font.getbbox(text, stroke_width=stroke_width)
        return (right - left, bottom - top)

    def add_image(self, file):
        """Add an image to the message."""
        x, y = self._cursor
        new_image = Image.open(file).convert("RGBA")
        self._enlarge_canvas(new_image.width, new_image.height)
        self._image.alpha_composite(new_image, dest=(x, y))
        self._cursor[0] += new_image.width

    def clear(self):
        """Clear the message content, but retain style settings."""
        self._image = Image.new("RGBA", (0, 0), (0, 0, 0, 0))
        self._draw = ImageDraw.Draw(self._image)
        self._cursor = [0, 0]

    def get_image(self):
        """Get the message content as an image."""
        return self._image

    @property
    def width(self):
        """Get the current message width in pixels."""
        return self._image.width

    @property
    def height(self):
        """Get the current message height in pixels."""
        return self._image.height

    @property
    def shadow_offset(self):
        """Get or set the current shadow offset in pixels."""
        return self._shadow_offset

    @shadow_offset.setter
    def shadow_offset(self, value):
        if not isinstance(value, int):
            raise TypeError("Shadow offset must be an integer.")
        self._shadow_offset = max(value, 0)

    @property
    def shadow_intensity(self):
        """Get or set the shadow intensity from 0 to 1."""
        return self._shadow_intensity

    @shadow_intensity.setter
    def shadow_intensity(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Shadow intensity must be an integer or float.")
        self._shadow_intensity = max(0, min(1.0, value))

    @property
    def opacity(self):
        """Get or set the maximum opacity from 0 to 1."""
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Opacity must be an integer or float.")
        self._opacity = max(0, min(1.0, value))

    @property
    def cursor(self):
        """Get or set the current cursor position."""
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        if isinstance(value, (tuple, list)) and len(value) >= 2:
            self._cursor = [value[0], value[1]]
        else:
            raise TypeError("Value must be a tuple or list.")
