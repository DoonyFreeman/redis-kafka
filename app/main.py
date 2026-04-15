import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aiokafka.errors import KafkaConnectionError
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as api_router
from app.config import get_settings
from app.core.exceptions import AppError
from app.core.kafka import kafka_producer
from app.core.redis import redis_client
from app.middleware.rate_limiter import RateLimitMiddleware

settings = get_settings()


async def _start_kafka_with_retry() -> None:
    max_retries = 30
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            await kafka_producer.start()
            return
        except KafkaConnectionError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise e


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await redis_client.connect()
    await _start_kafka_with_retry()
    yield
    await kafka_producer.stop()
    await redis_client.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

app.include_router(api_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "app": settings.APP_NAME}
