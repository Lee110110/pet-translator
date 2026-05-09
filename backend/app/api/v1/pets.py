from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user, get_current_pet
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.models.pet import Pet
from app.schemas.pet import PetCreate, PetUpdate, PetOut

router = APIRouter(prefix="/pets", tags=["宠物档案"])


@router.post("", response_model=PetOut)
async def create_pet(req: PetCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pet = Pet(user_id=current_user.id, **req.model_dump())
    db.add(pet)
    await db.commit()
    await db.refresh(pet)
    return pet


@router.get("", response_model=list[PetOut])
async def list_pets(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pet).where(Pet.user_id == current_user.id, Pet.is_active == True).order_by(Pet.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{pet_id}", response_model=PetOut)
async def get_pet(pet: Pet = Depends(get_current_pet)):
    return pet


@router.put("/{pet_id}", response_model=PetOut)
async def update_pet(req: PetUpdate, pet: Pet = Depends(get_current_pet), db: AsyncSession = Depends(get_db)):
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pet, key, value)
    await db.commit()
    await db.refresh(pet)
    return pet


@router.delete("/{pet_id}")
async def delete_pet(pet: Pet = Depends(get_current_pet), db: AsyncSession = Depends(get_db)):
    pet.is_active = False
    await db.commit()
    return {"detail": "已删除"}