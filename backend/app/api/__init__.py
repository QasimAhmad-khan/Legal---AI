from fastapi import APIRouter

api_router = APIRouter()

from app.api.endpoints import auth, documents, precedents, analysis
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(precedents.router, prefix="/precedents", tags=["precedents"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
