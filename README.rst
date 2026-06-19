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

PyOpenSign 2.0 centers around ``Message`` objects and a single animation
dispatcher. You can still build reusable messages manually:

.. code-block:: python

    from opensign import Message, OpenSign

    sign = OpenSign(chain=6)
    sign.add_font("dejavu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

    message = Message(
        "Hello World!",
        font=sign.fonts.get("dejavu"),
        color="crimson",
        opacity=0.8,
    )

    sign.animate(message, "Scroll", "in_from_left", duration=2)

For quick scripts, pass text directly and let PyOpenSign create the temporary
message:

.. code-block:: python

    sign.scroll_in("Hello World!", dir_from="right", color="#ffcc00", font="dejavu")
    sign.wipe_out(dir_to="left")
    sign.fade_in("Hello again", font="dejavu")
    sign.fade_out()

Animation plugins live in ``opensign/animations``. Each plugin is discovered
from its module name, so adding ``opensign/animations/wipe.py`` with a ``Wipe``
class makes ``sign.animate(message, "Wipe", "method_name")`` available without
editing a central animation dictionary.

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
