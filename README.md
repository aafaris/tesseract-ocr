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

## API Usage

**Endpoint:** `POST /ocr`

Upload an image file to extract text:
```bash
curl -X POST -F "file=@image.png" http://localhost:8000/ocr
```

The API documentation is also available at `http://localhost:8000/docs