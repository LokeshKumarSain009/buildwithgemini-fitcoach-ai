"""Video generation tools for FitCoach AI using Google Omni model (gemini-omni-flash-preview)."""

import base64
import uuid
from google import genai
from google.cloud import storage
from google.genai import types
from google.adk.tools import ToolContext

# Hardcoded project ID and public Cloud Storage bucket name
PROJECT_ID = "qwiklabs-gcp-02-38ad309f606a"
BUCKET_NAME = "fitcoach-ai-media-qwiklabs-gcp-02-38ad309f606a"


async def generate_exercise_demo_video(
    prompt: str,
    tool_context: ToolContext,
) -> dict:
    """Generates a short exercise demonstration or workout motion video using Google's Omni model (gemini-omni-flash-preview).

    Saves the video as a session artifact and uploads it to public Cloud Storage, returning its public HTTPS URL.

    Args:
        prompt: Description of the exercise demonstration or workout video to generate.
        tool_context: ADK ToolContext provided automatically by the agent framework.

    Returns:
        Dict containing status, artifact filename, and public HTTPS URL of the generated video.
    """
    try:
        # Initialize GenAI Client for global location using gemini-omni-flash-preview
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        res = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        if hasattr(res, "output_video") and res.output_video and getattr(res.output_video, "data", None):
            raw_data = res.output_video.data
            if isinstance(raw_data, str):
                video_bytes = base64.b64decode(raw_data)
            else:
                video_bytes = raw_data
        elif hasattr(res, "outputs") and res.outputs:
            for item in res.outputs:
                if hasattr(item, "video") and item.video and getattr(item.video, "data", None):
                    raw_data = item.video.data
                    video_bytes = base64.b64decode(raw_data) if isinstance(raw_data, str) else raw_data
                    break

        if not video_bytes:
            return {
                "status": "error",
                "message": "No video bytes returned from gemini-omni-flash-preview model.",
            }

        file_id = str(uuid.uuid4())[:8]
        filename = f"exercise_demo_{file_id}.mp4"
        mime_type = "video/mp4"

        # (1) Save video as artifact to Playground's Artifacts panel
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # (2) Upload video bytes directly to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "message": f"Successfully generated exercise video for prompt: '{prompt}'",
            "artifact_filename": filename,
            "public_video_url": public_url,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate and save video: {str(e)}",
        }
