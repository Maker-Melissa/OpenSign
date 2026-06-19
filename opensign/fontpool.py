# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""
`opensign.fontpool`
================================================================================

A shared font pool to avoid loading the same font file multiple times.

* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Software and Dependencies:**

* Python Imaging Library (Pillow)

"""

from PIL import ImageFont


class FontPool:
    """A pool of fonts for reuse to avoid loading duplicates across canvases."""

    def __init__(self):
        self._fonts = {}
        self.add_default()

    def add_default(self):
        """Add Pillow's default font as 'default'."""
        if "default" not in self._fonts:
            self._fonts["default"] = ImageFont.load_default()

    def add_font(self, name, file, size=None):
        """Add a font to the pool. If already present, returns without reloading.

        :param string name: A unique name key for looking up this font later.
        :param string file: Path to the font file (TrueType or bitmap).
        :param int size: (optional) Font size for TrueType fonts. Omit for bitmap fonts.
        """
        if name in self._fonts:
            return
        if size is not None:
            self._fonts[name] = ImageFont.truetype(file, size)
        else:
            self._fonts[name] = ImageFont.load(file)

    def get(self, name):
        """Retrieve a font by name.

        :param string name: The name key used when adding the font.
        :returns: The PIL ImageFont object, or None if not found.
        """
        return self._fonts.get(name)

    def list_fonts(self):
        """Return a sorted list of registered font names."""
        return sorted(self._fonts.keys())
