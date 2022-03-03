#!/usr/bin/env python
import time
import copy
from opensign import OpenSign
from opensign.canvas import OpenSignCanvas

"""
Script
Scroll in text
an images
Fade text in
and fade out

"""


def duplicate(item_to_duplicate):
    new_canvas = copy.copy(item_to_duplicate)
    new_canvas.clear()
    return new_canvas


def main():
    message1 = OpenSignCanvas()
    message1.add_font(
        "comic", "/usr/share/fonts/truetype/msttcorefonts/Comic_Sans_MS.ttf", 14
    )
    message1.set_stroke(1, (0, 0, 0))
    message1.add_image("/home/pi/logo.png")
    message1.add_text("Maker Melissa's Lab", color=(255, 255, 0), y_offset=-2)
    message1.set_shadow()

    message2 = OpenSignCanvas()
    message2.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message2.set_stroke(1, (0, 0, 0))
    message2.add_text("New Video Dropping Soon", color=(255, 128, 0))
    message2.set_shadow()

    message3 = duplicate(message2)
    message3.add_text("This is a copy test", color=(255, 0, 0))

    circuit_image = "/home/pi/background.jpg"
    sign = OpenSign(chain=6, gpio_mapping="adafruit-hat-pwm")

    while True:
        sign.set_background_image(circuit_image)
        sign.join_in_vertically(message1)
        time.sleep(1)
        sign.fade_out(message1)
        sign.join_in_horizontally(message2)
        sign.flash(message2, duration=2)
        sign.split_out_vertically(message2)
        time.sleep(0.5)
        sign.scroll_in_from_left(message3)
        time.sleep(1)
        sign.scroll_out_to_right(message3)


# Main function
if __name__ == "__main__":
    main()
