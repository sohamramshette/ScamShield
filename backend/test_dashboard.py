import sys
sys.path.insert(0, '/app')
from app.db.session import SessionLocal
from app.services.dashboard_service import DashboardService
from app.models.user import User

def run():
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        print("No users found")
        return
    service = DashboardService(db, user)
    print(service.get_stats())

if __name__ == "__main__":
    run()
