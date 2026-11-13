from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database.session import get_db
from app.models.models import (
    CrawlJob, CrawlLog, University, Admission, Program, Scholarship, Faculty, Placement, ExtractedRecord
)
from app.schemas.schemas import CrawlStartRequest, CrawlJobStatus, CrawlLogSchema
from crawler.url_extractor import URLExtractor
from worker.job_manager import BackgroundJobManager

router = APIRouter()

@router.post("/start")
def start_crawl(payload: CrawlStartRequest):
    """
    Initiates an asynchronous crawl job for an institutional website.
    Validates SSRF protection and starts background extraction worker.
    """
    norm_url = URLExtractor.normalize_url(payload.url)
    if not norm_url:
        raise HTTPException(status_code=400, detail="Invalid URL format provided")

    if not URLExtractor.is_ssrf_safe(norm_url):
        raise HTTPException(status_code=400, detail="SSRF Security: Private network or localhost addresses are prohibited")

    manager = BackgroundJobManager()
    job_id = manager.start_crawl_job(
        seed_url=norm_url,
        max_depth=payload.max_depth or 2,
        max_pages=payload.max_pages or 25,
        university_name=payload.university_name
    )

    return {
        "job_id": job_id,
        "seed_url": norm_url,
        "status": "QUEUED",
        "message": "Crawl job accepted and queued in background worker"
    }

@router.get("/status/{job_id}", response_model=CrawlJobStatus)
def get_crawl_status(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieves real-time status, page progress, and logs for a crawl job.
    """
    job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Crawl job not found")

    logs = db.query(CrawlLog).filter(CrawlLog.job_id == job_id).order_by(CrawlLog.timestamp).all()

    univ_name = None
    univ_slug = None
    extracted_summary = None

    # Resolve University
    univ = None
    if job.university_id:
        univ = db.query(University).filter(University.id == job.university_id).first()
    if not univ and job.seed_url:
        domain = URLExtractor.get_domain(job.seed_url)
        if domain:
            univ = db.query(University).filter(University.domain == domain).first()

    if univ:
        univ_name = univ.name
        univ_slug = univ.slug
        extracted_summary = {
            "university_id": univ.id,
            "university_name": univ.name,
            "city": univ.city,
            "state": univ.state,
            "official_website": univ.official_website,
            "data_completeness_score": float(univ.data_completeness_score or 0),
            "admissions_count": db.query(Admission).filter(Admission.university_id == univ.id).count(),
            "programs_count": db.query(Program).filter(Program.university_id == univ.id).count(),
            "scholarships_count": db.query(Scholarship).filter(Scholarship.university_id == univ.id).count(),
            "faculty_count": db.query(Faculty).filter(Faculty.university_id == univ.id).count(),
            "placements_count": db.query(Placement).filter(Placement.university_id == univ.id).count(),
            "recent_records": [
                {
                    "category": r.category,
                    "field_name": r.field_name,
                    "extracted_value": r.extracted_value,
                    "source_url": r.source_url,
                    "confidence_score": float(r.confidence_score or 0.85),
                    "verification_status": r.verification_status
                }
                for r in db.query(ExtractedRecord).filter(
                    ExtractedRecord.university_id == univ.id
                ).order_by(desc(ExtractedRecord.extracted_at)).limit(12).all()
            ]
        }

    return CrawlJobStatus(
        job_id=job.id,
        seed_url=job.seed_url,
        status=job.status,
        pages_discovered=job.pages_discovered or 0,
        pages_crawled=job.pages_crawled or 0,
        records_extracted=job.records_extracted or 0,
        needs_review_count=job.needs_review_count or 0,
        errors_count=job.errors_count or 0,
        max_depth=job.max_depth or 2,
        max_pages=job.max_pages or 30,
        start_time=job.start_time,
        end_time=job.end_time,
        duration_seconds=float(job.duration_seconds) if job.duration_seconds else None,
        university_id=univ.id if univ else job.university_id,
        university_name=univ_name,
        university_slug=univ_slug,
        extracted_summary=extracted_summary,
        error_details=job.error_details,
        logs=[CrawlLogSchema.from_orm(l) for l in logs]
    )

@router.get("/jobs", response_model=List[CrawlJobStatus])
def list_crawl_jobs(limit: int = 20, db: Session = Depends(get_db)):
    jobs = db.query(CrawlJob).order_by(desc(CrawlJob.created_at)).limit(limit).all()
    results = []
    for j in jobs:
        results.append(CrawlJobStatus(
            job_id=j.id,
            seed_url=j.seed_url,
            status=j.status,
            pages_discovered=j.pages_discovered or 0,
            pages_crawled=j.pages_crawled or 0,
            records_extracted=j.records_extracted or 0,
            needs_review_count=j.needs_review_count or 0,
            errors_count=j.errors_count or 0,
            max_depth=j.max_depth or 2,
            max_pages=j.max_pages or 30,
            start_time=j.start_time,
            end_time=j.end_time,
            duration_seconds=float(j.duration_seconds) if j.duration_seconds else None,
            university_id=j.university_id,
            error_details=j.error_details,
            logs=[]
        ))
    return results
