from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/frames", tags=["frames"])

FRAMES_DIR = Path("/app/data/frames")
_FRAMES_DIR_RESOLVED = FRAMES_DIR.resolve()


@router.get("/{filename}")
async def get_frame(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = (FRAMES_DIR / filename).resolve()
    if not path.is_relative_to(_FRAMES_DIR_RESOLVED):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Frame not found")
    return FileResponse(path, media_type="image/jpeg")
