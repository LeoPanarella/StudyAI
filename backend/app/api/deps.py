from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User


import logging
logger = logging.getLogger(__name__)

def _extract_token(request: Request) -> str | None:
    # 1. Cookie httpOnly
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        return token
    # 2. Authorization: Bearer <token>
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        t = auth[7:].strip()
        if t:
            return t
    # 3. Header alternativo X-Session-Token (ignora filtros de Authorization em proxies/iframes)
    custom = request.headers.get("X-Session-Token", "").strip()
    if custom:
        return custom
    # 4. Query param ?auth_token=... (à prova de falhas em iframe)
    query_token = request.query_params.get("auth_token", "").strip()
    if query_token:
        return query_token

    logger.info(f"AUTH CHECK FAILED: path={request.url.path} headers={list(request.headers.keys())}")
    return None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = _extract_token(request)
    user_id = decode_access_token(token) if token else None
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado.")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida.")
    return user
