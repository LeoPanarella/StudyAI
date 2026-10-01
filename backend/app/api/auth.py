from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import login_limiter
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _is_https(request: Request) -> bool:
    return request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip() == "https"


def _set_session_cookie(request: Request, response: Response, token: str) -> None:
    """Cookie httpOnly como canal secundário de sessão.

    Atrás de HTTPS usamos SameSite=None + Secure + Partitioned para funcionar também quando a
    aplicação é embutida em um iframe de outro site; em HTTP local ficamos com SameSite=Lax.
    """
    https = _is_https(request) or settings.COOKIE_SECURE
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=https,
        samesite="none" if https else "lax",
        path="/",
    )
    if https:  # CHIPS: cookie particionado por site de topo (Starlette ainda não expõe o atributo)
        response.headers["set-cookie"] = response.headers["set-cookie"] + "; Partitioned"


def _auth_response(request: Request, response: Response, user: User) -> AuthResponse:
    token = create_access_token(user.id)
    _set_session_cookie(request, response, token)
    return AuthResponse(user=UserOut.model_validate(user), access_token=token)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    exists = db.scalar(select(User.id).where(User.email == email))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este e-mail já está cadastrado.")

    user = User(name=payload.name, email=email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # corrida entre dois cadastros simultâneos
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este e-mail já está cadastrado.")
    db.refresh(user)
    return _auth_response(request, response, user)


@router.post("/login", response_model=AuthResponse, dependencies=[Depends(login_limiter)])
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    # Mensagem genérica: não revelar se o e-mail existe.
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos.")
    return _auth_response(request, response, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(key=settings.COOKIE_NAME, path="/")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
