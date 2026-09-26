from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    Request
)

from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.orm import Session

from .ai_service import (
    generate_workout,
    generate_tip,
    update_plan
)

from .config import (
    ADMIN_TOKEN,
    TEMPLATES_DIR
)

from .database import get_db
from .models import UserPlan

from .schemas import (
    UserInput,
    FeedbackRequest
)


router = APIRouter()

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


def save_record(db, user, plan, tip):

    record = db.scalar(
        select(UserPlan).where(
            UserPlan.user_id == user.user_id
        )
    )

    values = dict(
        name=user.name,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
        experience_level=user.experience_level,
        days_per_week=user.days_per_week,
        original_plan=plan,
        updated_plan=None,
        nutrition_tip=tip,
        feedback=None
    )

    if record:

        for key, value in values.items():
            setattr(record, key, value)

    else:

        record = UserPlan(
            user_id=user.user_id,
            **values
        )

        db.add(record)

    db.commit()
    db.refresh(record)

    return record


def context(record, request, **extra):

    return {
        "request": request,
        "record": record,
        "workout_plan":
            record.updated_plan
            or record.original_plan,
        "is_updated":
            bool(record.updated_plan),
        **extra
    }


@router.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


@router.post("/generate-workout")
def generate_form(
    request: Request,

    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    experience_level: str = Form("beginner"),
    days_per_week: int = Form(5),

    db: Session = Depends(get_db)
):

    try:

        user = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
            experience_level=experience_level,
            days_per_week=days_per_week
        )

        record = save_record(
            db,
            user,
            generate_workout(
                user.model_dump()
            ),
            generate_tip(user.goal)
        )

        return templates.TemplateResponse(
            "result.html",
            context(record, request)
        )

    except Exception as exc:

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(exc)
            },
            status_code=400
        )

@router.get("/feedback")
def feedback_page(request: Request):
    return templates.TemplateResponse(
        "feedback.html",
        {
            "request": request
        }
    )


@router.post("/submit-feedback")
def feedback_form(
    request: Request,

    user_id: str = Form(...),
    feedback: str = Form(...),

    db: Session = Depends(get_db)
):

    record = db.scalar(
        select(UserPlan).where(
            UserPlan.user_id == user_id
        )
    )

    if not record:
        raise HTTPException(
            404,
            "User ID was not found."
        )

    data = FeedbackRequest(
        feedback=feedback
    )

    profile = {
        "name": record.name,
        "age": record.age,
        "weight": record.weight,
        "goal": record.goal,
        "intensity": record.intensity
    }

    record.updated_plan = update_plan(
        record.updated_plan
        or record.original_plan,
        data.feedback,
        profile
    )

    record.feedback = data.feedback

    record.nutrition_tip = generate_tip(
        record.goal
    )

    db.commit()
    db.refresh(record)

    return templates.TemplateResponse(
        "result.html",
        context(
            record,
            request,
            success="Your plan was updated."
        )
    )


@router.get("/view-all-users")
def all_users(
    request: Request,
    token: str | None = Query(None),
    db: Session = Depends(get_db)
):

    if token != ADMIN_TOKEN:

        raise HTTPException(
            401,
            "Invalid admin token."
        )

    users = db.scalars(
        select(UserPlan)
        .order_by(
            UserPlan.created_at.desc()
        )
    ).all()

    return templates.TemplateResponse(
        "all_users.html",
        {
            "request": request,
            "users": users
        }
    )


@router.get("/api/health")
def health():

    return {
        "status": "ok",
        "service": "FitBuddy"
    }


@router.post("/api/plans")
def create_api(
    user: UserInput,
    db: Session = Depends(get_db)
):

    record = save_record(
        db,
        user,
        generate_workout(
            user.model_dump()
        ),
        generate_tip(user.goal)
    )

    return {
        "id": record.id,
        "user_id": record.user_id,
        "name": record.name,
        "goal": record.goal,
        "intensity": record.intensity,
        "workout_plan": record.original_plan,
        "nutrition_tip": record.nutrition_tip,
        "updated": False
    }


@router.get("/api/plans/{user_id}")
def get_api(
    user_id: str,
    db: Session = Depends(get_db)
):

    record = db.scalar(
        select(UserPlan).where(
            UserPlan.user_id == user_id
        )
    )

    if not record:

        raise HTTPException(
            404,
            "User ID was not found."
        )

    return {
        "id": record.id,
        "user_id": record.user_id,
        "name": record.name,
        "age": record.age,
        "weight": record.weight,
        "goal": record.goal,
        "intensity": record.intensity,
        "original_plan": record.original_plan,
        "updated_plan": record.updated_plan,
        "nutrition_tip": record.nutrition_tip,
        "feedback": record.feedback
    }


@router.post("/api/plans/{user_id}/feedback")
def feedback_api(
    user_id: str,
    data: FeedbackRequest,
    db: Session = Depends(get_db)
):

    record = db.scalar(
        select(UserPlan).where(
            UserPlan.user_id == user_id
        )
    )

    if not record:

        raise HTTPException(
            404,
            "User ID was not found."
        )

    profile = {
        "name": record.name,
        "age": record.age,
        "weight": record.weight,
        "goal": record.goal,
        "intensity": record.intensity
    }

    record.updated_plan = update_plan(
        record.updated_plan
        or record.original_plan,
        data.feedback,
        profile
    )

    record.feedback = data.feedback

    record.nutrition_tip = generate_tip(
        record.goal
    )

    db.commit()
    db.refresh(record)

    return {
        "user_id": user_id,
        "workout_plan": record.updated_plan,
        "nutrition_tip": record.nutrition_tip,
        "updated": True
    }


@router.get("/api/nutrition-tip")
def tip_api(
    goal: str = Query(...)
):

    return {
        "goal": goal,
        "nutrition_tip": generate_tip(goal)
    }