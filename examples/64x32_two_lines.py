#!/usr/bin/env python
import time
from opensign import OpenSign
from opensign.canvas import OpenSignCanvas


def main():
    message = OpenSignCanvas()
    message.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message.set_stroke(1, (255, 255, 255))
    message.add_text("Hello\nWorld!", color=(0, 255, 0))

    sign = OpenSign(columns=64, rows=32, slowdown_gpio=2)
    while True:
        sign.scroll_in_from_left(message)
        time.sleep(1)
        sign.scroll_out_to_right(message)
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
