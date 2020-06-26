Introduction
============

.. image:: https://readthedocs.org/projects/opensign/badge/?version=latest
    :target: https://opensign.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/makermelissa/OpenSign/workflows/Build%20CI/badge.svg
    :target: https://github.com/makermelissa/OpenSign/actions
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

A library to facilitate easy RGB Matrix Sign Animations.


Dependencies
=============
This library depends on:

* `Henner Zeller RPi RGB LED Matrix <https://github.com/hzeller/rpi-rgb-led-matrix/>`_
* `Python Bindings for RGB Matrix Library <https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python>`_
* `Python Imaging Library (Pillow) <https://pypi.org/project/Pillow/>`_

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/opensign/>`_. To install for current user:

.. code-block:: shell

    pip3 install opensign

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install opensign

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install opensign
