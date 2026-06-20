#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time
from pathlib import Path

from opensign import OpenSign

ASSET_DIR = Path(__file__).resolve().parent


def main():
    sign = OpenSign(chain=6, slowdown_gpio=5)
    sign.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    sign.add_font("comic", "/usr/share/fonts/truetype/msttcorefonts/Comic_Sans_MS.ttf", 14)
    sign.set_background_image(ASSET_DIR / "background.jpg")

    while True:
        sign.clear()
        sign.message.shadow = (0.5, 1)
        sign.add_text(
            "Scroll Text In",
            font="dejavu",
            color=(255, 0, 0),
            stroke=(1, (255, 255, 255)),
        )
        sign.scroll_in(dir_from="left")  # Scroll the message in from the left
        time.sleep(1)  # Wait for a moment

        sign.clear()
        sign.message.shadow = (0.5, 1)
        sign.add_text(
            "Change Messages",
            font="dejavu",
            color=(255, 0, 0),
            stroke=(1, (255, 255, 255)),
        )
        sign.show()  # Update the sign with new message contents
        time.sleep(1)  # Wait for a moment

        sign.clear()
        sign.message.shadow = (0.5, 1)
        sign.add_text(
            "And Scroll Out",
            font="dejavu",
            color=(255, 0, 0),
            stroke=(1, (255, 255, 255)),
        )
        sign.show()  # Update the sign with new message contents
        sign.scroll_out(dir_to="right")  # Scroll the message out to the right
        time.sleep(1)  # Wait for a moment

        sign.clear()
        sign.message.shadow = (0.5, 1)
        sign.add_text(
            "Scroll Text In",
            font="dejavu",
            color=(255, 0, 0),
            stroke=(1, (255, 255, 255)),
        )
        sign.join_in(dir="vertically")  # Join the message in vertically
        sign.loop(dir="left")  # Loop the message out to the left and back in from the right
        sign.flash(count=3)  # Flash the current message 3 times
        sign.split_out(dir="vertically")  # Split the message out vertically
        time.sleep(1)  # Wait for a moment

        sign.set_background_color((0, 255, 0))  # Change the background color to green
        sign.clear()
        sign.message.shadow = (0.5, 1)
        sign.add_image(ASSET_DIR / "logo.png")
        sign.add_text(
            "Maker Melissa's Lab",
            font="comic",
            color=(255, 255, 0),
            stroke=(1, (0, 0, 0)),
        )
        sign.fade_in()  # Fade in the message
        time.sleep(1)  # Wait for a moment

        sign.fade_out()  # Fade out the current message
        sign.clear()
        sign.message.shadow = (0, 0)
        sign.add_text(
            "https://makermelissa.com/",
            font="dejavu",
            color=(255, 0, 0),
            stroke=(1, (0, 0, 0)),
        )
        sign.scroll_in(dir_from="top")  # Scroll the message in from the top
        time.sleep(1)  # Wait for a moment

        sign.scroll_out(dir_to="bottom")  # Scroll the message out to the bottom
        sign.clear()
        sign.message.shadow = (0.5, 1)
        sign.add_text(
            "Subscribe to my Channel",
            font="dejavu",
            color=(255, 255, 255),
            stroke=(1, (0, 0, 0)),
        )
        sign.scroll_in(dir_from="right")  # Scroll the message in from the right
        sign.wipe_out(dir_to="left")  # Wipe the message out to the left
        sign.clear()
        sign.message.shadow = (0.5, 1)
        sign.add_text(
            "Subscribe to my Channel",
            font="dejavu",
            color=(255, 255, 255),
            stroke=(1, (0, 0, 0)),
        )
        sign.wipe_in(dir_from="right")  # Wipe the message in from the right
        sign.clear()
        sign.message.shadow = (0, 0)
        sign.add_text("Hello from the managed Message", color="crimson", font="dejavu")
        sign.scroll_in(dir_from="left")  # Scroll in a new message from the left
        time.sleep(1)  # Wait for a moment


# Main function
if __name__ == "__main__":
    main()
