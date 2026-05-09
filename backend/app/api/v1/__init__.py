from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.pets import router as pets_router
from app.api.v1.checkins import router as checkins_router
from app.api.v1.baselines import router as baselines_router
from app.api.v1.warnings import router as warnings_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.vaccines import router as vaccines_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.medical import router as medical_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(pets_router)
router.include_router(checkins_router)
router.include_router(baselines_router)
router.include_router(warnings_router)
router.include_router(conversations_router)
router.include_router(vaccines_router)
router.include_router(uploads_router)
router.include_router(medical_router)