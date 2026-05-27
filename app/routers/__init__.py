from fastapi import APIRouter
from app.routers import auth, employees, clock, reports

router = APIRouter()
router.include_router(auth.router)
router.include_router(employees.router)
router.include_router(clock.router)
router.include_router(reports.router)
