from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    # bcrypt considera no máximo 72 bytes; limitamos em 72 caracteres para não truncar silenciosamente.
    password: str = Field(min_length=8, max_length=72)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Informe seu nome.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime


class AuthResponse(BaseModel):
    """Resposta de login/cadastro. O token também é gravado em cookie httpOnly, mas o SPA
    usa o header Authorization (funciona mesmo dentro de iframes / com cookies de terceiros bloqueados)."""

    user: UserOut
    access_token: str
    token_type: str = "bearer"
