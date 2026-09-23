"""Firestore backend tools for FitCoach AI workout session logging and history."""

import datetime
from google.cloud import firestore
from google.cloud.firestore import FieldFilter

# CRITICAL: Project ID is explicitly hardcoded as a string as required by Agent Platform specifications.
PROJECT_ID = "qwiklabs-gcp-02-38ad309f606a"
COLLECTION_NAME = "workout_sessions"

_db = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client initialized with hardcoded project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def log_workout_session(
    user_id: str,
    workout_name: str,
    exercises: list[dict],
    duration_minutes: int,
    notes: str = "",
    intensity_rating: int = 7,
    session_date: str | None = None,
) -> dict:
    """Logs a completed workout session into the Firestore database.

    Args:
        user_id: The ID of the user completing the workout (e.g., 'user_alex').
        workout_name: The name or title of the workout (e.g., 'Upper Body Strength').
        exercises: List of exercise dicts with 'name', 'sets', 'reps', and optional 'weight_lbs'.
        duration_minutes: Total workout duration in minutes (e.g., 45).
        notes: Optional feedback or notes regarding how the workout felt.
        intensity_rating: Rating from 1 (very light) to 10 (maximum effort).
        session_date: Optional date string ('YYYY-MM-DD'). Defaults to today's date if omitted.

    Returns:
        A dict confirming successful creation with session_id and status.
    """
    db = get_firestore_client()
    if not session_date:
        session_date = datetime.date.today().isoformat()

    doc_ref = db.collection(COLLECTION_NAME).document()
    session_data = {
        "session_id": doc_ref.id,
        "user_id": user_id,
        "workout_name": workout_name,
        "date": session_date,
        "duration_minutes": duration_minutes,
        "exercises": exercises,
        "notes": notes,
        "intensity_rating": intensity_rating,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    doc_ref.set(session_data)
    return {
        "status": "success",
        "message": f"Successfully logged workout session '{workout_name}' for user {user_id}.",
        "session_id": doc_ref.id,
        "data": session_data,
    }


def get_workout_history(user_id: str = "user_alex", limit: int = 5) -> list[dict]:
    """Retrieves recent workout session logs for a user from Firestore.

    Args:
        user_id: The user ID to query workout history for (e.g., 'user_alex').
        limit: Maximum number of recent workout sessions to return (default: 5).

    Returns:
        List of workout session documents ordered by date descending.
    """
    db = get_firestore_client()
    query = (
        db.collection(COLLECTION_NAME)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .limit(limit)
    )
    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append(data)
    results.sort(key=lambda x: x.get("date", ""), reverse=True)
    return results


def get_workout_session_details(session_id: str) -> dict:
    """Gets detailed info for a specific workout session from Firestore by session_id.

    Args:
        session_id: The unique document ID of the workout session.

    Returns:
        Dict containing workout session details or error message.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(session_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"status": "error", "message": f"Workout session {session_id} not found."}
    return {"status": "success", "data": doc.to_dict()}
