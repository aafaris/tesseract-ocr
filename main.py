from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
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
    "default": {"psm": "6", "oem": "3", "preprocess": False},
    "ui": {"psm": "11", "oem": "3", "preprocess": True},
    "document": {"psm": "6", "oem": "3", "preprocess": False},
}

CONF_THRESHOLD = 40


def upscale_image(image: Image.Image, scale: int = 2) -> Image.Image:
    return image.resize(
        (image.width * scale, image.height * scale),
        Image.BICUBIC
    )


def preprocess_image(image: Image.Image) -> np.ndarray:
    img = np.array(image.convert("RGB"))

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # slight blur helps reduce noise
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # adaptive threshold (MUCH better for UI)
    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

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
    mode: str = "default",
    _: str = Depends(verify_api_key)  # auth handled here
):
    logger.info(f"OCR request: file={file.filename}, mode={mode}")

    if mode not in PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {mode}. Available: {list(PRESETS.keys())}",
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        contents = await file.read()

        # Normalize image
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Upscale for better OCR accuracy
        image = upscale_image(image)

        preset = PRESETS[mode]

        # Preprocess if needed
        if preset["preprocess"]:
            processed = preprocess_image(image)
            processed_image = Image.fromarray(processed)
        else:
            processed_image = image

        config = f"--oem {preset['oem']} --psm {preset['psm']}"

        # Single OCR call (data only)
        data = image_to_data(processed_image, output_type=Output.DICT, config=config)

        words = []
        for i in range(len(data["text"])):
            text = data["text"][i].strip()
            conf = float(data["conf"][i])

            if text and conf > CONF_THRESHOLD:
                words.append(
                    {
                        "text": text,
                        "confidence": conf,
                        "bbox": {
                            "x": data["left"][i],
                            "y": data["top"][i],
                            "width": data["width"][i],
                            "height": data["height"][i],
                        },
                    }
                )

        # Reconstruct text from words
        full_text = " ".join(w["text"] for w in words)

        avg_conf = (
            sum(w["confidence"] for w in words) / len(words)
            if words else 0
        )

        logger.info(
            f"OCR completed: mode={mode}, words={len(words)}, avg_confidence={avg_conf:.2f}"
        )

        return {
            "text": full_text,
            "mode": mode,
            "config": config,
            "preprocess": preset["preprocess"],
            "words": words,
            "stats": {
                "total_words": len(words),
                "avg_confidence": avg_conf,
            },
        }

    except Exception as e:
        logger.exception(f"OCR failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))