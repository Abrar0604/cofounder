from fastapi import FastAPI
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from packages.core.config import settings
from apps.api.routes import approvals, experiments, stream

app = FastAPI(title=settings.app_name)
app.include_router(approvals.router)
app.include_router(experiments.router)
app.include_router(stream.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "app_name": settings.app_name}
