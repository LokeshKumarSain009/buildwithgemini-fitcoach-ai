# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import os
from zoneinfo import ZoneInfo

import dotenv
dotenv.load_dotenv()

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

from app.a2ui_utils import a2ui_callback
from app.tools.exercise_api_tools import fetch_exercise_info
from app.tools.fitness_calculator import calculate_fitness_metrics
from app.tools.image_gen_tools import generate_workout_badge_image
from app.tools.video_gen_tools import generate_exercise_demo_video
from app.tools.workout_db_tools import (
    get_workout_history,
    get_workout_session_details,
    log_workout_session,
)


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description="You are FitCoach AI, an expert workout and fitness coach.",
    workflow_description="Analyze the user request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

base_instruction = (
    "You remember all user exercise preferences, fitness goals, equipment availability, "
    "and injuries or physical limitations across sessions. Always tailor workout plans and recommendations "
    "around the user's remembered preferences and safety requirements. "
    "You can log workout sessions, retrieve workout history, calculate 1-Rep Max (1RM) & volume metrics, "
    "lookup exercise instructions from the public exercise database, generate workout achievement badge graphics, "
    "generate short exercise demonstration and workout videos using Google Omni model (gemini-omni-flash-preview), "
    "and execute Python code in a secure sandbox for fitness data analysis."
)
 
 
# Load Agent Engine resource name from deployment metadata or fallback
AGENT_ENGINE_RESOURCE = "projects/296896720801/locations/us-east1/reasoningEngines/6939389517824524288"
if os.path.exists("deployment_metadata.json"):
    try:
        with open("deployment_metadata.json", "r") as f:
            meta = json.load(f)
            if meta.get("remote_agent_runtime_id"):
                AGENT_ENGINE_RESOURCE = meta["remote_agent_runtime_id"]
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=AGENT_ENGINE_RESOURCE
)
 
 
async def generate_memories_callback(callback_context: CallbackContext):
    """Callback triggered after each agent turn to extract and store key memories (preferences & injuries)."""
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        # Memory service not configured or unavailable in current session context
        pass
    return None
 
 
def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.
 
    Args:
        query: A string containing the location to get weather information for.
 
    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."
 
 
def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.
 
    Args:
        city: The name of the city to get the current time for.
 
    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."
 
    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
 
 
root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=f"{a2ui_instruction}\n\n{base_instruction}",
    tools=[
        PreloadMemoryTool(),
        generate_workout_badge_image,
        generate_exercise_demo_video,
        fetch_exercise_info,
        calculate_fitness_metrics,
        log_workout_session,
        get_workout_history,
        get_workout_session_details,
        get_weather,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
