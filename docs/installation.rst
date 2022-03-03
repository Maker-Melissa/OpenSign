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


Install Dependencies
=====================
Install Python and other dependencies using this command::

    sudo apt install -y git python3-dev python3-pillow python3-pip libatlas-base-dev libtiff-dev libtiff5-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk libharfbuzz-dev libfribidi-dev libxcb1-dev


Additional Fonts
=================
Install additional fonts::

    sudo apt install -y fonts-dejavu msttcorefonts fonts-noto


RGB LED Matrix Python bindings
===============================
Install the Henner Zeller RPi RGB LED Matrix Python Bindings::

    git clone https://github.com/hzeller/rpi-rgb-led-matrix
    cd rpi-rgb-led-matrix/bindings/python
    make build-python PYTHON=$(which python3)
    sudo make install-python PYTHON=$(which python3)

Install OpenSign
=================
Install OpenSign via PyPI::

    sudo pip3 install opensign


Automatically Start on Boot
============================
To automatically start a python script on boot, the easiest way is to put it in **/etc/rc.local**

.. warning::
    If you are using any images in your script, be sure to use absolute paths because the script is not run from your home folder.

.. warning::
    Verify your script is working before doing this by running it from the command line first. If there are any bugs, it just won't start. You can check the specific errors by running ``systemctl status rc.local.service``.

Edit the file using::

    sudo nano /etc/rc.local

Insert a new line right before ``exit 0``

Assuming your username is pi and your script is in your home directory and called startup.py, the new line should be::

    sudo python3 /home/pi/startup.py &

Save, exit, and reboot. Your sign should come to life.
