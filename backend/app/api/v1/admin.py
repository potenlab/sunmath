from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.history import AdminSettings
from app.schemas.admin import SettingResponse, SettingUpdate, SettingsListResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/settings", response_model=SettingsListResponse)
async def list_settings(db: AsyncSession = Depends(get_db)):
    """List all admin settings."""
    result = await db.execute(select(AdminSettings))
    settings = result.scalars().all()
    return SettingsListResponse(
        settings=[SettingResponse.model_validate(s) for s in settings]
    )


@router.put("/settings/{key}", response_model=SettingResponse)
async def update_setting(
    key: str, body: SettingUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an admin setting by key."""
    result = await db.execute(select(AdminSettings).where(AdminSettings.key == key))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    setting.value = body.value
    db.add(setting)
    await db.flush()
    await db.refresh(setting)
    return SettingResponse.model_validate(setting)
