from fastapi import APIRouter

from app.api import auth, connections, flashcards, materials

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(materials.router)
api_router.include_router(flashcards.router)
api_router.include_router(connections.router)
