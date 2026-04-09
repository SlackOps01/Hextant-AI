from app.core.logging import logger
from app.core.database import Base, engine
from app.core.config import CONFIG
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from httpx import AsyncClient
from fastapi.middleware.cors import CORSMiddleware
import time
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.create_admin import create_admin_user
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from app.domains import (
    user_router,
    auth_router,
    conversation_router,
    llm_model_router,
    tier_router,
    message_router,
    attachment_router
)


def custom_rate_limit_exceeded_handler(request: Request, exc: Exception):
    logger.warning(f"Rate limit exceeded for {request.client.host}")

    custom_headers = {"Retry-After": "60", "Information": "Hehehehe"}
    return JSONResponse(
        status_code=429,
        content={"error": "Too Many Requests", "detail": exc.detail},
        headers=custom_headers,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = Redis(host=CONFIG.REDIS_HOST, port=CONFIG.REDIS_PORT, db=0)
    http_client = AsyncClient()
    app.state.redis_client = redis_client
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        
        # Attach to headers for the client
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        # Log it for your own telemetry
        logger.info(f"Path: {request.url.path} | Time: {process_time:.4f}s")
        
        return response

app.add_middleware(ProcessTimeMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# Routes
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(conversation_router)
app.include_router(llm_model_router)
app.include_router(tier_router)
app.include_router(message_router)
app.include_router(attachment_router)


@app.get("/")
@limiter.limit("1/second")
async def root(request: Request):
    return {"message": "Hello World"}
