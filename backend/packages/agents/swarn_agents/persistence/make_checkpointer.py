import asyncio
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from psycopg_pool import AsyncConnectionPool

_pool = None
_setup_done = False
_lock = asyncio.Lock()

def get_psycopg_conn_string(database_url: str) -> str:
    # converts "postgresql+psycopg://user:pass@host/db" -> "postgresql://user:pass@host/db"
    return database_url.replace("+psycopg", "").replace("+asyncpg", "")

async def _get_pool(settings):
    global _pool
    if _pool is None:
        conn_str = get_psycopg_conn_string(settings.database_url)
        _pool = AsyncConnectionPool(
            conninfo=conn_str,
            max_size=20,
            kwargs={"autocommit": True, "prepare_threshold": 0},
        )
    return _pool

async def make_checkpointer(settings) -> AsyncPostgresSaver:
    global _setup_done
    pool = await _get_pool(settings)
    checkpointer = AsyncPostgresSaver(pool)
    
    async with _lock:
        if not _setup_done:
            await checkpointer.setup()
            _setup_done = True
            
    return checkpointer

async def make_store(settings) -> AsyncPostgresStore:
    global _setup_done
    pool = await _get_pool(settings)
    store = AsyncPostgresStore(pool)
    
    async with _lock:
        if not _setup_done:
            await store.setup()
            _setup_done = True
            
    return store
