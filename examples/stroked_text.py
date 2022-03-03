#!/usr/bin/env python
from opensign import OpenSign
from opensign.canvas import OpenSignCanvas


def main():
    message = OpenSignCanvas()
    message.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message.set_stroke(1, (255, 255, 255))
    message.add_text("Hello World!", color=(0, 255, 0))

    sign = OpenSign(chain=6)
    while True:
        sign.scroll_in_from_left(message)
        sign.sleep(1)
        sign.scroll_out_to_right(message)
        sign.sleep(1)


# Main function
if __name__ == "__main__":
    main()
