from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from packages.core.config import settings
from apps.api.routes import approvals, experiments, stream, chat

from contextlib import asynccontextmanager
from arq import create_pool
from arq.connections import RedisSettings

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(redis_url))
    yield
    await app.state.arq_pool.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(approvals.router)
app.include_router(experiments.router)
app.include_router(stream.router)
app.include_router(chat.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "app_name": settings.app_name}
