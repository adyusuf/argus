import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.camera import Camera
from app.services.camera.rtsp import check_stream

router = APIRouter(prefix="/cameras", tags=["cameras"])


class CameraCreate(BaseModel):
    name: str
    rtsp_url: str
    onvif_host: str | None = None
    onvif_port: int = 80
    username: str | None = None
    password: str | None = None
    location: str | None = None


class CameraUpdate(BaseModel):
    name: str | None = None
    rtsp_url: str | None = None
    location: str | None = None
    is_active: bool | None = None


class CameraResponse(BaseModel):
    id: uuid.UUID
    name: str
    rtsp_url: str
    onvif_host: str | None
    onvif_port: int
    location: str | None
    is_active: bool
    status: str
    last_seen: datetime | None = None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[CameraResponse])
async def list_cameras(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).order_by(Camera.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=CameraResponse, status_code=201)
async def create_camera(payload: CameraCreate, db: AsyncSession = Depends(get_db)):
    camera = Camera(**payload.model_dump())
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    return camera


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: uuid.UUID,
    payload: CameraUpdate,
    db: AsyncSession = Depends(get_db),
):
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(camera, field, value)
    await db.commit()
    await db.refresh(camera)
    return camera


@router.delete("/{camera_id}", status_code=204)
async def delete_camera(camera_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    await db.delete(camera)
    await db.commit()


@router.post("/{camera_id}/check", response_model=dict)
async def check_camera_stream(camera_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    camera = await db.get(Camera, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    reachable = check_stream(camera.rtsp_url)
    camera.status = "online" if reachable else "offline"
    await db.commit()
    return {"camera_id": str(camera_id), "reachable": reachable, "status": camera.status}
