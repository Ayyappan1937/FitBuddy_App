from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import STATIC_DIR
from .database import Base, engine
from .routes import router


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="FitBuddy",
    version="1.0.0"
)


app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)


app.include_router(router)