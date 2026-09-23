"""Seed script for populating initial workout session items into Firestore."""

import datetime
from google.cloud import firestore

# CRITICAL: Project ID is explicitly hardcoded as a string as required by Agent Platform specifications.
PROJECT_ID = "qwiklabs-gcp-02-38ad309f606a"
COLLECTION_NAME = "workout_sessions"

SEEDED_WORKOUTS = [
    {
        "session_id": "seed_session_001",
        "user_id": "user_alex",
        "workout_name": "Upper Body Push & Core Routine",
        "date": "2026-09-20",
        "duration_minutes": 45,
        "intensity_rating": 7,
        "exercises": [
            {"name": "Dumbbell Bench Press", "sets": 3, "reps": 12, "weight_lbs": 45},
            {"name": "Seated Overhead Dumbbell Press", "sets": 3, "reps": 10, "weight_lbs": 30},
            {"name": "Bodyweight Incline Push-ups", "sets": 3, "reps": 15, "weight_lbs": 0},
            {"name": "Plank Hold", "sets": 3, "reps": 60, "weight_lbs": 0},
        ],
        "notes": "Focused on controlled eccentric phase. Zero strain on lower back.",
        "created_at": "2026-09-20T10:00:00Z",
    },
    {
        "session_id": "seed_session_002",
        "user_id": "user_alex",
        "workout_name": "Pull & Biceps Conditioning",
        "date": "2026-09-21",
        "duration_minutes": 40,
        "intensity_rating": 8,
        "exercises": [
            {"name": "Seated Cable Lat Pulldown", "sets": 3, "reps": 12, "weight_lbs": 90},
            {"name": "Chest-Supported Dumbbell Rows", "sets": 3, "reps": 10, "weight_lbs": 40},
            {"name": "Seated Dumbbell Bicep Curls", "sets": 3, "reps": 12, "weight_lbs": 25},
            {"name": "Face Pulls", "sets": 3, "reps": 15, "weight_lbs": 35},
        ],
        "notes": "Excellent posture support. Felt good pump in upper back.",
        "created_at": "2026-09-21T14:30:00Z",
    },
    {
        "session_id": "seed_session_003",
        "user_id": "user_alex",
        "workout_name": "Low-Impact Leg Mobility & Core",
        "date": "2026-09-22",
        "duration_minutes": 35,
        "intensity_rating": 6,
        "exercises": [
            {"name": "Bodyweight Dumbbell Lunges", "sets": 3, "reps": 10, "weight_lbs": 20},
            {"name": "Glute Bridges", "sets": 3, "reps": 15, "weight_lbs": 0},
            {"name": "Standing Calf Raises", "sets": 3, "reps": 20, "weight_lbs": 25},
            {"name": "Bird-Dog Extensions", "sets": 3, "reps": 12, "weight_lbs": 0},
        ],
        "notes": "Safe leg mobility workout. Preferred dumbbell lunges performed smoothly.",
        "created_at": "2026-09-22T09:15:00Z",
    },
]


def seed():
    print(f"Connecting to Firestore with hardcoded Project ID: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for item in SEEDED_WORKOUTS:
        doc_ref = collection.document(item["session_id"])
        doc_ref.set(item)
        print(f"Seeded document: {item['session_id']} -> {item['workout_name']}")

    print(f"Successfully seeded {len(SEEDED_WORKOUTS)} items into collection '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    seed()
