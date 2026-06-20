Introduction
============

.. image:: https://readthedocs.org/projects/pyopensign/badge/?version=latest
    :target: https://pyopensign.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/Maker-Melissa/PyOpenSign/workflows/Build%20CI/badge.svg
    :target: https://github.com/Maker-Melissa/PyOpenSign/actions
    :alt: Build Status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

A library to facilitate easy RGB Matrix Sign Animations.

Simple v2 API
=============

PyOpenSign 2.0 centers around a sign-managed ``Message`` and a single animation
dispatcher. Message contents stay in place until you explicitly alter them with
``clear()``, ``add_text()``, or ``add_image()``. When contents change, the
message is automatically readjusted on the sign:

.. code-block:: python

    from opensign import OpenSign

    sign = OpenSign(chain=6)
    sign.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

    sign.add_text(
        "Hello World!",
        font="dejavu",
        color="crimson",
    )
    sign.scroll_in(dir_from="right")
    sign.wipe_out(dir_to="left")

    sign.clear()
    sign.add_text("Hello again", font="dejavu")
    sign.fade_in()
    sign.fade_out()

When Python code needs direct control over message content, edit
``sign.message`` and then animate without passing text:

.. code-block:: python

    from opensign import OpenSign

    sign = OpenSign(chain=6)
    sign.add_text("Hello ", color="#ffcc00")
    sign.add_text("World!", color="lime")
    sign.animate("Scroll", "in_from_left", duration=2)

Animation plugins live in ``opensign/animations``. Each plugin is discovered
from its module name, so adding ``opensign/animations/wipe.py`` with a ``Wipe``
class makes ``sign.animate("Wipe", "method_name")`` available without
editing a central animation dictionary.

Advanced Canvases
=================

For layered effects, create additional persistent canvases. Each canvas keeps
its own content, opacity, and position:

.. code-block:: python

    from opensign import DEFAULT

    default_canvas = sign.get_canvas(DEFAULT)
    front = sign.create_canvas("front")

    sign.add_text("Back", color="red")
    front.add_text("Front", color="blue")

    default_canvas.opacity = 0.5
    front.opacity = 0.5
    front.position = default_canvas.position

    sign.draw_canvases(default_canvas, front)

Animations can also target a named canvas:

.. code-block:: python

    sign.scroll_in(canvas="front", dir_from="right")

YAML Scripts
============

PyOpenSign can run simple YAML scripts with the ``osscript`` command:

.. code-block:: shell

    osscript examples/multiple_canvases.yml

Scripts use top-level setup sections and ordered steps:

.. code-block:: yaml

    sign:
      chain: 6
      slowdown_gpio: 5
      background_image: background.jpg

    fonts:
      dejavu:
        file: /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
        size: 14

    canvases:
      front: {}

    repeat: forever

    steps:
      - clear: default
      - clear: front
      - add_text:
          text: Back
          font: dejavu
          color: red
      - add_text:
          canvas: front
          text: Front
          font: dejavu
          color: blue
      - set_canvas:
          canvas: front
          opacity: 0.5
          position: default
      - draw_canvases: [default, front]
      - sleep: 1
      - scroll_in:
          canvas: front
          dir_from: left

Dependencies
=============
This library depends on:

* `Henner Zeller RPi RGB LED Matrix <https://github.com/hzeller/rpi-rgb-led-matrix/>`_
* `Python Bindings for RGB Matrix Library <https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python>`_
* `Python Imaging Library (Pillow) <https://pypi.org/project/Pillow/>`_

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/pyopensign/>`_. To install for current user:

.. code-block:: shell

    pip3 install pyopensign

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install pyopensign

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install pyopensign

Running on a Raspberry Pi 4
============================

On the Raspberry Pi 4, the processor is faster than the GPIOs are able to handle. This results in some "glitchiness" in the animantions.
To help mitigate this, you can pass the ``slowdown_gpio`` parameter to the OpenSign constructor. This will slow down the GPIO clock to a more manageable speed.

A value of 5 is a good starting point, but you may need to experiment with different values to find the best performance for your specific setup.

The tradeoff is that the animations will be slower, but they will be smoother and more reliable.

Raspberry Pi 5 doesn't have the same issues because of the different GPIO architecture, so you can omit the slowdown_gpio parameter when running on a Raspberry Pi 5.
