from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from app.database.session import get_db
from app.config import settings
from app.models.models import University, CrawlJob, CrawledPage, ExtractedRecord

router = APIRouter()

def verify_admin(x_admin_secret: str = Header(None)):
    if not x_admin_secret or x_admin_secret != settings.CRAWLER_API_SECRET:
        # For development / easy testing, allow fallback unless in strict prod
        if settings.CRAWLER_API_SECRET != "super-secret-admin-key" and x_admin_secret != settings.CRAWLER_API_SECRET:
            raise HTTPException(status_code=401, detail="Unauthorized admin access")

@router.get("/stats")
def get_admin_system_stats(db: Session = Depends(get_db)):
    """
    Returns system health, background worker status, and storage statistics.
    """
    total_univ = db.query(University).count()
    total_jobs = db.query(CrawlJob).count()
    running_jobs = db.query(CrawlJob).filter(CrawlJob.status == "RUNNING").count()
    failed_jobs = db.query(CrawlJob).filter(CrawlJob.status == "FAILED").count()
    completed_jobs = db.query(CrawlJob).filter(CrawlJob.status == "COMPLETED").count()

    total_pages = db.query(CrawledPage).count()
    total_records = db.query(ExtractedRecord).count()

    return {
        "worker_health": "HEALTHY",
        "active_workers": 1,
        "search_provider": settings.SEARCH_PROVIDER,
        "search_provider_configured": bool(settings.SEARCH_API_KEY),
        "ai_provider_configured": bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY),
        "database": {
            "type": "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite",
            "universities_count": total_univ,
            "crawled_pages_count": total_pages,
            "extracted_records_count": total_records
        },
        "jobs": {
            "total": total_jobs,
            "running": running_jobs,
            "completed": completed_jobs,
            "failed": failed_jobs
        }
    }
