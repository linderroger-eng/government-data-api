from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import logging
import time
import uuid
from dotenv import load_dotenv

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from database import get_db, engine
from models import Base
from schemas import ContractResponse, GrantResponse, AgencyResponse
from usaspending_service import USASpendingService
from cache_service import CacheService

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Government Data API",
    description="Clean, reliable access to US Government spending data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dashboard access
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security middleware  
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Allow all hosts for simplicity
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request_id to logging context
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.request_id = request_id
        return record
    logging.setLogRecordFactory(record_factory)
    
    start_time = time.time()
    logger.info(f"Request started: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Request completed: {response.status_code} in {process_time:.3f}s")
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY" 
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed: {str(e)} after {process_time:.3f}s")
        raise
    finally:
        logging.setLogRecordFactory(old_factory)

# Initialize services
usaspending_service = USASpendingService()
cache_service = CacheService()

@app.get("/")
async def root():
    """API Status and information"""
    return {
        "message": "Government Data API - Clean access to US Government spending",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "contracts": "/contracts",
            "grants": "/grants", 
            "agencies": "/agencies"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for Railway deployment monitoring"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {},
            "version": "1.0.0"
        }
        
        # Test database connection
        try:
            from database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            health_status["services"]["database"] = "connected"
        except Exception as e:
            health_status["services"]["database"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Test cache service
        try:
            test_key = f"health_test_{int(time.time())}"
            cache_service.set(test_key, "ok", ttl=60)
            cache_result = cache_service.get(test_key)
            cache_service.delete(test_key)  # Cleanup
            
            if cache_result == "ok":
                health_status["services"]["cache"] = "working"
            else:
                health_status["services"]["cache"] = "warning"
        except Exception as e:
            health_status["services"]["cache"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Test USASpending API connection
        try:
            # Simple connectivity test to external API
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://api.usaspending.gov/api/v2/")
                if response.status_code == 200:
                    health_status["services"]["usaspending_api"] = "connected"
                else:
                    health_status["services"]["usaspending_api"] = f"status_code: {response.status_code}"
        except Exception as e:
            health_status["services"]["usaspending_api"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Determine overall health
        if health_status["status"] == "degraded":
            return HTTPException(status_code=503, detail=health_status)
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/contracts", response_model=List[ContractResponse])
async def get_contracts(
    agency: Optional[str] = Query(None, description="Filter by agency (e.g., 'NASA', 'DOD')"),
    amount_min: Optional[float] = Query(None, description="Minimum contract amount"),
    amount_max: Optional[float] = Query(None, description="Maximum contract amount"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, le=1000, description="Number of results (max 1000)"),
    db: Session = Depends(get_db)
):
    """
    Get government contracts with optional filtering
    
    Example: /contracts?agency=NASA&amount_min=1000000&limit=50
    """
    try:
        # Check cache first
        cache_key = f"contracts:{agency}:{amount_min}:{amount_max}:{date_from}:{date_to}:{limit}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return cached_result
        
        # Fetch from service
        contracts = await usaspending_service.get_contracts(
            agency=agency,
            amount_min=amount_min,
            amount_max=amount_max,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        
        # Cache result for 1 hour
        cache_service.set(cache_key, contracts, ttl=3600)
        
        return contracts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contracts: {str(e)}")

@app.get("/grants", response_model=List[GrantResponse])
async def get_grants(
    agency: Optional[str] = Query(None, description="Filter by agency"),
    amount_min: Optional[float] = Query(None, description="Minimum grant amount"),
    category: Optional[str] = Query(None, description="Grant category"),
    limit: int = Query(100, le=1000, description="Number of results"),
    db: Session = Depends(get_db)
):
    """
    Get government grants with optional filtering
    
    Example: /grants?agency=NSF&amount_min=50000&category=research
    """
    try:
        cache_key = f"grants:{agency}:{amount_min}:{category}:{limit}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return cached_result
            
        grants = await usaspending_service.get_grants(
            agency=agency,
            amount_min=amount_min,
            category=category,
            limit=limit
        )
        
        cache_service.set(cache_key, grants, ttl=3600)
        return grants
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching grants: {str(e)}")

@app.get("/agencies", response_model=List[AgencyResponse])
async def get_agencies(db: Session = Depends(get_db)):
    """
    Get list of all government agencies with spending data
    
    Example: /agencies
    """
    try:
        cached_result = cache_service.get("agencies:all")
        if cached_result:
            return cached_result
            
        agencies = await usaspending_service.get_agencies()
        cache_service.set("agencies:all", agencies, ttl=86400)  # Cache for 24 hours
        
        return agencies
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agencies: {str(e)}")

@app.get("/stats")
async def get_api_stats():
    """API usage statistics and data freshness"""
    try:
        stats = await usaspending_service.get_stats()
        return {
            "total_contracts": stats.get("contracts", 0),
            "total_grants": stats.get("grants", 0),
            "total_agencies": stats.get("agencies", 0),
            "last_updated": stats.get("last_updated"),
            "data_sources": ["USASpending.gov", "Grants.gov"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_RELOAD", "True").lower() == "true"
    )