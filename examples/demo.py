#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time

from opensign import Message, OpenSign


def main():
    sign = OpenSign(chain=6, slowdown_gpio=5)
    sign.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    sign.add_font("comic", "/usr/share/fonts/truetype/msttcorefonts/Comic_Sans_MS.ttf", 14)
    sign.set_background_image("background.jpg")

    message1 = Message(font=sign.fonts.get("dejavu"))
    message1.set_stroke(1, (255, 255, 255))
    message1.add_text("Scroll Text In", color=(255, 0, 0))
    message1.set_shadow()

    message2 = Message(font=sign.fonts.get("comic"))
    message2.set_stroke(1, (0, 0, 0))
    message2.add_image("logo.png")
    message2.add_text("Maker Melissa's Lab", color=(255, 255, 0), y_offset=-2)
    message2.set_shadow()

    message3 = Message(font=sign.fonts.get("dejavu"))
    message3.set_stroke(1, (0, 0, 0))
    message3.add_text("https://makermelissa.com/", color=(255, 0, 0))

    message4 = Message(font=sign.fonts.get("dejavu"))
    message4.set_stroke(1, (0, 0, 0))
    message4.add_text("Subscribe to my Channel", color=(255, 255, 255))
    message4.set_shadow()

    while True:
        sign.scroll_in(message1, from_="left")
        time.sleep(1)

        message1.clear()
        message1.add_text("Change Messages")
        sign.show(message1)
        time.sleep(1)

        message1.clear()
        message1.add_text("And Scroll Out")
        sign.show(message1)
        sign.scroll_out(to="right")
        time.sleep(1)

        sign.join_in(message1, direction="vertically")
        sign.loop(direction="left")
        sign.flash(message1, count=3)
        sign.split_out(direction="vertically")
        time.sleep(1)

        sign.set_background_color((0, 255, 0))
        sign.fade_in(message2)
        time.sleep(1)

        sign.fade_out()
        sign.scroll_in(message3, from_="top")
        time.sleep(1)

        sign.scroll_out(to="bottom")
        sign.scroll_in(message4, from_="right")
        sign.wipe_out(to="left")
        sign.wipe_in(message4, from_="right")
        sign.scroll_in(
            "Hello from a temporary Message", from_="left", color="crimson", font="dejavu"
        )
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
