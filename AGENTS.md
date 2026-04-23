# AGENTS.md

## Project Overview

- **Type**: FastAPI web service
- **Purpose**: OCR API that extracts text from image uploads using Tesseract OCR
- **Main file**: `main.py`

## Key Commands

### Run the app
```bash
uvicorn main:app --reload
```

### Install dependencies
```bash
pip install -r requirements.txt
```

## Testing the API

API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Important Notes

- Requires Tesseract OCR binary installed on the system
- The venv directory is already present and should be activated before running