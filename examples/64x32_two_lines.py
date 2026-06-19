#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time

from opensign import Message, OpenSign


def main():
    message = Message(
        "Hello\nWorld!",
        font_file="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        font_size=14,
        color=(0, 255, 0),
        stroke=(1, (255, 255, 255)),
    )

    sign = OpenSign(columns=64, rows=32, slowdown_gpio=2)
    while True:
        sign.scroll_in(message, dir_from="left")
        time.sleep(1)
        sign.scroll_out(dir_to="right")
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
