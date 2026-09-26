import os
from pathlib import Path


os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.db"
os.environ["GOOGLE_API_KEY"] = ""
os.environ["ALLOW_AI_FALLBACK"] = "true"
os.environ["ADMIN_TOKEN"] = "test-token"


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    r = client.get("/api/health")

    assert (
        r.status_code == 200
        and r.json()["status"] == "ok"
    )


def test_create_and_feedback():

    payload = {
        "user_id": "test-user",
        "name": "Tester",
        "age": 20,
        "weight": 65,
        "goal": "general wellness",
        "intensity": "low",
        "experience_level": "beginner",
        "days_per_week": 3
    }

    r = client.post(
        "/api/plans",
        json=payload
    )

    assert (
        r.status_code == 200
        and "Day 1" in r.json()["workout_plan"]
    )


    r = client.post(
        "/api/plans/test-user/feedback",
        json={
            "feedback":
            "Add mobility and recovery."
        }
    )

    assert (
        r.status_code == 200
        and r.json()["updated"] is True
    )


def teardown_module():

    p = Path("test_fitbuddy.db")

    if p.exists():
        p.unlink()