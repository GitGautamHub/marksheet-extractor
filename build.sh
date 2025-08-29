#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies for Poppler
sudo apt-get update && sudo apt-get install -y poppler-utils