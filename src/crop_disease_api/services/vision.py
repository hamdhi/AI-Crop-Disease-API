"""
Gemini vision service.

Step 1: load the API key from environment variables or a .env file
Step 2: create the Google GenAI client
Step 3: asynchronously send the plant image plus prompt to Gemini
Step 4: parse the returned JSON response
"""

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# Step 1: Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# Step 2: Create Gemini client
# ============================================================

def get_gemini_client() -> genai.Client:
    """
    Creates and returns a Gemini client using GEMINI_API_KEY.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "No API key was provided. Please set GEMINI_API_KEY "
            "in your environment or .env file."
        )

    return genai.Client(api_key=api_key)


# ============================================================
# Gemini Prompt
# ============================================================

CROP_ANALYSIS_PROMPT = """
You are an expert agricultural scientist specializing in crop disease detection.

Analyze this image of a crop/plant and provide a detailed disease assessment.

Return ONLY a valid JSON object.

Do NOT:
- use Markdown
- use ```json
- add explanations outside the JSON
- add text before or after the JSON

The JSON must have exactly this structure:

{
    "crop_detected": "Name of the crop or plant visible in the image",

    "severity": "healthy",

    "diseases": [
        {
            "name": "Disease name",
            "confidence": 0.0,
            "description": "Brief description of the disease and visible symptoms"
        }
    ],

    "treatments": [
        {
            "treatment_name": "Name of treatment",
            "treatment_type": "organic",
            "instructions": "Step by step treatment instructions",
            "urgency": "immediate"
        }
    ],

    "overall_health": "One sentence summary of plant health",

    "additional_notes": "Any other observations or recommendations"
}

Rules:

- severity MUST be one of:
  "healthy", "mild", "moderate", "severe", "critical"

- disease confidence MUST be a number between 0.0 and 1.0.

- treatment_type MUST be one of:
  "organic", "chemical", "preventive"

- urgency MUST be one of:
  "immediate", "within_week", "seasonal"

- If no disease is detected, return an empty diseases array.

- If the plant appears healthy, set severity to "healthy".

- Return ONLY the JSON object.
"""


# ============================================================
# Step 3: Analyse image ASYNCHRONOUSLY
# ============================================================

async def analyse_image(
    image_content: bytes,
    content_type: str,
):
    """
    Asynchronously sends the uploaded crop image to Gemini.

    Returns:
        dict: Parsed crop disease analysis.
    """

    # Create Gemini client
    client = get_gemini_client()

    # Gemini model
    model_name = "gemini-3.6-flash"

    # --------------------------------------------------------
    # Asynchronous Gemini request
    # --------------------------------------------------------

    interaction = await client.aio.models.generate_content(
        model=model_name,

        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=CROP_ANALYSIS_PROMPT
                    ),

                    types.Part(
                        inline_data=types.Blob(
                            mime_type=content_type or "image/jpeg",
                            data=image_content,
                        )
                    ),
                ],
            )
        ],

        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    # --------------------------------------------------------
    # Get Gemini response
    # --------------------------------------------------------

    output_text = getattr(interaction, "text", None)

    if not output_text:
        raise ValueError(
            "GenAI interaction returned no output text."
        )

    print("GenAI interaction response:")
    print(output_text)

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:
        analysis = json.loads(output_text)

    except json.JSONDecodeError as error:
        print("Invalid JSON returned by Gemini:")
        print(repr(output_text))

        raise ValueError(
            "Gemini returned invalid JSON."
        ) from error

    return analysis
