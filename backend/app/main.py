"""
KRAI System v0.6 - FastAPI Backend
Main application entry point
"""

import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.logging import setup_logging, log_api_request, log_api_response
from app.api.api_v1.api import api_router
from app.db.init_db import init_db
from app.middleware.auth import BasicAuthMiddleware

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="KRAI Production System API",
    docs_url="/docs",
    redoc_url="/redoc",
)

logger.info(f"Initializing KRAI System v{settings.VERSION}")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests and responses"""
    start_time = time.time()

    # Log request
    # Do not read request body here to avoid interfering with FastAPI's body parsing.
    body = None

    logger.info("log_requests: before call_next")
    log_api_request(
        method=request.method,
        path=str(request.url),
        params=dict(request.query_params),
        body=body
    )

    # Process request
    try:
        response = await call_next(request)
        logger.info("log_requests: after call_next")
        process_time = time.time() - start_time

        # Log response
        log_api_response(
            path=str(request.url.path),
            status_code=response.status_code,
            response_data={"process_time": process_time}
        )

        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url.path} - {str(e)}")
        log_api_response(
            path=str(request.url.path),
            status_code=500,
            error=str(e)
        )
        raise


# Add Basic Auth middleware if enabled
if settings.ENABLE_BASIC_AUTH:
    app.add_middleware(
        BasicAuthMiddleware,
        username=settings.BASIC_AUTH_USERNAME,
        password=settings.BASIC_AUTH_PASSWORD,
    )
    logger.info("Basic Authentication enabled")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

logger.info("API routes configured")

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return JSONResponse({
        "message": "KRAI Production System API v0.6",
        "status": "active",
        "docs": "/docs",
        "version": settings.VERSION
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return JSONResponse({
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": "2024-09-19T05:05:00Z"
    })


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    init_db()
    logger.info("KRAI System backend starting up...")
    logger.info(f"Version: {settings.VERSION}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Allowed hosts: {settings.ALLOWED_HOSTS}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("KRAI System backend shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
