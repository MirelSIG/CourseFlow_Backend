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
