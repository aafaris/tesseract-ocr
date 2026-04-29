# Tesseract OCR API

A FastAPI-based OCR web service that extracts text from images using Tesseract OCR.

## What This Repo Does

This is a simple REST API that accepts image uploads and returns extracted text using the Tesseract OCR engine. Built with FastAPI and pytesseract.

## Prerequisites

- Python 3.12+
- Tesseract OCR installed on the system
  - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
  - Linux: `sudo apt install tesseract-ocr`
  - macOS: `brew install tesseract`

## Setup

1. Create and activate the virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Environment Variables

Set the following environment variables for authentication:

- `BASIC_AUTH_USERNAME`: Username for Basic Auth (default: `admin`)
- `BASIC_AUTH_PASSWORD`: Password for Basic Auth

## API Usage

**Endpoint:** `POST /ocr`

Send binary image data to extract text using the "document" preset:

```bash
curl -X POST http://localhost:8000/ocr \
  -u username:password \
  -H "Content-Type: image/png" \
  --data-binary "@image.png"
```

The API documentation is also available at `http://localhost:8000/docs`