"""
Paksa AI Assistant - Main Application

This is the entry point for the Paksa AI Assistant application.
Copyright © 2025 Paksa IT Solutions (www.paksa.com.pk)
"""
import os
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    # Startup
    logger.info("Starting Paksa AI Assistant...")
    logger.info(f"Environment: {os.getenv('APP_ENV', 'development')}")
    
    # Initialize services
    await initialize_services()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Paksa AI Assistant...")
    await shutdown_services()

# Create FastAPI app
app = FastAPI(
    title="Paksa AI Assistant",
    description="AI-Powered E-commerce Customer Support Solution",
    version="1.0.0",
    contact={
        "name": "Paksa IT Solutions",
        "url": "https://www.paksa.com.pk",
        "email": "info@paksa.com.pk",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://www.paksa.com.pk/license",
    },
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Paksa AI Assistant",
        "version": "1.0.0"
    }

# Import and include routers
from app.api import router as api_router
app.include_router(api_router, prefix=os.getenv("API_PREFIX", "/api/v1"))

# Mount static files (if any)
app.mount("/static", StaticFiles(directory="static"), name="static")

async def initialize_services():
    """Initialize application services"""
    # Initialize database connection
    # Initialize cache
    # Initialize AI models
    logger.info("Initializing services...")

async def shutdown_services():
    """Shutdown application services"""
    # Close database connections
    # Clean up resources
    logger.info("Shutting down services...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
