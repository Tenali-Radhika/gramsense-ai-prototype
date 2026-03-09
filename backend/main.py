from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging
from datetime import datetime

from api import prices, forecast, recommendation, export, feedback
from aws_integration import get_aws_service
from middleware import rate_limit_middleware, rate_limiter
from data_ingestion import get_all_cache_stats
from session_manager import session_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="GramSense AI", description="Rural Market Intelligence Platform")

# GZip compression middleware for response optimization
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting middleware (applied first)
@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    """Apply rate limiting to all requests."""
    return await rate_limit_middleware(request, call_next)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing information."""
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url.path}")
    logger.info(f"Client: {request.client.host if request.client else 'unknown'}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response details
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    # Add custom header with processing time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(prices.router)
app.include_router(forecast.router)
app.include_router(recommendation.router)
app.include_router(export.router)
app.include_router(feedback.router)

@app.get("/")
def root():
    return {"message": "GramSense AI Prototype Running"}

@app.get("/health")
def health():
    """Health check endpoint with system status."""
    aws_status = "configured" if get_aws_service().s3_client else "not configured"
    cache_stats = get_all_cache_stats()
    rate_limit_stats = rate_limiter.get_stats()
    session_stats = session_manager.get_stats()
    
    return {
        "status": "ok",
        "version": "1.0.0",
        "aws_integration": aws_status,
        "cache": cache_stats,
        "rate_limiting": rate_limit_stats,
        "sessions": session_stats,
        "features": {
            "request_logging": True,
            "rate_limiting": True,
            "response_compression": True,
            "data_caching": True,
            "conversation_history": True,
        }
    }