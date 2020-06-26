#!/usr/bin/env python
from opensign import OpenSign, OpenSignCanvas


def main():
    sign = OpenSign(chain=6)
    canvas = OpenSignCanvas()
    canvas.add_image("mml.ppm")

    while True:
        sign.loop_down(canvas, duration=2)


# Main function
if __name__ == "__main__":
    main()
