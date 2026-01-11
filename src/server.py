"""
MCP Server with Streamable HTTP Transport

MCP 서버 생성 가이드(2025-03-26 스펙) 준수:
- Streamable HTTP 전송 방식 사용
- 단일 /mcp 엔드포인트
- Stateless 설계
- Bearer Token 인증 지원
"""

import os
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

# Import the initialized FastMCP instance
from src.main import mcp


class AuthMiddleware(BaseHTTPMiddleware):
    """Bearer Token 인증 미들웨어 (커스텀 헤더 방식)"""
    
    async def dispatch(self, request: Request, call_next):
        # /health 엔드포인트는 인증 제외
        if request.url.path == "/health":
            return await call_next(request)
            
        auth_token = os.getenv("MCP_AUTH_TOKEN")
        if auth_token:
            auth_header = request.headers.get("Authorization")
            if not auth_header or auth_header != f"Bearer {auth_token}":
                return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)


async def health_check(request: Request) -> JSONResponse:
    """헬스체크 엔드포인트"""
    return JSONResponse({"status": "ok", "transport": "streamable-http"})


# FastMCP의 내장 Streamable HTTP 앱 사용 (lifespan 포함)
# transport_security 설정은 main.py에서 FastMCP 초기화 시 적용됨
_mcp_app = mcp.streamable_http_app()

# MCP 앱에 커스텀 라우트 추가 (/health)
_mcp_app.routes.insert(0, Route("/health", endpoint=health_check, methods=["GET"]))

# 미들웨어 추가
_mcp_app.add_middleware(AuthMiddleware)

# 최종 앱
app = _mcp_app
