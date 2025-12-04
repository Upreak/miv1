from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ClientCreate(BaseModel):
    name: str
    billing_address: Optional[str] = None
    status: Optional[str] = None
    corporate_identity: Optional[dict] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    account_manager_id: str
    created_from_lead_id: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    billing_address: Optional[str] = None
    status: Optional[str] = None
    corporate_identity: Optional[dict] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    account_manager_id: Optional[str] = None
    created_from_lead_id: Optional[str] = None

class ClientResponse(BaseModel):
    id: str
    name: str
    billing_address: Optional[str] = None
    status: Optional[str] = None
    corporate_identity: Optional[dict] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    account_manager_id: str
    created_from_lead_id: Optional[str] = None

    class Config:
        from_attributes = True