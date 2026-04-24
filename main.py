from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from pytesseract import image_to_string, image_to_data, Output
from PIL import Image
from dotenv import load_dotenv
import io
import logging
import cv2
import numpy as np
import os
from typing import Optional

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ocr-api")

API_KEY = os.getenv("API_KEY", "")


def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

app = FastAPI()

PRESETS = {
    "default": {"psm": "3", "oem": "3", "preprocess": True},
    "ui": {"psm": "11", "oem": "3", "preprocess": True},
    "document": {"psm": "6", "oem": "3", "preprocess": False},
}


def preprocess_image(image: Image.Image) -> np.ndarray:
    img = np.array(image)
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return thresh


@app.get("/")
async def root():
    return {
        "message": "Tesseract OCR API",
        "endpoints": {
            "POST /ocr": "Extract text from image",
            "GET /presets": "Get available OCR presets",
        },
    }


@app.get("/presets")
async def get_presets():
    return PRESETS


@app.post("/ocr")
async def perform_ocr(
    file: UploadFile = File(...),
    x_api_key: str = Header(None),
    mode: str = "default",
):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    logger.info(f"OCR request: file={file.filename}, mode={mode}")

    if mode not in PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {mode}. Available: {list(PRESETS.keys())}",
        )

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        preset = PRESETS[mode]
        if preset["preprocess"]:
            processed = preprocess_image(image)
            processed_image = Image.fromarray(processed)
        else:
            processed_image = image

        config = f"--oem {preset['oem']} --psm {preset['psm']}"
        text = image_to_string(processed_image, config=config)

        data = image_to_data(processed_image, output_type=Output.DICT)

        words = []
        for i in range(len(data["text"])):
            if data["text"][i].strip():
                words.append(
                    {
                        "text": data["text"][i],
                        "confidence": float(data["conf"][i]),
                        "bbox": {
                            "x": data["left"][i],
                            "y": data["top"][i],
                            "width": data["width"][i],
                            "height": data["height"][i],
                        },
                    }
                )

        return {
            "text": text,
            "mode": mode,
            "config": config,
            "preprocess": preset["preprocess"],
            "words": words,
            "stats": {
                "total_words": len(words),
                "avg_confidence": (
                    sum(w["confidence"] for w in words) / len(words) if words else 0
                ),
            },
        }
    except Exception as e:
        logger.exception(f"OCR failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    logger.info(f"OCR completed: mode={mode}, words={len(words)}, avg_confidence={stats['avg_confidence']:.2f}")