"""
Crop disease API package.

Step 1: This file creates the FastAPI application instance.
Step 2: It imports the route file where the upload logic is defined.
Step 3: It exposes a health endpoint so the API can be checked easily.
Step 4: It contains the run function used to start the server.

Why this file matters:
- It is the entry point for the API.
- It connects the app to route files.
- It gives the project a clean top-level object to run with uvicorn.
"""

from fastapi import FastAPI

# Import the upload route module.
# This helps us keep endpoint code separate from app startup code.
from .routes.analyse import router

# Step 1: Create the main FastAPI application object.
# This object controls the entire API and holds its routes, middleware, and metadata.
app = FastAPI(
    title="Netra Vision API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Step 2: Include the router from the analyse route file.
# This means every endpoint defined there becomes part of the app.
app.include_router(router)


@app.get("/")
async def root() -> dict:
    """
    Step 3: Health check endpoint.

    What it does:
    - tells us the API is alive and responding
    - gives a quick overview of available endpoints

    How it does:
    - returns a normal JSON dictionary to the browser or API client
    - uses FastAPI's automatic JSON serialization
    """
    return {
        "message": "Crop disease API is healthy",
        "endpoints": {
            "POST /analyse": "Upload an image for validation and saving",
        },
    }


def main() -> None:
    """
    Step 4: Run the API from the terminal.

    What it does:
    - starts the server locally so the API can receive requests

    How it does:
    - imports uvicorn
    - tells uvicorn which FastAPI app to run
    - chooses host and port configuration
    """
    import uvicorn

    # Use uvicorn to launch the app.
    # The string "crop_disease_api:app" tells uvicorn to find the app object in this package.
    uvicorn.run("crop_disease_api:app", host="0.0.0.0", port=8000, reload=True)

