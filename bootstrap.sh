#!/usr/bin/env bash
set -e

echo "=== Installing Dependencies ==="

python3 -m pip install --upgrade pip

python3 -m pip install \
    deepnote-cli \
    python-dotenv \
    requests \
    pandas \
    pyyaml \
    ipykernel

echo "=== Installation complete ==="
