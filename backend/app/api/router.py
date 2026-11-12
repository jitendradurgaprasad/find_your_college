from fastapi import APIRouter
from app.api.endpoints import universities, crawl, quality, compare, monitoring, saved, admin

api_router = APIRouter()

api_router.include_router(universities.router, prefix="/universities", tags=["Universities"])
api_router.include_router(crawl.router, prefix="/crawl", tags=["Crawler Engine"])
api_router.include_router(quality.router, prefix="/data-quality", tags=["Data Quality"])
api_router.include_router(compare.router, prefix="/universities", tags=["Comparison"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(saved.router, prefix="/saved", tags=["Saved Colleges"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])
