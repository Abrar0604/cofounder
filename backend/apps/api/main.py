from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from packages.core.config import settings
from apps.api.routes import approvals, experiments, stream, chat

app = FastAPI(title=settings.app_name)

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
