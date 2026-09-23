"""Image generation tools for FitCoach AI using Gemini models."""

import uuid
from google import genai
from google.cloud import storage
from google.genai import types
from google.adk.tools import ToolContext

# CRITICAL: Hardcoded project ID and public Cloud Storage bucket name
PROJECT_ID = "qwiklabs-gcp-02-38ad309f606a"
BUCKET_NAME = "fitcoach-ai-media-qwiklabs-gcp-02-38ad309f606a"


async def generate_workout_badge_image(
    prompt: str,
    tool_context: ToolContext,
) -> dict:
    """Generates a custom workout achievement badge, posture card, or fitness motivational graphic.

    Saves the image as a session artifact and uploads it to public Cloud Storage, returning its public HTTPS URL.

    Args:
        prompt: Description of the fitness image or achievement badge to generate.
        tool_context: ADK ToolContext provided automatically by the agent framework.

    Returns:
        Dict containing status, artifact filename, and public HTTPS URL of the generated image.
    """
    try:
        # Initialize GenAI Client for global location using gemini-3.1-flash-lite-image
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        image_bytes = None
        mime_type = "image/png"

        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    if part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
                    break

        if not image_bytes:
            return {
                "status": "error",
                "message": "No image data returned from image generation model.",
            }

        file_id = str(uuid.uuid4())[:8]
        extension = "png" if "png" in mime_type.lower() else "jpg"
        filename = f"workout_badge_{file_id}.{extension}"

        # Action 1: Save artifact to Playground's Artifacts panel via ToolContext
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # Action 2: Upload image bytes directly to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "message": f"Successfully generated fitness image for prompt: '{prompt}'",
            "artifact_filename": filename,
            "public_image_url": public_url,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate and save image: {str(e)}",
        }
