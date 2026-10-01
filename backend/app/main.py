import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.core.config import settings
from app.db.session import get_db
from app.services.jobs import fail_stale_jobs


logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    fail_stale_jobs()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.api_route("/api/health", methods=["GET", "HEAD"], tags=["health"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok", "env": settings.ENV}


# Monta os arquivos do frontend estático (dist) para servir a SPA em qualquer porta
from pathlib import Path
from fastapi import HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if (dist_dir / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

if (dist_dir / "index.html").is_file():
    @app.api_route("/{full_path:path}", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    def serve_spa(request: Request, full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail=f"Endpoint da API '/{full_path}' não encontrado.")
        if request.method not in ("GET", "HEAD"):
            raise HTTPException(status_code=405, detail="Método não permitido para rota estática.")
        target = dist_dir / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(dist_dir / "index.html")
