from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.schemas.leads import LeadCreate, LeadUpdate, LeadResponse
from app.schemas.clients import ClientCreate, ClientUpdate, ClientResponse
from app.models.leads import Lead
from app.models.clients import Client
from app.models.sales_tasks import SalesTask
from uuid import UUID
from datetime import datetime, date

router = APIRouter()

@router.get("/leads", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    owner_id: Optional[str] = None,
    status: Optional[str] = None,
    service_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Lead)
        
        if owner_id:
            query = query.filter(Lead.owner_id == UUID(owner_id))
        
        if status:
            query = query.filter(Lead.status == status)
        
        if service_type:
            query = query.filter(Lead.service_type == service_type)
        
        leads = query.offset(skip).limit(limit).all()
        return leads
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving leads: {str(e)}"
        )

@router.post("/leads", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db)
):
    try:
        db_lead = Lead(
            owner_id=UUID(lead.owner_id),
            company_name=lead.company_name,
            contact_person=lead.contact_person,
            contact_email=lead.contact_email,
            contact_phone=lead.contact_phone,
            status=lead.status or "New",
            service_type=lead.service_type,
            estimated_value=lead.estimated_value,
            probability=lead.probability,
            expected_close_date=lead.expected_close_date,
            next_follow_up=lead.next_follow_up,
            source=lead.source
        )
        
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        
        return db_lead
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating lead: {str(e)}"
        )

@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: Session = Depends(get_db)
):
    try:
        lead = db.query(Lead).filter(Lead.id == UUID(lead_id)).first()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        return lead
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving lead: {str(e)}"
        )

@router.put("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db)
):
    try:
        lead = db.query(Lead).filter(Lead.id == UUID(lead_id)).first()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        for field, value in lead_update.dict(exclude_unset=True).items():
            setattr(lead, field, value)
        
        db.commit()
        db.refresh(lead)
        
        return lead
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating lead: {str(e)}"
        )

@router.delete("/leads/{lead_id}")
async def delete_lead(
    lead_id: str,
    db: Session = Depends(get_db)
):
    try:
        lead = db.query(Lead).filter(Lead.id == UUID(lead_id)).first()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        db.delete(lead)
        db.commit()
        
        return {"message": "Lead deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting lead: {str(e)}"
        )

@router.post("/clients", response_model=ClientResponse)
async def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db)
):
    try:
        db_client = Client(
            name=client.name,
            billing_address=client.billing_address,
            status=client.status or "Active",
            corporate_identity=client.corporate_identity,
            contract_start_date=client.contract_start_date,
            contract_end_date=client.contract_end_date,
            account_manager_id=UUID(client.account_manager_id),
            created_from_lead_id=UUID(client.created_from_lead_id) if client.created_from_lead_id else None
        )
        
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        
        return db_client
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating client: {str(e)}"
        )

@router.get("/clients", response_model=List[ClientResponse])
async def get_clients(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    account_manager_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Client)
        
        if status:
            query = query.filter(Client.status == status)
        
        if account_manager_id:
            query = query.filter(Client.account_manager_id == UUID(account_manager_id))
        
        clients = query.offset(skip).limit(limit).all()
        return clients
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving clients: {str(e)}"
        )

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    db: Session = Depends(get_db)
):
    try:
        client = db.query(Client).filter(Client.id == UUID(client_id)).first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        return client
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving client: {str(e)}"
        )

@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_update: ClientUpdate,
    db: Session = Depends(get_db)
):
    try:
        client = db.query(Client).filter(Client.id == UUID(client_id)).first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        for field, value in client_update.dict(exclude_unset=True).items():
            setattr(client, field, value)
        
        db.commit()
        db.refresh(client)
        
        return client
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating client: {str(e)}"
        )

@router.get("/leads/{lead_id}/tasks")
async def get_lead_tasks(
    lead_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        tasks = db.query(SalesTask).filter(SalesTask.lead_id == UUID(lead_id)).offset(skip).limit(limit).all()
        return tasks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving lead tasks: {str(e)}"
        )

@router.post("/leads/{lead_id}/tasks")
async def create_lead_task(
    lead_id: str,
    task_title: str,
    due_date: date,
    assigned_to: str,
    db: Session = Depends(get_db)
):
    try:
        task = SalesTask(
            lead_id=UUID(lead_id),
            title=task_title,
            is_completed=False,
            due_date=due_date,
            assigned_to=UUID(assigned_to)
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return task
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating lead task: {str(e)}"
        )