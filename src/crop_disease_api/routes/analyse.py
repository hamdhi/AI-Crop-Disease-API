"""
Analyse route module.

This file handles the image upload endpoint for the crop disease API.
It separates the route layer from the lower-level image processing logic so the project is easier to understand and maintain.

Main flow:
Step 1: create the router with a /analyse prefix
Step 2: accept the uploaded file from the client
Step 3: validate the file and image content
Step 4: resize and save the image
Step 5: return useful metadata to the client
"""

import uuid
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..services.image import resize_image, save_image, validate_image

# Step 1: Create the route group for this feature.
# The prefix /analyse makes the endpoint easier to organize and understand.
router = APIRouter(
    prefix="/analyse",
    tags=["analyse"],
)


async def process_single_image(file: UploadFile) -> dict[str, Any]:
    """
    Step 2: Process one uploaded image.

    What it does:
    - reads the uploaded file bytes
    - checks whether the file is valid
    - resizes the image if needed
    - saves it to the uploads folder
    - returns image information to the client

    How it does:
    - uses file.read() to read raw bytes
    - calls validation logic from the service layer
    - reuses a helper function to resize and save the file
    """
    if file.content_type is None:
        raise HTTPException(status_code=400, detail="Missing file content type")

    # Read the raw file bytes from the HTTP request.
    content = await file.read()

    # Validate the file before applying any processing.
    # If validation fails, stop immediately and return a 400 error.
    validation = validate_image(content, file.content_type)
    if not validation["is_valid"]:
        raise HTTPException(status_code=400, detail=validation["message"])

    # Resize the image only after it passes validation.
    # This keeps the image size manageable and safe for storage.
    processed_content = resize_image(content)

    # Create a safe filename.
    # We use the original extension if present, otherwise we use jpg.
    filename = file.filename or "upload.jpg"
    extension = filename.rsplit(".", 1)[1].lower() if "." in filename else "jpg"
    unique_filename = f"{uuid.uuid4().hex}.{extension}"

    # Save the processed file to the uploads directory.
    # The function returns the file path that was saved on disk.
    saved_path = save_image(processed_content, upload_path="uploads", filename=unique_filename)

    # Return metadata to the client so they can confirm what was processed.
    return {
        "is_valid": validation["is_valid"],
        "message": validation["message"],
        "width": validation["width"],
        "height": validation["height"],
        "size_mb": validation["size_mb"],
        "image_path": saved_path,
    }


@router.post("/")
async def analyse_image(file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Step 3: Upload endpoint for one image.

    What it does:
    - accepts an uploaded file from the client
    - checks the MIME type
    - sends the file to the processing function

    How it does:
    - uses FastAPI's UploadFile and File(...) to receive multipart form data
    - validates the content type before processing begins
    """
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Pass the file into the real processing flow.
    return await process_single_image(file)

    