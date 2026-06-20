#!/usr/bin/env python
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

import time

from opensign import OpenSign


def main():
    sign = OpenSign(chain=6)
    sign.message.font = sign.message.load_font(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        14,
    )
    sign.add_text("Hello ", color=(255, 0, 0))
    sign.add_text("World!", color=(128, 255, 0))

    while True:
        sign.scroll_in(dir_from="left")
        time.sleep(1)
        sign.scroll_out(dir_to="right")
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
