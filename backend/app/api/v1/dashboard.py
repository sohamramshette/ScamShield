from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.dashboard_service import DashboardService

router = APIRouter()

@router.get("/stats", tags=["Dashboard"])
def get_dashboard_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = DashboardService(db, current_user)
    return service.build_dashboard()
