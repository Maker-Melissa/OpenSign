#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time
from pathlib import Path

from opensign import DEFAULT, OpenSign

ASSET_DIR = Path(__file__).resolve().parent


def main():
    sign = OpenSign(chain=6, slowdown_gpio=5)
    sign.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    sign.add_font("dejavu_small", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    sign.set_background_image(ASSET_DIR / "background.jpg")

    default_canvas = sign.get_canvas(DEFAULT)
    logo = sign.create_canvas("logo")
    caption = sign.create_canvas("caption")

    sign.add_text(  # Add text to the default canvas
        "Default Canvas",
        font="dejavu",
        color=(255, 0, 0),
        stroke=(1, (0, 0, 0)),
    )
    default_canvas.opacity = 0.55
    default_canvas.shadow = (0.5, 1)

    logo.add_image(ASSET_DIR / "logo.png")
    logo.opacity = 0.55
    logo.position = default_canvas.position

    caption.add_text(
        "Named Canvas",
        font="dejavu_small",
        color=(255, 255, 0),
        stroke=(1, (0, 0, 0)),
    )
    caption.opacity = 0.8
    caption.position = (default_canvas.position[0], default_canvas.position[1] + 16)

    while True:
        sign.draw_canvases(default_canvas, logo, caption)
        time.sleep(2)

        sign.scroll_out(canvas="logo", dir_to="right")
        time.sleep(1)

        sign.scroll_in(canvas="logo", dir_from="left")
        logo.position = default_canvas.position
        sign.draw_canvases(default_canvas, logo, caption)
        time.sleep(2)

        caption.opacity = 0.35
        sign.draw_canvases(default_canvas, logo, caption)
        time.sleep(1)

        caption.opacity = 0.8
        sign.draw_canvases(default_canvas, logo, caption)
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
