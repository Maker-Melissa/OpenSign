#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time

from opensign import Message, OpenSign


def main():
    message = Message()
    message.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message.add_text("Hello ", color=(255, 0, 0))
    message.add_text("World!", color=(128, 255, 0))

    sign = OpenSign(chain=6)
    while True:
        sign.scroll_in(message, from_="left")
        time.sleep(1)
        sign.scroll_out(to="right")
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
