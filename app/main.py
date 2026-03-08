from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router as ticket_router
from app.core.config import get_settings
from app.db.database import init_db
from app.utils.logging import configure_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(ticket_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
