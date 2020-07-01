#!/usr/bin/env python
from opensign import OpenSign, OpenSignCanvas

"""
Script
Scroll in text
an images
Fade text in
and fade out



"""


def main():
    message1 = OpenSignCanvas()
    message1.add_font(
        "dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14
    )
    message1.set_stroke(1, (255, 255, 255))
    message1.add_text("Black Lives Matter", color=(0, 255, 0))

    message2 = OpenSignCanvas()
    message2.add_font(
        "dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14
    )
    message2.set_stroke(1, (0, 0, 0))
    message2.add_text("Wear a Mask", color=(255, 0, 0))

    message3 = OpenSignCanvas()
    message3.add_font(
        "comic", "/usr/share/fonts/truetype/msttcorefonts/Comic_Sans_MS.ttf", 14
    )
    message3.set_stroke(1, (0, 0, 0))
    message3.add_image("logo.png")
    message3.add_text("Maker Melissa's Lab", color=(255, 255, 0), y_offset=-2)
    message3.set_shadow()

    message4 = OpenSignCanvas()
    message4.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    message4.set_stroke(1, (0, 0, 0))
    message4.add_text("Like, Share, and Subscribe", color=(255, 255, 255))
    message4.set_shadow()

    circuit_image = "background.jpg"
    sign = OpenSign(chain=6)

    while True:
        sign.set_background_color((0, 0, 0))
        sign.scroll_in_from_left(message1)
        sign.sleep(1)
        sign.scroll_out_to_right(message1)
        sign.scroll_in_from_top(message2)
        sign.sleep(1)
        sign.scroll_out_to_bottom(message2)
        sign.set_background_image(circuit_image)
        sign.join_in_vertically(message3)
        sign.sleep(1)
        sign.fade_out(message3)
        sign.join_in_horizontally(message4)
        sign.flash(message4, duration=2)
        sign.split_out_vertically(message4)
        sign.sleep(0.5)


# Main function
if __name__ == "__main__":
    main()
