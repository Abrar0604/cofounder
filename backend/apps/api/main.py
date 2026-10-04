from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from packages.core.config import settings
from apps.api.routes import approvals, experiments, stream, chat, ventures

from contextlib import asynccontextmanager
from arq import create_pool
from arq.connections import RedisSettings

import redis.asyncio as redis

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from packages.agents.orchestrator.graph import create_orchestrator_graph
from packages.approvals.service import ApprovalService

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    app.state.redis_client = redis.from_url(redis_url)
    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(redis_url))
    
    # Initialize shared checkpointer
    app.state.checkpointer_cm = AsyncSqliteSaver.from_conn_string("checkpoints.db")
    app.state.checkpointer = await app.state.checkpointer_cm.__aenter__()
    await app.state.checkpointer.setup()
    
    # Initialize graph and approval service for the API
    app.state.shared_graph = create_orchestrator_graph(checkpointer=app.state.checkpointer)
    app.state.approval_service = ApprovalService(app.state.shared_graph)
    
    yield
    await app.state.checkpointer_cm.__aexit__(None, None, None)
    await app.state.arq_pool.close()
    await app.state.redis_client.aclose()

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
app.include_router(ventures.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "app_name": settings.app_name}
