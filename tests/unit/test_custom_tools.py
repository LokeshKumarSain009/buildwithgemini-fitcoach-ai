"""Unit tests for FitCoach AI custom function tools."""

import pytest
from app.tools.fitness_calculator import calculate_fitness_metrics
from app.tools.exercise_api_tools import fetch_exercise_info


def test_calculate_fitness_metrics():
    """Test 1RM and total volume calculations."""
    res = calculate_fitness_metrics(weight_lbs=185.0, reps=8, sets=3, duration_minutes=45)
    assert "estimated_1rm_lbs" in res
    assert res["estimated_1rm_lbs"] == 234.3
    assert res["total_volume_lbs"] == 4440.0
    assert "estimated_calories_burned" in res


def test_calculate_fitness_metrics_invalid():
    """Test error handling for non-positive inputs."""
    res = calculate_fitness_metrics(weight_lbs=0, reps=-5)
    assert "error" in res


def test_fetch_exercise_info_public_api():
    """Test fetching exercise details from the wger.de public API."""
    res = fetch_exercise_info("rollout")
    assert res.get("status") == "success"
    assert res.get("count", 0) > 0
    assert len(res.get("exercises", [])) > 0
    exercise = res["exercises"][0]
    assert "name" in exercise
    assert "muscles_targeted" in exercise
    assert "instructions" in exercise
