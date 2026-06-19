#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time

from opensign import Message, OpenSign


def main():
    message = Message(
        "OpenSign is now available",
        font_file="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        font_size=14,
        color=(255, 255, 0),
        stroke=(1, (0, 0, 0)),
        shadow=(0.5, 1),
    )

    sign = OpenSign(chain=6)
    sign.set_background_image("background.jpg")

    while True:
        sign.scroll_in(message, dir_from="top")
        time.sleep(1)
        sign.scroll_out(dir_to="bottom")
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
