import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.event import Event

router = APIRouter(prefix="/events", tags=["events"])


class EventResponse(BaseModel):
    id: uuid.UUID
    camera_id: uuid.UUID
    event_type: str
    confidence: float
    details: dict | None
    frame_path: str | None
    ai_provider: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[EventResponse])
async def list_events(
    camera_id: uuid.UUID | None = Query(None),
    event_type: str | None = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Event).order_by(Event.created_at.desc()).limit(limit)
    if camera_id:
        query = query.where(Event.camera_id == camera_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
    result = await db.execute(query)
    return result.scalars().all()
