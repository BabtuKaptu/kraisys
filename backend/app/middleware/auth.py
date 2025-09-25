"""Simple Basic Auth middleware for v0.7.1 security."""

import base64
import secrets
from typing import Optional, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class BasicAuthMiddleware(BaseHTTPMiddleware):
    """Simple HTTP Basic Authentication middleware."""
    
    def __init__(self, app, username: str, password: str):
        super().__init__(app)
        self.username = username
        self.password = password
        self.realm = "KRAI Production System"
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Check authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not self._verify_credentials(auth_header):
            return self._unauthorized_response()
        
        return await call_next(request)
    
    def _verify_credentials(self, auth_header: str) -> bool:
        """Verify Basic Auth credentials."""
        try:
            if not auth_header.startswith("Basic "):
                return False
            
            # Decode base64 credentials
            encoded_credentials = auth_header.split(" ", 1)[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
            
            # Constant time comparison to prevent timing attacks
            return (
                secrets.compare_digest(username, self.username) and
                secrets.compare_digest(password, self.password)
            )
        except Exception:
            return False
    
    def _unauthorized_response(self) -> Response:
        """Return 401 Unauthorized response with WWW-Authenticate header."""
        return Response(
            content="Authentication required",
            status_code=401,
            headers={"WWW-Authenticate": f'Basic realm="{self.realm}"'}
        )
