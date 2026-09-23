"""Fitness calculator tools for FitCoach AI."""


def calculate_fitness_metrics(
    weight_lbs: float,
    reps: int,
    sets: int = 1,
    duration_minutes: int | None = None,
) -> dict:
    """Calculates key fitness metrics including estimated 1-Rep Max (1RM) and total workout volume.

    Args:
        weight_lbs: The weight lifted in pounds (e.g., 150.0).
        reps: Number of repetitions performed per set (e.g., 10).
        sets: Number of sets completed (default: 1).
        duration_minutes: Optional workout duration in minutes for calorie estimation.

    Returns:
        Dict containing estimated 1-Rep Max (1RM), total volume, and estimated calories burned.
    """
    if reps <= 0 or weight_lbs <= 0:
        return {"error": "Weight and reps must be greater than zero."}

    # Epley formula for 1RM: 1RM = weight * (1 + reps / 30)
    if reps == 1:
        one_rep_max = round(weight_lbs, 1)
    else:
        one_rep_max = round(weight_lbs * (1 + reps / 30.0), 1)

    total_volume = round(weight_lbs * reps * sets, 1)

    result = {
        "estimated_1rm_lbs": one_rep_max,
        "total_volume_lbs": total_volume,
        "weight_lbs": weight_lbs,
        "reps": reps,
        "sets": sets,
    }

    if duration_minutes and duration_minutes > 0:
        # Average resistance training MET ~5.0 assuming 70kg user weight
        est_calories = round(5.0 * 70.0 * (duration_minutes / 60.0), 1)
        result["estimated_calories_burned"] = est_calories

    return result
