from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.db.session import init_db
from app.api.v1 import router as api_v1_router
from app.core.exceptions import NotFoundError, ConflictError, ForbiddenError, not_found_handler, conflict_handler, forbidden_handler

import pathlib


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Create uploads directory
    pathlib.Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI宠物翻译官 — 帮你发现宠物你没注意到的健康异常",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(ConflictError, conflict_handler)
app.add_exception_handler(ForbiddenError, forbidden_handler)

app.include_router(api_v1_router)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/health")
async def health():
    return {"status": "ok"}