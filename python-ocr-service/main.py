from fastapi import FastAPI, UploadFile, File
from ocr_service import extract_marksheet
import tempfile
import os

app = FastAPI(
    title="OCR",
    description="PaddleOCR"
)

@app.get("/")
def root():
    return {
        "message": "OCR Service is running"
    }

@app.post("/ocr")
async def process_ocr(file: UploadFile = File(...)):
    # Create temporary file
    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name


    try:
        # Send image to our OCR service
        result = extract_marksheet(temp_path)
        return result
    
    finally:
        # Delete temporary image
        if os.path.exists(temp_path):
            os.remove(temp_path)