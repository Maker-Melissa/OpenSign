#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time
from pathlib import Path

from opensign import Message, OpenSign

ASSET_DIR = Path(__file__).resolve().parent


def main():
    sign = OpenSign(chain=6, slowdown_gpio=5)
    sign.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    sign.add_font("comic", "/usr/share/fonts/truetype/msttcorefonts/Comic_Sans_MS.ttf", 14)
    sign.set_background_image(ASSET_DIR / "background.jpg")

    message1 = Message(
        "Scroll Text In",
        font=sign.fonts.get("dejavu"),
        color=(255, 0, 0),
        stroke=(1, (255, 255, 255)),
        shadow=(0.5, 1),
    )

    message2 = Message(
        "Maker Melissa's Lab",
        image=ASSET_DIR / "logo.png",
        font=sign.fonts.get("comic"),
        color=(255, 255, 0),
        stroke=(1, (0, 0, 0)),
        shadow=(0.5, 1),
        # y_offset=-2,
    )

    message3 = Message(
        "https://makermelissa.com/",
        font=sign.fonts.get("dejavu"),
        color=(255, 0, 0),
        stroke=(1, (0, 0, 0)),
    )

    message4 = Message(
        "Subscribe to my Channel",
        font=sign.fonts.get("dejavu"),
        color=(255, 255, 255),
        stroke=(1, (0, 0, 0)),
        shadow=(0.5, 1),
    )

    while True:
        sign.scroll_in(message1, dir_from="left")  # Scroll the message 1 in from the left
        time.sleep(1)  # Wait for a moment

        message1.clear()  # Clear the message contents for reuse
        message1.add_text("Change Messages")  # Add new text to the message
        sign.show(message1)  # Update the sign with the new message changes
        time.sleep(1)  # Wait for a moment

        message1.clear()  # Clear the message again to reuse it for another message
        message1.add_text("And Scroll Out")  # Add new text to the message
        sign.show(message1)  # Update the sign with the new message changes
        sign.scroll_out(dir_to="right")  # Scroll the message out to the right
        time.sleep(1)  # Wait for a moment

        sign.join_in(message1, dir="vertically")  # Join the message in vertically
        sign.loop(dir="left")  # Loop the message out to the left and back in from the right
        sign.flash(message1, count=3)  # Flash the message 3 times
        sign.split_out(dir="vertically")  # Split the message out vertically
        time.sleep(1)  # Wait for a moment

        sign.set_background_color((0, 255, 0))  # Change the background color to green
        sign.fade_in(message2)  # Fade in the message2
        time.sleep(1)  # Wait for a moment

        sign.fade_out()  # Fade out the current message
        sign.scroll_in(message3, dir_from="top")  # Scroll the message3 in from the top
        time.sleep(1)  # Wait for a moment

        sign.scroll_out(dir_to="bottom")  # Scroll the message3 out to the bottom
        sign.scroll_in(message4, dir_from="right")  # Scroll the message4 in from the right
        sign.wipe_out(dir_to="left")  # Wipe the message4 out to the left
        sign.wipe_in(message4, dir_from="right")  # Wipe the message4 in from the right
        sign.scroll_in(
            "Hello from a temporary Message", dir_from="left", color="crimson", font="dejavu"
        )  # Scroll in a temporary message from the left
        time.sleep(1)  # Wait for a moment


# Main function
if __name__ == "__main__":
    main()
