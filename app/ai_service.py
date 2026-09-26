from .config import (
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    ALLOW_AI_FALLBACK
)


try:
    from google import genai
except ImportError:
    genai = None


def fallback_plan(goal, intensity, level):

    sessions = [
        "Full body strength: squats, incline push-ups, glute bridges, and rows; 2–3 sets each.",

        "Cardio: 20–35 minutes brisk walking or cycling, followed by mobility.",

        "Upper body and core: push-ups, rows, shoulder presses, dead bugs, and plank.",

        "Lower body: squats, reverse lunges, hip hinges, calf raises, and side plank.",

        "Conditioning: alternate 2 minutes easy cardio with 1 minute moderate cardio for 20 minutes.",

        "Active recovery: easy walking and gentle stretching.",

        "Recovery: light mobility, breathing practice, and a comfortable walk.",
    ]

    out = [
        f"FITBUDDY 7-DAY PLAN | Goal: {goal} | Intensity: {intensity} | Level: {level}",
        ""
    ]

    for i, session in enumerate(sessions, 1):

        out += [
            f"Day {i}:",
            "- Warm-up: 5–10 minutes.",
            f"- Main session: {session}",
            "- Cooldown: 5 minutes.",
            ""
        ]

    out.append(
        "Safety: Stop for pain, dizziness, chest discomfort, or unusual breathlessness."
    )

    return "\n".join(out)


def fallback_tip(goal):

    return {

        "weight loss":
            "Build meals around vegetables, protein, fiber-rich carbohydrates, and water. Avoid extreme restriction.",

        "muscle gain":
            "Include protein in each meal, eat enough overall, hydrate, and prioritize sleep.",

        "general wellness":
            "Keep movement consistent and combine balanced meals, hydration, and regular sleep.",

        "flexibility":
            "Practice gentle mobility consistently and never force a stretch into sharp pain.",

        "endurance":
            "Increase cardio gradually and include easy recovery days.",

    }.get(
        goal,
        "Prioritize balanced meals, hydration, movement, and sleep."
    )


def ask(prompt):

    if not GOOGLE_API_KEY or genai is None:

        if ALLOW_AI_FALLBACK:
            return None

        raise RuntimeError(
            "GOOGLE_API_KEY is not configured."
        )

    try:

        client = genai.Client(
            api_key=GOOGLE_API_KEY
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        return (
            getattr(response, "text", None)
            or str(response)
        ).strip()

    except Exception:

        if ALLOW_AI_FALLBACK:
            return None

        raise


def generate_workout(data):

    prompt = f"""
Create a safe, practical 7-day workout plan in plain text.

Profile:
{data}

Include:

- Warm-up
- Exercises
- Sets/reps or duration
- Cooldown
- Recovery days
- Safety note

Do not diagnose or promise results.
"""

    result = ask(prompt)

    return (
        result
        or fallback_plan(
            data["goal"],
            data["intensity"],
            data["experience_level"]
        )
    )


def generate_tip(goal):

    result = ask(
        f"""
Give 2–4 concise, practical,
non-medical nutrition or recovery
sentences for {goal}.
"""
    )

    return result or fallback_tip(goal)


def update_plan(original, feedback, profile):

    prompt = f"""
Revise this complete 7-day fitness plan
using the feedback.

Profile:
{profile}

Original plan:
{original}

Feedback:
{feedback}

Return the complete revised plan
with recovery and safety guidance.
"""

    result = ask(prompt)

    return (
        result
        or original
        + f"\n\nUPDATED FROM FEEDBACK:\n{feedback}"
    )