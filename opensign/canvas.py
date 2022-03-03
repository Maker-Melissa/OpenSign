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
`opensign.canvas`
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

from PIL import Image, ImageDraw, ImageFont

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/makermelissa/OpenSign.git"


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
        then the new font will automatically become the current font

        :param string name: The name of the font. This is used when setting the font.
        :param string file: The filename of the font. This should be the full path.
        :param float size: (optional) The font-size to use if it is a True Type font.
                           Set to None for bitmap fonts. (default=None)
        :param bool use: (optional) Whether or not the font should immediately be used.
                         (default=False)
        """
        if size is not None:
            self._fonts[name] = ImageFont.truetype(file, size)
        else:
            self._fonts[name] = ImageFont.load(file)
        if use or self._current_font is None:
            self._current_font = self._fonts[name]

    def set_font(self, fontname):
        """Set the current font

        :param string fontname: The name of the font to use. This should match the name parameter
                                used when adding the font.
        """
        if self._fonts.get(fontname) is None:
            raise ValueError("Font name not found.")
        self._current_font = self._fonts[fontname]

    def set_stroke(self, width, color=None):
        """Set the text stroke width and color

        :param int width: The stroke width to use. This is how wide the outline of
                          the text is in pixels.
        :param color: (optional) The color of the stroke. (default=None)
        :type color: tuple or list or int
        """
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
        """Set the current text color.

        :param color: The color of the text.
        :type color: tuple or list or int
        """
        self._current_color = self._convert_color(color)

    def set_shadow(self, intensity=0.5, offset=1):
        """Set the canvas to display a shadow of the content. To turn shadow off, set
        the intensity to 0. The shadow is global for the entire canvas.

        :param float intensity: (optional) The opaquness of the shadow (default=0.5).
        :param int offset: (optional) The offset in pixels towards the lower right (default=1).
        """
        intensity = max(0, min(1.0, intensity))
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
        """Add text to the canvas.

        :param string text: The text to add.
        :param color: (optional) The color of the text to override the current setting.
                      (default=Current Setting)
        :param string fontname: (optional) The name of the font to override the current setting.
                                (default=Current Setting)
        :param int stroke_width: (optional) The stroke width to override the current setting.
                                 (default=Current Setting)
        :param stroke_color: (optional) The color of the stroke to override the current setting.
                             (default=Current Setting)
        :param int x_offset: (optional) The amount of x-offset to nudge the text. (default=0)
        :param int y_offset: (optional) The amount of y-offset to nudge the text. (default=0)
        :type color: tuple or list or int
        :type stroke_color: tuple or list or int
        """
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

        lines = text.split("\n")
        for index, line in enumerate(lines):
            (text_width, text_height) = font.getsize(line, stroke_width=stroke_width)
            self._enlarge_canvas(text_width, text_height)
            # Draw the text
            self._draw.text(
                (x + x_offset, y + y_offset),
                line,
                font=font,
                fill=color,
                stroke_width=stroke_width,
                stroke_fill=stroke_color,
            )
            # Get size and add to cursor
            self._cursor[0] += text_width
            if index < len(lines) - 1:
                y += text_height
                self._cursor[0] = 0
                self._cursor[1] += text_height

    # pylint: enable=too-many-arguments

    def add_image(self, file):
        """Add an image to the canvas.

        :param string file: The filename of the image. This should be the full path.
        """
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
        value = max(value, 0)
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
        transparent and 1 is opaque."""
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
