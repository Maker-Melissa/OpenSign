#!/usr/bin/env python
import time
from opensign import OpenSign
from opensign.canvas import OpenSignCanvas


def main():
    message1 = OpenSignCanvas()
    message1.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message1.set_stroke(1, (255, 255, 255))
    message1.add_text("Scroll Text In", color=(255, 0, 0))
    message1.set_shadow()

    message2 = OpenSignCanvas()
    message2.add_font(
        "comic", "/usr/share/fonts/truetype/msttcorefonts/Comic_Sans_MS.ttf", 14
    )
    message2.set_stroke(1, (0, 0, 0))
    message2.add_image("logo.png")
    message2.add_text("Maker Melissa's Lab", color=(255, 255, 0), y_offset=-2)
    message2.set_shadow()

    message3 = OpenSignCanvas()
    message3.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message3.set_stroke(1, (0, 0, 0))
    message3.add_text("https://makermelissa.com/", color=(255, 0, 0))

    message4 = OpenSignCanvas()
    message4.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message4.set_stroke(1, (0, 0, 0))
    message4.add_text("Subscribe to my Channel", color=(255, 255, 255))
    message4.set_shadow()

    sign = OpenSign(chain=6)
    sign.set_background_image("background.jpg")

    while True:
        sign.scroll_in_from_left(message1)
        time.sleep(1)
        message1.clear()
        message1.add_text("Change Messages")
        sign.show(message1)
        time.sleep(1)
        message1.clear()
        message1.add_text("And Scroll Out")
        sign.show(message1)
        sign.scroll_out_to_right(message1)
        time.sleep(1)

        sign.join_in_vertically(message1)
        sign.loop_left(message1)
        sign.flash(message1, count=3)
        sign.split_out_vertically(message1)
        time.sleep(1)
        sign.set_background_color((0, 255, 0))
        sign.fade_in(message2)
        time.sleep(1)
        sign.fade_out(message2)
        sign.scroll_in_from_top(message3)
        time.sleep(1)
        sign.scroll_out_to_bottom(message3)
        sign.scroll_in_from_right(message4)
        time.sleep(1)


# Main function
if __name__ == "__main__":
    main()
