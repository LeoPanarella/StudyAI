from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas de variáveis de ambiente (ou do arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "StudyAI"
    ENV: str = "development"  # development | production

    # Banco de dados — a aplicação depende apenas desta URL.
    # Formato: postgresql+psycopg://usuario:senha@host:5432/nome_do_banco
    DATABASE_URL: str

    # Autenticação
    SECRET_KEY: str  # use algo longo e aleatório em produção (ex.: openssl rand -hex 32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias
    COOKIE_NAME: str = "studyai_session"
    COOKIE_SECURE: bool = False  # True em produção (HTTPS)

    # CORS — só é necessário se o frontend for servido de outra origem.
    # Em dev, o Vite faz proxy de /api, então fica vazio.
    CORS_ORIGINS: str = ""

    # Upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_MB: int = 25

    # IA (Google Gemini + Motor Local de Contingência)
    AI_PROVIDER: str = "gemini"  # "gemini" ou "local"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"  # modelo principal rápido e estável no tier gratuito
    GEMINI_FALLBACK_MODELS: str = (  # modelos tentados em ordem se o principal atingir limite
        "gemini-3.5-flash,gemini-flash-lite-latest,gemini-3.8-flash"
    )
    GEMINI_TIMEOUT_SECONDS: int = 30
    GEMINI_RETRY_ROUNDS: int = 8  # rodadas (cada uma percorre todos os modelos); roda em segundo plano, então pode insistir

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024

    @property
    def gemini_fallback_models_list(self) -> list[str]:
        return [m.strip() for m in self.GEMINI_FALLBACK_MODELS.split(",") if m.strip()]


settings = Settings()
