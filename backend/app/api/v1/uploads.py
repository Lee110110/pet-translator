import uuid
import pathlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_pet
from app.core.config import get_settings
from app.core.utils import calculate_age
from app.models.pet import Pet
from app.services.vision_service import analyze_image

settings = get_settings()
router = APIRouter(prefix="/pets/{pet_id}/uploads", tags=["文件上传"])


class AnalyzeImageRequest(BaseModel):
    image_url: str
    analysis_type: str  # food_bowl, litter_box, vomit


@router.post("/image")
async def upload_image(
    pet_id: int,
    file: UploadFile = File(...),
    pet: Pet = Depends(get_current_pet),
):
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/WebP 格式")

    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"图片大小不能超过 {settings.MAX_IMAGE_SIZE // 1024 // 1024}MB")

    ext = "jpg" if file.content_type == "image/jpeg" else ("png" if file.content_type == "image/png" else "webp")
    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = pathlib.Path(settings.UPLOAD_DIR) / "pet_images" / str(pet_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / filename
    with open(file_path, "wb") as f:
        f.write(content)

    url = f"/uploads/pet_images/{pet_id}/{filename}"
    return {"url": url, "filename": filename}


@router.post("/analyze-image")
async def analyze_uploaded_image(
    pet_id: int,
    req: AnalyzeImageRequest,
    pet: Pet = Depends(get_current_pet),
):
    # Resolve image path from URL
    image_path = pathlib.Path(settings.UPLOAD_DIR) / req.image_url.lstrip("/")

    if not image_path.exists():
        raise HTTPException(status_code=404, detail="图片不存在")

    pet_context = {
        "breed": pet.breed or "未知品种",
        "age": calculate_age(pet.birthday) if pet.birthday else "未知",
    }

    result = await analyze_image(str(image_path), req.analysis_type, pet_context)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result