from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app import models  # noqa: F401
from app.models.user import User

settings = get_settings()


async def _ensure_default_user() -> None:
    if not settings.default_user_email or not settings.default_user_password:
        return

    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == settings.default_user_email))
        existing_user = result.scalar_one_or_none()
        if existing_user is not None:
            return

        session.add(
            User(
                email=settings.default_user_email,
                name=settings.default_user_name,
                password_hash=hash_password(settings.default_user_password),
            )
        )
        await session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.db_auto_create:
        for attempt in range(1, 21):
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                break
            except Exception:
                if attempt == 20:
                    raise
                await asyncio.sleep(1)
    await _ensure_default_user()
    yield


app = FastAPI(title="Target App API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
