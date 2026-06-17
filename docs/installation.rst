Raspberry Pi Setup
===================
Start by download Raspberry Pi OS Lite from https://www.raspberrypi.org/downloads/raspberry-pi-os/. Once it is done downloading, flash the image onto a Micro SD card using a program such as `balenaEtcher <https://www.balena.io/etcher/>`_.

Mount the SD card on a computer and create an empty file named "ssh" inside the boot partition. If you only have a WiFi networking, you'll want to create a wpa_supplicant.conf file as well following `these instructions <https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md>`_. Otherwise, you can wait a bit and use raspi-config to do it the easy way.

Eject the card from your computer and insert the card into the Raspberry Pi.

If you didn't set up WiFi already, be sure the Raspberry Pi is plugged into your network.

Plug in power and let the Raspberry Pi boot.

Wait for a few minutes and then SSH into the Raspberry Pi using an SSH client such as PuTTY for windows or command line SSH on macOS or Linux.

Start raspi-config::

    sudo raspi-config

You can change your password by going to ``System Options`` > ``Password``, which is recommended for security if necessary.

If you haven't already and want to enable WiFi, you can do so now by choosing ``System Options`` > ``Wireless LAN`` and follow the prompts.

Be sure to set your Timezone by going to ``Localisation Options`` > ``Change Timezone``.

If you would like to change your hostname so that it doesn't conflict with any other Raspberry Pi, you can do so by choosing ``System Options`` > ``Hostname``.

After that you can exit the utility.


Package Updates
================
Next, you'll want to perform an update with the following commands::

    sudo apt update
    sudo apt upgrade


Configure the RGB Matrix HAT/Bonnet
===================================
If you are using an Adafruit RGB Matrix HAT or Bonnet, run Adafruit's matrix
setup script first. It configures the sound blacklist and CPU isolation the
matrix library needs for a clean, flicker-free image::

    curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh >rgb-matrix.sh
    sudo bash rgb-matrix.sh

Reboot when it asks you to.


Quick Install
=============
The easiest way to install OpenSign is with the included installer. Clone the
repository and run it::

    git clone https://github.com/Maker-Melissa/PyOpenSign
    cd PyOpenSign
    ./install.sh

The installer will:

* install the required apt packages and fonts,
* create a Python virtual environment (``~/opensign-venv`` by default),
* build the Henner Zeller RGB LED Matrix Python bindings into that venv,
* install OpenSign into the venv, and
* optionally install a systemd service so the sign starts on boot.

You can override the defaults by exporting variables before running it, for
example to use a different venv or startup script location::

    OPENSIGN_VENV=/home/pi/myvenv OPENSIGN_SCRIPT=/home/pi/mysign.py ./install.sh

When it finishes, test your sign by running your script with the venv's
Python::

    sudo ~/opensign-venv/bin/python ~/startup.py


Manual Install
==============
If you would rather install everything by hand, the steps the installer runs
are below.

Install the dependencies and fonts::

    sudo apt install -y git python3-dev python3-pip python3-venv libatlas-base-dev libtiff-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk libharfbuzz-dev libfribidi-dev libxcb1-dev
    sudo apt install -y fonts-dejavu fonts-noto ttf-mscorefonts-installer

Create and activate a virtual environment::

    python3 -m venv ~/opensign-venv
    source ~/opensign-venv/bin/activate

Build the Henner Zeller RPi RGB LED Matrix Python Bindings **into the venv**
(activate it first so ``rgbmatrix`` installs alongside OpenSign)::

    git clone https://github.com/hzeller/rpi-rgb-led-matrix
    cd rpi-rgb-led-matrix/bindings/python
    make build-python PYTHON=$(which python3)
    make install-python PYTHON=$(which python3)

Install OpenSign into the venv::

    pip3 install pyopensign


Automatically Start on Boot
============================
The installer can set up a systemd service for you. To install (or reinstall)
it separately, run::

    ./install-service.sh

This installs a service that runs your startup script with the venv's Python
as root (the matrix library needs root for GPIO). The venv and script paths
are read from ``/etc/opensign/opensign.conf``::

    OPENSIGN_VENV=/home/pi/opensign-venv
    OPENSIGN_SCRIPT=/home/pi/startup.py

.. warning::
    If you are using any images in your script, be sure to use absolute paths because the service is not run from your home folder.

Manage the service with the usual ``systemctl`` commands::

    sudo systemctl start opensign      # start now
    sudo systemctl status opensign     # check status
    sudo systemctl restart opensign    # restart after editing the config or script
    journalctl -u opensign -f          # follow the logs

After editing ``/etc/opensign/opensign.conf`` (or your startup script), run
``sudo systemctl restart opensign`` to apply the change. The service is
enabled on install, so it will come up automatically after a reboot.
