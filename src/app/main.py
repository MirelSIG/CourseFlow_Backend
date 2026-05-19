from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1 import routes_admin
import os
from app.db.session import init_db
from app.models.user import User
from app.utils.enums import Role
from app.core.security import hash_password

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
def on_startup():
    init_db(settings.SQLALCHEMY_DATABASE_URI)
    
    # Bootstrap superadmin
    superadmin_email = os.getenv("SUPERADMIN_EMAIL")
    superadmin_password = os.getenv("SUPERADMIN_PASSWORD")
    if superadmin_email and superadmin_password:
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            # Check if superadmin already exists
            existing_superadmin = db.query(User).filter(User.role == Role.SUPERADMIN.value).first()
            if not existing_superadmin:
                superadmin = User(
                    name="Super Admin",
                    email=superadmin_email,
                    password=hash_password(superadmin_password),
                    role=Role.SUPERADMIN
                )
                db.add(superadmin)
                db.commit()
                print("Superadmin bootstrapped successfully.")
        except Exception as e:
            print(f"Error bootstrapping superadmin: {e}")
        finally:
            db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(routes_admin.router, prefix="/api/admin", tags=["admin"])
