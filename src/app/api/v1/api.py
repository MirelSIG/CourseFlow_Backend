"""
Agrupa todos los módulos de rutas de API para la versión 1 de la API de CourseFlow.
Incluye sub-enrutadores para autenticación, usuarios, cursos, solicitudes y listas de espera.
"""

from fastapi import APIRouter

from app.api.v1 import routes_auth, routes_users, routes_courses, routes_applications, routes_waiting_list

api_router = APIRouter()
api_router.include_router(routes_auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(routes_users.router, prefix="/users", tags=["users"])
api_router.include_router(routes_courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(routes_applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(routes_waiting_list.router, prefix="/waiting-list", tags=["waiting-list"])