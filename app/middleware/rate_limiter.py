from collections.abc import Awaitable
from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import get_settings
from app.core.redis import redis_client

settings = get_settings()

PUBLIC_PATHS = [
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/api/v1/products",
    "/api/v1/categories",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
]


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path

        if not self._is_public_path(path):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        user_id = await self._get_user_id(request)

        key = f"rate_limit:{client_ip}:{user_id}"

        current = await redis_client.client.incr(key)
        if current == 1:
            await redis_client.client.expire(key, 60)

        if current > settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Max {settings.RATE_LIMIT_PER_MINUTE} requests per minute."
                },
            )

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        for public_path in PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def _get_user_id(self, request: Request) -> str:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return "anonymous"

        try:
            from app.core.security import decode_token

            token = auth_header.replace("Bearer ", "")
            payload = decode_token(token)
            if payload and payload.get("sub"):
                return payload["sub"]
        except Exception:
            pass

        return "anonymous"
