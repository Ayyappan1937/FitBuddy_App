from typing import Literal

from pydantic import BaseModel, Field


class UserInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=100
    )

    name: str = Field(
        min_length=2,
        max_length=120
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=20,
        le=400
    )

    goal: Literal[
        "weight loss",
        "muscle gain",
        "general wellness",
        "flexibility",
        "endurance"
    ]

    intensity: Literal[
        "low",
        "medium",
        "high"
    ]

    experience_level: str = Field(
        default="beginner",
        min_length=3,
        max_length=30
    )

    days_per_week: int = Field(
        default=5,
        ge=2,
        le=7
    )


class FeedbackRequest(BaseModel):

    feedback: str = Field(
        min_length=5,
        max_length=2000
    )