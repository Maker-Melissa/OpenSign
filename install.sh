#!/bin/bash
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

#
# OpenSign installer
#
# Sets up OpenSign in a Python virtual environment, builds the Henner Zeller
# RGB LED Matrix Python bindings into that same venv, and (optionally)
# installs a systemd service so the sign starts on boot.
#
# Run from the root of a checked-out OpenSign repo:
#
#     ./install.sh
#
# Re-running is safe (idempotent).

set -e

# --- Configuration (override by exporting before running) -------------------
OPENSIGN_USER="${OPENSIGN_USER:-$(whoami)}"
OPENSIGN_HOME="${OPENSIGN_HOME:-$HOME}"
OPENSIGN_VENV="${OPENSIGN_VENV:-${OPENSIGN_HOME}/opensign-venv}"
OPENSIGN_SCRIPT="${OPENSIGN_SCRIPT:-${OPENSIGN_HOME}/startup.py}"
MATRIX_SRC="${MATRIX_SRC:-${OPENSIGN_HOME}/rpi-rgb-led-matrix}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "OpenSign installer"
echo "  user        : ${OPENSIGN_USER}"
echo "  venv        : ${OPENSIGN_VENV}"
echo "  startup     : ${OPENSIGN_SCRIPT}"
echo "  matrix src  : ${MATRIX_SRC}"
echo

if [ "$(id -u)" -eq 0 ]; then
    echo "Please run this script as a normal user (not root)."
    echo "It will call sudo only where it needs to."
    exit 1
fi

# --- System dependencies ----------------------------------------------------
echo "==> Installing system dependencies (apt)"
sudo apt-get update
sudo apt-get install -y \
    git python3-dev python3-pip python3-venv \
    libatlas-base-dev libtiff-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev \
    tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev

echo "==> Installing fonts"
# msttcorefonts (Comic Sans etc.) needs contrib + EULA acceptance.
sudo apt-get install -y fonts-dejavu fonts-noto || true
sudo apt-get install -y ttf-mscorefonts-installer || \
    echo "    (skipping ttf-mscorefonts-installer - enable 'contrib' if you need MS fonts)"

# --- Virtual environment ----------------------------------------------------
echo "==> Creating virtual environment at ${OPENSIGN_VENV}"
if [ ! -d "${OPENSIGN_VENV}" ]; then
    python3 -m venv "${OPENSIGN_VENV}"
fi
# shellcheck disable=SC1091
source "${OPENSIGN_VENV}/bin/activate"
pip install --upgrade pip wheel

# --- RGB LED Matrix Python bindings -----------------------------------------
echo "==> Building Henner Zeller RGB LED Matrix Python bindings"
if [ ! -d "${MATRIX_SRC}" ]; then
    git clone https://github.com/hzeller/rpi-rgb-led-matrix "${MATRIX_SRC}"
fi
# Build/install into the *active venv* so rgbmatrix lives alongside opensign.
make -C "${MATRIX_SRC}/bindings/python" build-python PYTHON="$(which python3)"
make -C "${MATRIX_SRC}/bindings/python" install-python PYTHON="$(which python3)"

# --- OpenSign ----------------------------------------------------------------
echo "==> Installing OpenSign into the venv"
# OpenSign uses setuptools_scm, which needs git tags to derive its version.
# If this isn't a git checkout with tags (e.g. a downloaded zip), fall back to
# a pretend version so the install still succeeds.
if ! git -C "${REPO_DIR}" describe --tags >/dev/null 2>&1; then
    echo "    (no git tags found - using a fallback version)"
    export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OPENSIGN="0.0.0+local"
fi
pip install "${REPO_DIR}"

echo
echo "OpenSign installed into ${OPENSIGN_VENV}"
echo

# --- Optional systemd service -----------------------------------------------
read -r -p "Install systemd service to start OpenSign on boot? [y/N] " ans
if [[ "${ans}" =~ ^[Yy]$ ]]; then
    "${REPO_DIR}/install-service.sh"
else
    echo "Skipping service install. You can run it later with:"
    echo "    ./install-service.sh"
fi

echo
echo "Done. Test your sign by running:"
echo "    sudo ${OPENSIGN_VENV}/bin/python ${OPENSIGN_SCRIPT}"
