"""
Define funciones auxiliares para el manejo y estandarización de respuestas de error.
Facilita el lanzamiento de excepciones HTTP consistentes en toda la aplicación.
"""

from fastapi import HTTPException, status

def error_response(code: int, message: str):
    """
    Devuelve una respuesta de error estandarizada levantando HTTPException.
    """
    raise HTTPException(status_code=code, detail=message)

def forbidden_error():
    """
    Devuelve un error 403 genérico sanitizado para no revelar información de la ruta.
    """
    error_response(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
