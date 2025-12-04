from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date, datetime

class LeadCreate(BaseModel):
    owner_id: str
    company_name: str
    contact_person: str
    contact_email: str
    contact_phone: str
    status: Optional[str] = None
    service_type: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    probability: Optional[int] = None
    expected_close_date: Optional[date] = None
    next_follow_up: Optional[datetime] = None
    source: Optional[str] = None

class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[str] = None
    service_type: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    probability: Optional[int] = None
    expected_close_date: Optional[date] = None
    next_follow_up: Optional[datetime] = None
    source: Optional[str] = None

class LeadResponse(BaseModel):
    id: str
    owner_id: str
    company_name: str
    contact_person: str
    contact_email: str
    contact_phone: str
    status: Optional[str] = None
    service_type: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    probability: Optional[int] = None
    expected_close_date: Optional[date] = None
    next_follow_up: Optional[datetime] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True