from app.core.logging import logger
from app.core.database import Base, engine
from app.core.config import CONFIG
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from httpx import AsyncClient
from app.domains import *  # noqa: F401, F403
from app.utils.create_admin import create_admin_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = Redis(host=CONFIG.REDIS_HOST, port=CONFIG.REDIS_PORT, db=0)
    http_client = AsyncClient()
    app.state.redis = redis_client
    app.state.http_client = http_client
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
        create_admin_user()
        redis_status = await redis_client.ping()
        logger.info(f"Redis connection status: {redis_status}")
    except Exception as e:
        logger.error(e)
        raise
    try:
        yield
    finally:
        await redis_client.aclose()
        await http_client.aclose()


app = FastAPI(lifespan=lifespan)
