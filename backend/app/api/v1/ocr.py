from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.api.deps_auth import require_role
from app.models.user import User, UserRole
from app.schemas.ocr import OCRResponse
from app.services.ocr import OCRService

router = APIRouter(prefix="/ocr", tags=["ocr"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/recognize", response_model=OCRResponse)
async def recognize_image(
    file: UploadFile = File(...),
    _: User = Depends(require_role(UserRole.admin, UserRole.student)),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    try:
        service = OCRService()
        result = await service.recognize(image_bytes, file.content_type)
        return OCRResponse(**result)
    except RuntimeError as e:
        status = 429 if "rate limited" in str(e).lower() else 500
        raise HTTPException(status_code=status, detail=str(e))
