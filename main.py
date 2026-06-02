from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Government Contracts & Grants API",
    description="Real-time access to US Government contracts, grants, and agency spending data from USASpending.gov",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

USASPENDING_BASE = "https://api.usaspending.gov/api/v2"

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "message": "Government Contracts & Grants API",
        "version": "2.0.0",
        "data_source": "USASpending.gov (live)",
        "docs": "/docs",
        "endpoints": {
            "contracts": "/contracts",
            "grants": "/grants",
            "agencies": "/agencies",
            "health": "/health"
        }
    }

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{USASPENDING_BASE}/")
            upstream = "ok" if r.status_code == 200 else f"status {r.status_code}"
    except Exception as e:
        upstream = f"error: {str(e)}"
    return {"status": "healthy", "upstream_usaspending": upstream, "version": "2.0.0"}

@app.get("/contracts")
async def get_contracts(
    agency: Optional[str] = Query(None, description="Filter by awarding agency name (e.g. 'NASA', 'Department of Defense')"),
    amount_min: Optional[float] = Query(None, description="Minimum award amount in USD"),
    amount_max: Optional[float] = Query(None, description="Maximum award amount in USD"),
    keyword: Optional[str] = Query(None, description="Keyword search in contract description"),
    limit: int = Query(10, ge=1, le=100, description="Number of results (max 100)")
):
    """
    Fetch real US government contracts from USASpending.gov.
    Returns the largest contracts by default, sorted by award amount descending.
    Filter by agency, dollar amount, or keyword.
    """
    filters = {
        "award_type_codes": ["A", "B", "C", "D"]  # Contract types only
    }

    if agency:
        filters["agencies"] = [{"type": "awarding", "tier": "toptier", "name": agency}]

    if amount_min or amount_max:
        amt = {}
        if amount_min:
            amt["lower_bound"] = amount_min
        if amount_max:
            amt["upper_bound"] = amount_max
        filters["award_amounts"] = [amt]

    if keyword:
        filters["keywords"] = [keyword]

    payload = {
        "filters": filters,
        "fields": [
            "Award ID",
            "Recipient Name",
            "Award Amount",
            "Awarding Agency",
            "Description",
            "Start Date",
            "End Date",
            "Place of Performance City Name",
            "Place of Performance State Code"
        ],
        "page": 1,
        "limit": limit,
        "sort": "Award Amount",
        "order": "desc"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{USASPENDING_BASE}/search/spending_by_award/",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for r in data.get("results", []):
            results.append({
                "contract_id": r.get("Award ID", ""),
                "recipient": r.get("Recipient Name", ""),
                "agency": r.get("Awarding Agency", ""),
                "amount_usd": r.get("Award Amount", 0),
                "description": r.get("Description", ""),
                "start_date": r.get("Start Date", ""),
                "end_date": r.get("End Date", ""),
                "location": f"{r.get('Place of Performance City Name', '')}, {r.get('Place of Performance State Code', '')}".strip(", ")
            })

        return {
            "count": len(results),
            "source": "USASpending.gov",
            "contracts": results
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"USASpending.gov error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Contracts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/grants")
async def get_grants(
    agency: Optional[str] = Query(None, description="Filter by awarding agency name"),
    amount_min: Optional[float] = Query(None, description="Minimum grant amount in USD"),
    keyword: Optional[str] = Query(None, description="Keyword search in grant description"),
    limit: int = Query(10, ge=1, le=100, description="Number of results (max 100)")
):
    """
    Fetch real US government grants from USASpending.gov.
    Returns the largest grants by default, sorted by award amount descending.
    """
    filters = {
        "award_type_codes": ["02", "03", "04", "05"]  # Grant type codes
    }

    if agency:
        filters["agencies"] = [{"type": "awarding", "tier": "toptier", "name": agency}]

    if amount_min:
        filters["award_amounts"] = [{"lower_bound": amount_min}]

    if keyword:
        filters["keywords"] = [keyword]

    payload = {
        "filters": filters,
        "fields": [
            "Award ID",
            "Recipient Name",
            "Award Amount",
            "Awarding Agency",
            "Description",
            "Start Date",
            "End Date"
        ],
        "page": 1,
        "limit": limit,
        "sort": "Award Amount",
        "order": "desc"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{USASPENDING_BASE}/search/spending_by_award/",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for r in data.get("results", []):
            results.append({
                "grant_id": r.get("Award ID", ""),
                "recipient": r.get("Recipient Name", ""),
                "agency": r.get("Awarding Agency", ""),
                "amount_usd": r.get("Award Amount", 0),
                "description": r.get("Description", ""),
                "start_date": r.get("Start Date", ""),
                "end_date": r.get("End Date", "")
            })

        return {
            "count": len(results),
            "source": "USASpending.gov",
            "grants": results
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"USASpending.gov error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Grants error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agencies")
async def get_agencies(
    limit: int = Query(50, ge=1, le=100, description="Number of agencies to return")
):
    """
    Fetch list of US government agencies from USASpending.gov.
    Returns agency names, codes, and abbreviations.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{USASPENDING_BASE}/references/toptier_agencies/")
            response.raise_for_status()
            data = response.json()

        agencies = data.get("results", [])[:limit]
        results = []
        for a in agencies:
            results.append({
                "agency_code": a.get("toptier_code", ""),
                "name": a.get("agency_name", ""),
                "abbreviation": a.get("abbreviation", ""),
                "active_fy": a.get("active_fy", ""),
                "budget_authority_amount": a.get("budget_authority_amount", 0),
                "obligated_amount": a.get("obligated_amount", 0),
            })

        return {
            "count": len(results),
            "source": "USASpending.gov",
            "agencies": results
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"USASpending.gov error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Agencies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000))
    )
