#!/usr/bin/env python
from opensign import OpenSign, OpenSignCanvas


def main():
    sign = OpenSign(chain=6)

    canvas2 = OpenSignCanvas()
    canvas2.add_font("default", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    canvas2.add_font(
        "comic",
        "/usr/share/fonts/truetype/msttcorefonts/Comic_Sans_MS.ttf",
        14,
        use=True,
    )
    canvas2.set_stroke(1, (0, 0, 0))
    # canvas2.add_image("logo.png")
    canvas2.add_text("https://makermelissa.com", color=(0, 255, 0), font="default")
    canvas2.set_shadow()

    sign = OpenSign(chain=6)
    sign.set_background_image("background.jpg")
    sign.scroll_in_from_top(canvas2)
    sign.sleep(30)


# Main function
if __name__ == "__main__":
    main()
