from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv

from database import get_db, engine
from models import Base
from services.usaspending_service import USASpendingService
from services.cache_service import CacheService
from schemas import ContractResponse, GrantResponse, AgencyResponse

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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