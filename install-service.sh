#!/bin/bash
# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

#
# Install (or update) the OpenSign systemd service.
#
# Reads the same overridable variables as install.sh so the service points
# at the right venv and startup script:
#
#     OPENSIGN_VENV    (default: $HOME/opensign-venv)
#     OPENSIGN_SCRIPT  (default: $HOME/startup.py)
#
# Run from a checked-out OpenSign repo:
#
#     ./install-service.sh

set -e

OPENSIGN_HOME="${OPENSIGN_HOME:-$HOME}"
OPENSIGN_VENV="${OPENSIGN_VENV:-${OPENSIGN_HOME}/opensign-venv}"
OPENSIGN_SCRIPT="${OPENSIGN_SCRIPT:-${OPENSIGN_HOME}/startup.py}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CONF_DIR="/etc/opensign"
CONF_FILE="${CONF_DIR}/opensign.conf"
UNIT_FILE="/etc/systemd/system/opensign.service"

echo "==> Installing OpenSign systemd service"
echo "    venv   : ${OPENSIGN_VENV}"
echo "    script : ${OPENSIGN_SCRIPT}"

# --- Config file (don't clobber an existing edited one) ---------------------
sudo mkdir -p "${CONF_DIR}"
if [ -f "${CONF_FILE}" ]; then
    echo "    ${CONF_FILE} already exists - leaving it untouched."
else
    echo "    Writing ${CONF_FILE}"
    sudo tee "${CONF_FILE}" >/dev/null <<EOF
# OpenSign service configuration
# Edit these paths, then apply with: sudo systemctl restart opensign
OPENSIGN_VENV=${OPENSIGN_VENV}
OPENSIGN_SCRIPT=${OPENSIGN_SCRIPT}
EOF
fi

# --- Unit file --------------------------------------------------------------
# systemd needs an absolute path for the ExecStart executable (it won't expand
# an env var for the binary), so bake the venv interpreter into the unit. The
# script path stays configurable through OPENSIGN_SCRIPT in the config file.
VENV_PYTHON="${OPENSIGN_VENV}/bin/python"
echo "    Installing ${UNIT_FILE} (python: ${VENV_PYTHON})"
sudo sed "s|__VENV_PYTHON__|${VENV_PYTHON}|g" \
    "${REPO_DIR}/service/opensign.service" | sudo tee "${UNIT_FILE}" >/dev/null

# --- Enable + start ---------------------------------------------------------
sudo systemctl daemon-reload
sudo systemctl enable opensign.service

echo
echo "Service installed and enabled. Start it now with:"
echo "    sudo systemctl start opensign"
echo
echo "Useful commands:"
echo "    sudo systemctl status opensign     # check status"
echo "    sudo systemctl restart opensign    # restart after editing config/script"
echo "    journalctl -u opensign -f          # follow logs"
echo "    sudo nano ${CONF_FILE}             # change venv / script paths"
