"""
Crop disease API package.

This file is the project entry point.
It is the top-level place where the FastAPI app is created and connected to its routes.

Learning flow:
Step 1: load environment variables
Step 2: create the FastAPI app instance
Step 3: include the route module
Step 4: expose a basic health endpoint
Step 5: run the server with uvicorn

Think of this file as the front door of the API.
Everything important starts from here.
"""

from dotenv import load_dotenv
from fastapi import FastAPI

# Step 1: Load environment variables before app startup.
# This is useful for secret values such as GEMINI_API_KEY.
load_dotenv()

# Step 2: Import the route module containing the /analyse endpoint.
# This keeps the API code organized by feature instead of placing everything in one file.
from .routes.analyse import router

# Step 3: Create the main FastAPI application object.
# This object contains the app configuration and all registered routes.
app = FastAPI(
    title="Netra Vision API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Step 4: Include the router.
# This attaches all endpoints defined in the analyse module to the app.
app.include_router(router)


@app.get("/")
async def root() -> dict:
    """
    Step 5: Health check endpoint.

    What it does:
    - confirms the app is running
    - gives a quick guide to the main endpoint

    How it does:
    - returns a normal JSON dictionary
    - FastAPI serializes it automatically for the client
    """
    return {
        "message": "Crop disease API is healthy",
        "endpoints": {
            "POST /analyse": "Upload an image for validation, processing, and AI analysis",
        },
    }


def main() -> None:
    """
    Step 6: Run the API from the terminal.

    What it does:
    - starts the uvicorn server

    How it does:
    - imports uvicorn
    - passes the app object to uvicorn.run()
    """
    import uvicorn

    uvicorn.run("crop_disease_api:app", host="0.0.0.0", port=8000, reload=True)

