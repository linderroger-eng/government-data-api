import httpx
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio

class USASpendingService:
    """Service to fetch and clean data from USASpending.gov API"""
    
    def __init__(self):
        self.base_url = os.getenv("USASPENDING_BASE_URL", "https://api.usaspending.gov/api/v2/")
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def get_contracts(
        self, 
        agency: Optional[str] = None,
        amount_min: Optional[float] = None,
        amount_max: Optional[float] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch contracts from USASpending.gov with filtering"""
        
        # Build search filters
        filters = {}
        
        if agency:
            filters["agencies"] = [{"type": "awarding", "tier": "toptier", "name": agency}]
        
        if amount_min or amount_max:
            award_amounts = []
            if amount_min:
                award_amounts.append({"lower_bound": amount_min})
            if amount_max:
                award_amounts.append({"upper_bound": amount_max})
            filters["award_amounts"] = award_amounts
        
        if date_from or date_to:
            time_period = []
            if date_from:
                time_period.append({"start_date": date_from})
            if date_to:
                time_period.append({"end_date": date_to})
            filters["time_period"] = time_period
        
        # Build request payload
        payload = {
            "filters": filters,
            "fields": [
                "Award ID",
                "Recipient Name", 
                "Award Amount",
                "Description",
                "Start Date",
                "End Date",
                "Awarding Agency",
                "Place of Performance City Name",
                "Place of Performance State Code"
            ],
            "page": 1,
            "limit": min(limit, 100),  # USASpending.gov max is 100 per request
            "sort": "Award Amount",
            "order": "desc"
        }
        
        try:
            url = f"{self.base_url}search/spending_by_award/"
            response = await self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            # Clean and normalize the data
            cleaned_contracts = []
            for result in results:
                contract = {
                    "contract_id": result.get("Award ID", ""),
                    "agency_name": result.get("Awarding Agency", ""),
                    "recipient_name": result.get("Recipient Name", ""),
                    "description": result.get("Description", ""),
                    "award_amount": float(result.get("Award Amount", 0)),
                    "start_date": self._parse_date(result.get("Start Date")),
                    "end_date": self._parse_date(result.get("End Date")),
                    "place_of_performance": f"{result.get('Place of Performance City Name', '')}, {result.get('Place of Performance State Code', '')}".strip(", ")
                }
                cleaned_contracts.append(contract)
            
            return cleaned_contracts
            
        except Exception as e:
            print(f"Error fetching contracts: {e}")
            return []
    
    async def get_grants(
        self,
        agency: Optional[str] = None,
        amount_min: Optional[float] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch grants data (using contracts endpoint with grant filtering)"""
        
        # USASpending.gov doesn't have a separate grants endpoint
        # We'll filter contracts for grant-type awards
        filters = {
            "award_type_codes": ["06", "07", "08", "09", "10", "11"]  # Grant type codes
        }
        
        if agency:
            filters["agencies"] = [{"type": "awarding", "tier": "toptier", "name": agency}]
        
        if amount_min:
            filters["award_amounts"] = [{"lower_bound": amount_min}]
        
        payload = {
            "filters": filters,
            "fields": [
                "Award ID",
                "Recipient Name",
                "Award Amount", 
                "Description",
                "Start Date",
                "End Date",
                "Awarding Agency"
            ],
            "page": 1,
            "limit": min(limit, 100),
            "sort": "Award Amount",
            "order": "desc"
        }
        
        try:
            url = f"{self.base_url}search/spending_by_award/"
            response = await self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            cleaned_grants = []
            for result in results:
                grant = {
                    "grant_id": result.get("Award ID", ""),
                    "agency_name": result.get("Awarding Agency", ""),
                    "recipient_name": result.get("Recipient Name", ""),
                    "title": result.get("Description", "")[:100] + "..." if result.get("Description") else "",
                    "description": result.get("Description", ""),
                    "award_amount": float(result.get("Award Amount", 0)),
                    "start_date": self._parse_date(result.get("Start Date")),
                    "end_date": self._parse_date(result.get("End Date")),
                    "category": category or "General"
                }
                cleaned_grants.append(grant)
            
            return cleaned_grants
            
        except Exception as e:
            print(f"Error fetching grants: {e}")
            return []
    
    async def get_agencies(self) -> List[Dict[str, Any]]:
        """Fetch list of government agencies"""
        
        try:
            url = f"{self.base_url}references/toptier_agencies/"
            response = await self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            agencies = data.get("results", [])
            
            cleaned_agencies = []
            for agency in agencies:
                cleaned_agency = {
                    "agency_code": agency.get("toptier_code", ""),
                    "agency_name": agency.get("name", ""),
                    "total_contracts": 0,  # Would need separate call to calculate
                    "total_grants": 0,     # Would need separate call to calculate  
                    "total_spending": 0    # Would need separate call to calculate
                }
                cleaned_agencies.append(cleaned_agency)
            
            return cleaned_agencies[:50]  # Return top 50 agencies
            
        except Exception as e:
            print(f"Error fetching agencies: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get API statistics"""
        return {
            "contracts": 1000000,  # Placeholder - would calculate from database
            "grants": 500000,      # Placeholder - would calculate from database
            "agencies": 50,        # Placeholder - would calculate from database
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()