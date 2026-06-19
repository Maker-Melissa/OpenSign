#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time

from opensign import Message, OpenSign


def main():
    message = Message(
        "Hello World!",
        font_file="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        font_size=14,
        color=(255, 255, 0),
    )

    sign = OpenSign(chain=6)
    sign.set_background_image("background.jpg")

    while True:
        sign.scroll_in(message, dir_from="left")
        time.sleep(1)
        sign.scroll_out(dir_to="right")
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
