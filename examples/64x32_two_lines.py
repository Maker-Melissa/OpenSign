#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time

from opensign import Message, OpenSign


def main():
    message = Message()
    message.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message.set_stroke(1, (255, 255, 255))
    message.add_text("Hello\nWorld!", color=(0, 255, 0))

    sign = OpenSign(columns=64, rows=32, slowdown_gpio=2)
    while True:
        sign.scroll_in(message, from_="left")
        time.sleep(1)
        sign.scroll_out(to="right")
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
