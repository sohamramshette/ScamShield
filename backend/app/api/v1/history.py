from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.website_scan import WebsiteScan

router = APIRouter()


@router.get("/", tags=["History"])
def get_history(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    scans = (
        db.query(WebsiteScan)
        .filter(WebsiteScan.user_id == current_user.id)
        .order_by(WebsiteScan.created_at.desc())
        .all()
    )
    # In a full implementation, union with QR and UPI scans
    return scans
