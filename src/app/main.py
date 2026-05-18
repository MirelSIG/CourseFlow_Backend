from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import routes_auth, routes_users, routes_courses, routes_applications, routes_waiting_list

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(routes_users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(routes_courses.router, prefix="/api/v1/courses", tags=["courses"])
app.include_router(routes_applications.router, prefix="/api/v1/applications", tags=["applications"])
app.include_router(routes_waiting_list.router, prefix="/api/v1/waiting-list", tags=["waiting_list"])