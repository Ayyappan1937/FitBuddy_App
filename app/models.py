from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class UserPlan(Base):

    __tablename__ = "user_plans"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(120)
    )

    age: Mapped[int] = mapped_column(
        Integer
    )

    weight: Mapped[float] = mapped_column(
        Float
    )

    goal: Mapped[str] = mapped_column(
        String(80)
    )

    intensity: Mapped[str] = mapped_column(
        String(20)
    )

    experience_level: Mapped[str] = mapped_column(
        String(30)
    )

    days_per_week: Mapped[int] = mapped_column(
        Integer
    )

    original_plan: Mapped[str] = mapped_column(
        Text
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )