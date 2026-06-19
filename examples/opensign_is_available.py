#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time

from opensign import Message, OpenSign


def main():
    message = Message()
    message.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message.set_stroke(1, (0, 0, 0))
    message.add_text("OpenSign is now available", color=(255, 255, 0))
    message.set_shadow()

    sign = OpenSign(chain=6)
    sign.set_background_image("background.jpg")

    while True:
        sign.scroll_in(message, from_="top")
        time.sleep(1)
        sign.scroll_out(to="bottom")
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
