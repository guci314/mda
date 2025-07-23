"""System Events API - Provides access to audit trail"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


class EventResponse(BaseModel):
    """System event response"""
    id: int
    timestamp: str
    event_type: str
    entity_type: str
    entity_id: str
    description: str
    details: Optional[dict] = None
    severity: str


class EventsListResponse(BaseModel):
    """List of events response"""
    events: List[EventResponse]
    total: int


@router.get("", response_model=EventsListResponse)
async def list_events(
    request: Request, 
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None, regex="^(info|warning|error)$")
):
    """List recent system events"""
    try:
        persistence_manager = request.app.state.persistence_manager
        
        events = persistence_manager.get_recent_events(
            limit=limit,
            entity_type=entity_type,
            severity=severity
        )
        
        return EventsListResponse(
            events=[EventResponse(**event.to_dict()) for event in events],
            total=len(events)
        )
    except Exception as e:
        logger.error(f"Error listing events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cleanup")
async def cleanup_old_events(
    request: Request,
    days: int = Query(30, ge=1, le=365)
):
    """Delete events older than specified days"""
    try:
        persistence_manager = request.app.state.persistence_manager
        
        persistence_manager.cleanup_old_events(days=days)
        
        return {
            "message": f"Old events cleaned up successfully (older than {days} days)"
        }
    except Exception as e:
        logger.error(f"Error cleaning up events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))