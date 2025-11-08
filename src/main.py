"""
FastAPI application for Webex Calling Security AI
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from src.config import settings
from src.database import init_db_async
from src.utils.logger import setup_logger

# Import routers (will create these)
# from src.api.routes import cdr, alerts, users, detection

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI"""
    # Startup
    logger.info("Starting Webex Calling Security AI API...")
    logger.info(f"Environment: {settings.environment}")

    # Initialize database
    await init_db_async()

    yield

    # Shutdown
    logger.info("Shutting down Webex Calling Security AI API...")


# Create FastAPI app
app = FastAPI(
    title="Webex Calling Security AI",
    description="AI-powered security and anomaly detection for Webex Calling",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "Webex Calling Security AI",
        "version": "0.1.0",
        "environment": settings.environment,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "0.1.0",
    }


# Include routers
from src.api.routes import alerts

app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
# app.include_router(cdr.router, prefix="/api/v1/cdr", tags=["CDR"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(detection.router, prefix="/api/v1/detection", tags=["Detection"])


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "status_code": 500,
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
