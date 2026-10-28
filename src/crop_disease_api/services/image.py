"""
Image service module.

This file contains the lower-level logic for handling uploaded images.
It is responsible for validating the file, resizing it when needed, and saving it to disk.

Main flow:
Step 1: check the content type and file size
Step 2: confirm the file is a readable image
Step 3: resize oversize images while keeping proportions
Step 4: save the processed file to the uploads folder
"""

import io
import os
from typing import Any

from PIL import Image

# Allowed content types for this API.
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]

# Maximum width or height allowed for a processed image.
MAX_IMAGE_DIMENSION = 2048


def validate_image(content: bytes, content_type: str) -> dict[str, Any]:
    """
    Step 1: Validate the incoming image file.

    What it does:
    - checks whether the upload is actually an image
    - ensures the type is allowed
    - ensures the file is not too large
    - confirms the bytes can be opened by Pillow

    How it does:
    - inspects the content_type header
    - measures the file size in megabytes
    - uses Image.open() and image.verify() to validate the image data
    """
    if not content_type or not content_type.startswith("image/"):
        return {
            "is_valid": False,
            "message": "Invalid file type",
        }

    if content_type not in ALLOWED_IMAGE_TYPES:
        return {
            "is_valid": False,
            "message": "Image type not allowed",
        }

    # Convert bytes to MB so the file size can be checked using a human-friendly limit.
    size_mb = len(content) / 1024 / 1024
    if size_mb > 15:
        return {
            "is_valid": False,
            "message": "Image size exceeded limit (15MB)",
        }

    try:
        # Pillow opens the image from memory instead of reading a file on disk.
        image = Image.open(io.BytesIO(content))
        image.verify()

        # Open the image again because verify() closes the image object.
        image = Image.open(io.BytesIO(content))
        width, height = image.size
    except Exception:
        return {
            "is_valid": False,
            "message": "Corrupted or unsupported image file",
        }

    return {
        "is_valid": True,
        "message": "Image is valid",
        "width": width,
        "height": height,
        "size_mb": size_mb,
    }


def resize_image(content: bytes) -> bytes:
    """
    Step 2: Resize large images to keep storage and processing efficient.

    What it does:
    - checks the current width and height
    - shrinks images that exceed the allowed maximum size
    - preserves the original aspect ratio as much as possible

    How it does:
    - calculates the new width or height proportionally
    - uses Pillow resize() with a resampling filter
    - writes the resized image into a memory buffer
    """
    image = Image.open(io.BytesIO(content))
    width, height = image.size

    # If the image already fits inside the target limits, do nothing.
    if width <= MAX_IMAGE_DIMENSION and height <= MAX_IMAGE_DIMENSION:
        return content

    # Scale the image proportionally so it stays visually balanced.
    if width > height:
        new_width = MAX_IMAGE_DIMENSION
        new_height = max(1, int(height * (new_width / width)))
    else:
        new_height = MAX_IMAGE_DIMENSION
        new_width = max(1, int(width * (new_height / height)))

    # LANCZOS gives better quality than a rough resize.
    resample = Image.Resampling.LANCZOS
    resized_image = image.resize((new_width, new_height), resample)

    # Save the resized image to memory and return its bytes.
    output = io.BytesIO()
    resized_image.save(output, format=image.format or "PNG")
    return output.getvalue()


def save_image(content: bytes, upload_path: str, filename: str) -> str:
    """
    Step 3: Save the processed file to disk.

    What it does:
    - creates the upload directory if it does not exist
    - writes the processed image bytes to a file
    - returns the final saved path

    How it does:
    - uses os.makedirs() for folder creation
    - writes in binary mode with open(..., "wb")
    """
    # Make sure the uploads folder exists before writing any files.
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, filename)

    # Write the binary image data to disk.
    with open(file_path, "wb") as file:
        file.write(content)

    return file_path
