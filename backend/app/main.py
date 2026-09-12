"""
Point d'entrée de l'application Trust Mesh.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import engine, get_db
from app.models import User
from app.routers.auth import router as auth_router
from app.routers.demo import router as demo_router
from app.routers.trust import router as trust_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Les tables sont gérées par Alembic (voir alembic/), plus par create_all.
    yield
    await engine.dispose()


app = FastAPI(
    title="Trust Mesh API",
    description="AI-Powered Adaptive Identity Engine — MENA Open Gateway Hackathon 2026",
    version="0.1.0",
    lifespan=lifespan,
)


if settings.cors_origins == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(demo_router)
app.include_router(trust_router)