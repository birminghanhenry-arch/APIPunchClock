"""
app/core/security.py
Creación y verificación de JWT + dependencia get_current_user.

Sin lógica de negocio: solo codifica/decodifica tokens y carga
el empleado desde el repo para validar que sigue activo.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config   import settings
from app.core.database import get_db

_ALGORITHM = "HS256"
_bearer    = HTTPBearer()


def create_access_token(employee_id: int, is_admin: bool) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub":      str(employee_id),
        "is_admin": is_admin,
        "exp":      expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    """
    Dependencia FastAPI — extrae y valida el JWT del header
    Authorization: Bearer <token> y retorna el Employee activo.

        def endpoint(current_user = Depends(get_current_user)): ...
    """
    _401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload     = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[_ALGORITHM])
        employee_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise _401

    # Import diferido para evitar circular imports
    from app.repositories import employee_repo
    emp = employee_repo.get_by_id(db, employee_id)
    if not emp or not emp.active:
        raise _401
    return emp
