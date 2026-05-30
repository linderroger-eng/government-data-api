from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ContractResponse(BaseModel):
    contract_id: str
    agency_name: str
    recipient_name: str
    description: Optional[str]
    award_amount: float
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    place_of_performance: Optional[str]
    
    class Config:
        from_attributes = True

class GrantResponse(BaseModel):
    grant_id: str
    agency_name: str
    recipient_name: str
    title: Optional[str]
    description: Optional[str]
    award_amount: float
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    category: Optional[str]
    
    class Config:
        from_attributes = True

class AgencyResponse(BaseModel):
    agency_code: str
    agency_name: str
    total_contracts: int
    total_grants: int
    total_spending: float
    
    class Config:
        from_attributes = True