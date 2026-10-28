# Crop Disease API

This project is a FastAPI application for uploading crop images, validating them, saving them, and analyzing them with a Gemini-based vision model.

## Project flow

Step 1: The app starts from the package entry point in the `src/crop_disease_api/__init__.py` file.
Step 2: FastAPI creates the app and includes the route module.
Step 3: The `/analyse` route receives the uploaded image.
Step 4: The image service validates the file type and dimensions.
Step 5: The image is resized and saved to the `uploads/` folder.
Step 6: The Gemini vision service sends the image to the AI model.
Step 7: The model returns a structured analysis in JSON format.
Step 8: The API returns the result to the client.

## Folder structure

- `src/crop_disease_api/__init__.py`  
  Main FastAPI app entry point.

- `src/crop_disease_api/routes/analyse.py`  
  Upload route and processing flow for image requests.

- `src/crop_disease_api/services/image.py`  
  Image validation, resizing, and saving functions.

- `src/crop_disease_api/services/vision.py`  
  Gemini AI integration for crop disease analysis.

## Environment setup

Create a `.env` file in the project root with your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

## Run the app

```bash
uv run uvicorn crop_disease_api:app --host 127.0.0.1 --port 8000 --reload
```

Once the server is ready, your default browser opens http://127.0.0.1:8000/ui.
Select one image for single analysis or several images for batch analysis, then click **Analyse**.
You can also open that URL manually if your browser does not launch.
Automatic opening uses local port 8000; with `--reload`, each server restart may open another tab.
The existing JSON health endpoint remains at `/` and API documentation at `/docs`.

## Learning notes

- The app is split into small modules so the code is easier to study.
- `routes` handles HTTP requests.
- `services` handles business logic.
- `__init__.py` starts the API and connects the modules.
- The AI vision step is separated from the file workflow so the project stays organized.

## Common project pattern

This is a standard pattern used in many FastAPI projects:

1. Receive the request
2. Validate the input
3. Process the data
4. Save or transform the data
5. Return a result
