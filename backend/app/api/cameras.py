import uuid
from datetime import datetime
from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.camera import Camera
from app.services.camera.rtsp import check_stream

router = APIRouter(prefix="/cameras", tags=["cameras"])


def _redact_rtsp_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.username or parsed.password:
        netloc = parsed.hostname or ""
        if parsed.port:
            netloc += f":{parsed.port}"
        return urlunparse(parsed._replace(netloc=netloc))
    return url


def _validate_rtsp_scheme(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("rtsp", "rtsps"):
        raise ValueError("Only rtsp:// and rtsps:// URLs are allowed")
    if not parsed.hostname:
        raise ValueError("RTSP URL must include a hostname")
    return url


class CameraCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    rtsp_url: str = Field(max_length=1024)
    onvif_host: str | None = Field(None, max_length=255)
    onvif_port: int = Field(80, ge=1, le=65535)
    username: str | None = Field(None, max_length=255)
    password: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)

    @field_validator("rtsp_url")
    @classmethod
    def validate_rtsp_url(cls, v: str) -> str:
        return _validate_rtsp_scheme(v)


class CameraUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    rtsp_url: str | None = Field(None, max_length=1024)
    location: str | None = Field(None, max_length=255)
    is_active: bool | None = None

    @field_validator("rtsp_url")
    @classmethod
    def validate_rtsp_url(cls, v: str | None) -> str | None:
        if v is not None:
            return _validate_rtsp_scheme(v)
        return v


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
    last_frame: str | None = None

    model_config = {"from_attributes": True}

    @field_validator("rtsp_url")
    @classmethod
    def redact_credentials(cls, v: str) -> str:
        return _redact_rtsp_url(v)


@router.get("", response_model=list[CameraResponse])
async def list_cameras(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).order_by(Camera.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=CameraResponse, status_code=201)
async def create_camera(payload: CameraCreate, db: AsyncSession = Depends(get_db)):
    count_result = await db.execute(select(func.count(Camera.id)))
    if (count_result.scalar() or 0) >= settings.max_concurrent_streams:
        raise HTTPException(status_code=409, detail="Camera limit reached")
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
