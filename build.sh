#!/usr/bin/env bash
set -o errexit  # exit on error

echo "Updating packages..."
apt-get update

echo "Installing Tesseract OCR..."
apt-get install -y tesseract-ocr

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"