"""Public exercise database tool using wger.de free public API."""

import os
import re
import requests

WGER_API_URL = "https://wger.de/api/v2/exerciseinfo/"


def fetch_exercise_info(exercise_name: str) -> dict:
    """Fetches real exercise details, target muscle groups, and required equipment from the wger.de public fitness API.

    Args:
        exercise_name: The name or keyword of the exercise to search for (e.g., 'rollout', 'press', 'bicep', 'squat').

    Returns:
        Dict containing matching exercise names, target muscle groups, equipment, and form instructions.
    """
    try:
        headers = {}
        api_key = os.environ.get("WGER_API_KEY")
        if api_key:
            headers["Authorization"] = f"Token {api_key}"

        response = requests.get(
            WGER_API_URL,
            headers=headers,
            params={"limit": 60},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        matched_exercises = []
        query = exercise_name.lower().strip()

        for item in results:
            translations = item.get("translations", [])
            for trans in translations:
                # English language ID is 2 in wger API, or match query in name
                name = trans.get("name", "")
                desc = trans.get("description", "")
                if query in name.lower() or query in desc.lower():
                    category_info = item.get("category", {})
                    category_name = (
                        category_info.get("name")
                        if isinstance(category_info, dict)
                        else str(category_info)
                    )

                    muscles = [
                        m.get("name")
                        for m in item.get("muscles", [])
                        if isinstance(m, dict) and m.get("name")
                    ]
                    equipment = [
                        e.get("name")
                        for e in item.get("equipment", [])
                        if isinstance(e, dict) and e.get("name")
                    ]

                    # Strip HTML tags from description
                    clean_desc = re.sub("<[^<]+?>", "", desc).strip()

                    matched_exercises.append(
                        {
                            "name": name,
                            "category": category_name,
                            "muscles_targeted": muscles,
                            "equipment_required": equipment,
                            "instructions": clean_desc,
                        }
                    )
                    break

        if not matched_exercises:
            return {
                "status": "not_found",
                "message": f"No exercises matching '{exercise_name}' found in public database.",
            }

        return {
            "status": "success",
            "query": exercise_name,
            "count": len(matched_exercises),
            "exercises": matched_exercises[:3],
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch exercise info from public API: {str(e)}",
        }
