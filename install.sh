#!/bin/bash
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

#
# PyOpenSign installer
#
# Self-contained installer for PyOpenSign on Raspberry Pi OS (Bookworm or
# Trixie). Configures the hardware (audio off, snd_bcm2835 blacklist, isolcpus,
# optional quality-mod overlay), builds the Henner Zeller RGB LED Matrix Python
# bindings into a venv, installs PyOpenSign, and (optionally) installs a
# systemd service so the sign starts on boot.
#
# Run from the root of a checked-out PyOpenSign repo:
#
#     ./install.sh
#
# Re-running is safe.

set -e

# --- Configuration (override by exporting before running) -------------------
OPENSIGN_USER="${OPENSIGN_USER:-$(whoami)}"
OPENSIGN_HOME="${OPENSIGN_HOME:-$HOME}"
OPENSIGN_VENV="${OPENSIGN_VENV:-${OPENSIGN_HOME}/opensign-venv}"
OPENSIGN_SCRIPT="${OPENSIGN_SCRIPT:-${OPENSIGN_HOME}/startup.py}"
MATRIX_SRC="${MATRIX_SRC:-${OPENSIGN_HOME}/rpi-rgb-led-matrix}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Boot config paths: Trixie+Bookworm-current use /boot/firmware, legacy is /boot.
if [ -d /boot/firmware ]; then
    BOOT_DIR="/boot/firmware"
else
    BOOT_DIR="/boot"
fi
CONFIG_TXT="${BOOT_DIR}/config.txt"
CMDLINE_TXT="${BOOT_DIR}/cmdline.txt"
BLACKLIST_FILE="/etc/modprobe.d/pyopensign-blacklist.conf"

# Track whether boot config changed so we can prompt for reboot at the end.
NEEDS_REBOOT=0

echo "PyOpenSign installer"
echo "  user        : ${OPENSIGN_USER}"
echo "  venv        : ${OPENSIGN_VENV}"
echo "  startup     : ${OPENSIGN_SCRIPT}"
echo "  matrix src  : ${MATRIX_SRC}"
echo "  boot dir    : ${BOOT_DIR}"
echo

if [ "$(id -u)" -eq 0 ]; then
    echo "Please run this script as a normal user (not root)."
    echo "It will call sudo only where it needs to."
    exit 1
fi

# --- Hardware prompt --------------------------------------------------------
# The quality-mod jumper (GPIO4 to GPIO18 soldered together) significantly
# reduces flicker on both the Adafruit RGB Matrix Bonnet and HAT. It's the
# single piece of info we need to set the boot config correctly.
echo "==> Hardware configuration"
read -r -p "Did you solder the quality-mod jumper (GPIO4 to GPIO18)? [Y/n] " jumper_ans
case "${jumper_ans}" in
    [Nn]*) QUALITY_MOD=0 ;;
    *)     QUALITY_MOD=1 ;;
esac
echo "    quality-mod jumper: $( [ "${QUALITY_MOD}" -eq 1 ] && echo yes || echo no )"
echo

# --- System dependencies ----------------------------------------------------
echo "==> Installing system dependencies (apt)"
sudo apt-get update
# libfreetype6-dev was renamed to libfreetype-dev on Trixie (apt auto-
# substitutes, but be explicit). libatlas-base-dev was removed in Trixie and
# is not actually needed for Pillow/PyOpenSign.
# cython3 is required by hzeller's rpi-rgb-led-matrix Python bindings.
sudo apt-get install -y \
    git python3-dev python3-pip python3-venv cython3 \
    libtiff-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype-dev liblcms2-dev libwebp-dev \
    tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev

echo "==> Installing fonts"
# msttcorefonts (Comic Sans etc.) needs contrib + EULA acceptance.
sudo apt-get install -y fonts-dejavu fonts-noto || true
sudo apt-get install -y ttf-mscorefonts-installer || \
    echo "    (skipping ttf-mscorefonts-installer - enable 'contrib' if you need MS fonts)"

# --- System / boot config ---------------------------------------------------
# The Henner Zeller matrix library needs three things from the OS for clean,
# flicker-free output:
#   1) onboard PWM audio disabled (it conflicts with matrix PWM timing)
#   2) snd_bcm2835 blacklisted (same reason; survives module reload)
#   3) one CPU core isolated from the scheduler so the refresh thread can
#      run undisturbed
# Plus optionally a pwm-pio overlay for the quality-mod jumper.
echo "==> Configuring hardware (${CONFIG_TXT}, ${CMDLINE_TXT})"

# Back up boot files once per run, with a timestamp so multiple runs don't
# clobber the original baseline.
backup_once() {
    local f="$1"
    local stamp; stamp="$(date +%Y%m%d-%H%M%S)"
    sudo cp -n "${f}" "${f}.pyopensign-bak-${stamp}" 2>/dev/null || true
}
backup_once "${CONFIG_TXT}"
backup_once "${CMDLINE_TXT}"

# (a) audio off in config.txt
if grep -qE '^[[:space:]]*dtparam=audio=on' "${CONFIG_TXT}"; then
    echo "    disabling onboard audio (dtparam=audio=off)"
    sudo sed -i 's/^[[:space:]]*dtparam=audio=on/dtparam=audio=off/' "${CONFIG_TXT}"
    NEEDS_REBOOT=1
elif ! grep -qE '^[[:space:]]*dtparam=audio=off' "${CONFIG_TXT}"; then
    echo "    adding dtparam=audio=off"
    echo 'dtparam=audio=off' | sudo tee -a "${CONFIG_TXT}" >/dev/null
    NEEDS_REBOOT=1
else
    echo "    onboard audio already disabled"
fi

# (b) snd_bcm2835 blacklist
if [ ! -f "${BLACKLIST_FILE}" ]; then
    echo "    writing ${BLACKLIST_FILE}"
    echo 'blacklist snd_bcm2835' | sudo tee "${BLACKLIST_FILE}" >/dev/null
    NEEDS_REBOOT=1
else
    echo "    snd_bcm2835 blacklist already in place"
fi

# (c) isolcpus=3 in cmdline.txt
if ! grep -q 'isolcpus=3' "${CMDLINE_TXT}"; then
    echo "    adding isolcpus=3 to ${CMDLINE_TXT}"
    sudo sed -i 's/$/ isolcpus=3/' "${CMDLINE_TXT}"
    NEEDS_REBOOT=1
else
    echo "    isolcpus=3 already present"
fi

# (d) quality-mod overlay (only if user said yes to the jumper)
if [ "${QUALITY_MOD}" -eq 1 ]; then
    if ! grep -qE '^[[:space:]]*dtoverlay=pwm-pio,gpio_pin=4,output_pin=18' "${CONFIG_TXT}"; then
        echo "    adding quality-mod overlay (pwm-pio GPIO4->GPIO18)"
        echo 'dtoverlay=pwm-pio,gpio_pin=4,output_pin=18' | sudo tee -a "${CONFIG_TXT}" >/dev/null
        NEEDS_REBOOT=1
    else
        echo "    quality-mod overlay already present"
    fi
else
    # User said they don't have the jumper; remove the overlay if a previous
    # run had added it.
    if grep -qE '^[[:space:]]*dtoverlay=pwm-pio,gpio_pin=4,output_pin=18' "${CONFIG_TXT}"; then
        echo "    removing previously-added quality-mod overlay (user said no jumper)"
        sudo sed -i '/^[[:space:]]*dtoverlay=pwm-pio,gpio_pin=4,output_pin=18/d' "${CONFIG_TXT}"
        NEEDS_REBOOT=1
    fi
fi

# --- Virtual environment ----------------------------------------------------
echo "==> Creating virtual environment at ${OPENSIGN_VENV}"
# Check pyvenv.cfg (the real venv marker), not just the directory, so a
# leftover/broken venv dir from another tool doesn't get reused.
if [ ! -f "${OPENSIGN_VENV}/pyvenv.cfg" ]; then
    if [ -d "${OPENSIGN_VENV}" ]; then
        echo "    (existing ${OPENSIGN_VENV} is not a valid venv - recreating)"
        rm -rf "${OPENSIGN_VENV}"
    fi
    python3 -m venv "${OPENSIGN_VENV}"
fi
# shellcheck disable=SC1091
source "${OPENSIGN_VENV}/bin/activate"
# Sanity-check that activation actually pointed us at the venv's python.
if [ "$(command -v python3)" != "${OPENSIGN_VENV}/bin/python3" ]; then
    echo "ERROR: venv activation did not take. Expected python3 to be"
    echo "    ${OPENSIGN_VENV}/bin/python3"
    echo "but got $(command -v python3). Aborting to avoid touching system Python."
    exit 1
fi
pip install --upgrade pip wheel

# --- RGB LED Matrix Python bindings -----------------------------------------
echo "==> Building Henner Zeller RGB LED Matrix Python bindings"
# hzeller's repo now uses a pyproject.toml at the root (no more Makefile
# build-python target). Check pyproject.toml exists; reclone if not.
if [ ! -f "${MATRIX_SRC}/pyproject.toml" ]; then
    if [ -d "${MATRIX_SRC}" ]; then
        echo "    (existing ${MATRIX_SRC} is missing pyproject.toml - recloning)"
        rm -rf "${MATRIX_SRC}"
    fi
    git clone https://github.com/hzeller/rpi-rgb-led-matrix "${MATRIX_SRC}"
fi
# Install into the *active venv* so rgbmatrix lives alongside pyopensign.
pip install "${MATRIX_SRC}"

# --- PyOpenSign --------------------------------------------------------------
echo "==> Installing PyOpenSign into the venv"
# PyOpenSign uses setuptools_scm, which needs git tags to derive its version.
# If this isn't a git checkout with tags (e.g. a downloaded zip), fall back to
# a pretend version so the install still succeeds.
if ! git -C "${REPO_DIR}" describe --tags >/dev/null 2>&1; then
    echo "    (no git tags found - using a fallback version)"
    export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYOPENSIGN="0.0.0+local"
fi
pip install "${REPO_DIR}"

echo
echo "PyOpenSign installed into ${OPENSIGN_VENV}"
echo

# --- Optional systemd service -----------------------------------------------
# Make sure install-service.sh is executable - SFTP transfers commonly strip
# the exec bit, which would otherwise abort the installer before the reboot
# prompt and leave the boot config un-applied.
chmod +x "${REPO_DIR}/install-service.sh" 2>/dev/null || true

read -r -p "Install systemd service to start PyOpenSign on boot? [y/N] " ans
if [[ "${ans}" =~ ^[Yy]$ ]]; then
    # Don't let a service install failure skip the reboot prompt below.
    "${REPO_DIR}/install-service.sh" || \
        echo "    WARNING: install-service.sh failed - continuing so the reboot prompt still runs."
else
    echo "Skipping service install. You can run it later with:"
    echo "    ./install-service.sh"
fi

echo
echo "Done. Test your sign by running:"
echo "    sudo ${OPENSIGN_VENV}/bin/python ${OPENSIGN_SCRIPT}"
echo

# --- Reboot prompt ----------------------------------------------------------
if [ "${NEEDS_REBOOT}" -eq 1 ]; then
    echo "==> Hardware configuration changed. A reboot is required to apply it."
    read -r -p "Reboot now? [Y/n] " reboot_ans
    case "${reboot_ans}" in
        [Nn]*) echo "    Skipping reboot. Run 'sudo reboot' when you're ready." ;;
        *)     echo "    Rebooting in 3 seconds..."; sleep 3; sudo reboot ;;
    esac
fi
