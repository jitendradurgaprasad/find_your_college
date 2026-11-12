from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List, Optional
from datetime import datetime

from app.database.session import get_db
from app.models.models import (
    University, Admission, Program, Scholarship, Faculty, Placement,
    Facility, Notification, UniversityContact, ExtractedRecord, ResearchProject
)
from app.schemas.schemas import (
    UniversitySummary, UniversityProfile, AdmissionSchema, ProgramSchema,
    ScholarshipSchema, FacultySchema, PlacementSchema, NotificationSchema,
    FacilitySchema, ContactSchema, TraceableFact, SearchRequest, SearchResponse
)
from crawler.discovery import DiscoveryEngine
from worker.job_manager import BackgroundJobManager

router = APIRouter()

@router.get("", response_model=SearchResponse)
def list_universities(
    query: Optional[str] = None,
    country: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    institution_type: Optional[str] = None,
    admission_status: Optional[str] = None,
    degree_type: Optional[str] = None,
    has_scholarship: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search and filter colleges by location, name, type, admission status, programs, and financial aid.
    """
    q = db.query(University).filter(University.is_active == True)

    if query:
        search_pattern = f"%{query}%"
        q = q.filter(
            or_(
                University.name.ilike(search_pattern),
                University.short_name.ilike(search_pattern),
                University.city.ilike(search_pattern),
                University.state.ilike(search_pattern),
                University.description.ilike(search_pattern)
            )
        )

    if country:
        q = q.filter(University.country.ilike(country))
    if state:
        q = q.filter(University.state.ilike(f"%{state}%"))
    if city:
        q = q.filter(University.city.ilike(f"%{city}%"))
    if institution_type:
        q = q.filter(University.institution_type.ilike(f"%{institution_type}%"))

    if admission_status:
        q = q.join(Admission).filter(Admission.admission_status == admission_status.upper())

    if degree_type:
        q = q.join(Program).filter(Program.degree_type.ilike(f"%{degree_type}%"))

    if has_scholarship:
        q = q.join(Scholarship)

    total = q.distinct().count()
    universities = q.order_by(desc(University.data_completeness_score), University.name)\
                    .offset((page - 1) * page_size)\
                    .limit(page_size)\
                    .all()

    results = []
    for u in universities:
        # Determine latest verified admission status
        latest_adm = db.query(Admission).filter(Admission.university_id == u.id).order_by(desc(Admission.academic_year)).first()
        adm_status = latest_adm.admission_status if latest_adm else "UNKNOWN"
        sch_count = db.query(Scholarship).filter(Scholarship.university_id == u.id).count()
        prog_count = db.query(Program).filter(Program.university_id == u.id).count()
        fac_count = db.query(Faculty).filter(Faculty.university_id == u.id).count()

        results.append(UniversitySummary(
            id=u.id,
            name=u.name,
            short_name=u.short_name,
            slug=u.slug,
            official_website=u.official_website,
            institution_type=u.institution_type or "University",
            ownership_type=u.ownership_type or "Public",
            country=u.country or "India",
            state=u.state,
            city=u.city,
            address=u.address,
            accreditation=u.accreditation,
            recognition=u.recognition,
            description=u.description,
            established_year=u.established_year,
            logo_url=u.logo_url,
            data_completeness_score=float(u.data_completeness_score or 0.0),
            last_scanned_at=u.last_scanned_at,
            admission_status=adm_status,
            has_scholarships=sch_count > 0,
            programs_count=prog_count,
            faculty_count=fac_count,
            created_at=u.created_at
        ))

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return SearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=results
    )

@router.post("/search", response_model=SearchResponse)
def search_universities(payload: SearchRequest, db: Session = Depends(get_db)):
    """
    POST search handler supporting JSON request bodies with rich filters.
    """
    return list_universities(
        query=payload.query,
        country=payload.country,
        state=payload.state,
        city=payload.city,
        institution_type=payload.institution_type,
        admission_status=payload.admission_status,
        degree_type=payload.degree_type,
        has_scholarship=payload.has_scholarship,
        page=payload.page,
        page_size=payload.page_size,
        db=db
    )

@router.get("/{univ_id}", response_model=UniversityProfile)
def get_university_profile(univ_id: str, db: Session = Depends(get_db)):
    """
    Returns complete 11-category profile for an institution with source traceability.
    """
    u = db.query(University).filter(or_(University.id == univ_id, University.slug == univ_id)).first()
    if not u:
        raise HTTPException(status_code=404, detail="University not found")

    admissions = db.query(Admission).filter(Admission.university_id == u.id).all()
    programs = db.query(Program).filter(Program.university_id == u.id).all()
    scholarships = db.query(Scholarship).filter(Scholarship.university_id == u.id).all()
    faculty = db.query(Faculty).filter(Faculty.university_id == u.id).all()
    placements = db.query(Placement).filter(Placement.university_id == u.id).all()
    facilities = db.query(Facility).filter(Facility.university_id == u.id).all()
    research = db.query(ResearchProject).filter(ResearchProject.university_id == u.id).all()
    notifications = db.query(Notification).filter(Notification.university_id == u.id).all()
    contacts = db.query(UniversityContact).filter(UniversityContact.university_id == u.id).all()
    records = db.query(ExtractedRecord).filter(ExtractedRecord.university_id == u.id).all()

    traceable_facts = [
        TraceableFact(
            category=r.category,
            field_name=r.field_name,
            value=r.extracted_value,
            source_url=r.source_url,
            source_page_title=r.source_page_title,
            confidence_score=float(r.confidence_score or 0.85),
            verification_status=r.verification_status,
            academic_year=r.academic_year,
            last_verified_at=r.last_verified_at
        ) for r in records
    ]

    latest_adm = admissions[0] if admissions else None
    adm_status = latest_adm.admission_status if latest_adm else "UNKNOWN"

    return UniversityProfile(
        id=u.id,
        name=u.name,
        short_name=u.short_name,
        slug=u.slug,
        official_website=u.official_website,
        institution_type=u.institution_type or "University",
        ownership_type=u.ownership_type or "Public",
        country=u.country or "India",
        state=u.state,
        city=u.city,
        address=u.address,
        accreditation=u.accreditation,
        recognition=u.recognition,
        description=u.description,
        established_year=u.established_year,
        logo_url=u.logo_url,
        data_completeness_score=float(u.data_completeness_score or 0.0),
        last_scanned_at=u.last_scanned_at,
        admission_status=adm_status,
        has_scholarships=len(scholarships) > 0,
        programs_count=len(programs),
        faculty_count=len(faculty),
        created_at=u.created_at,
        admissions=[AdmissionSchema.from_orm(a) for a in admissions],
        programs=[ProgramSchema.from_orm(p) for p in programs],
        scholarships=[ScholarshipSchema.from_orm(s) for s in scholarships],
        faculty=[FacultySchema.from_orm(f) for f in faculty],
        placements=[PlacementSchema.from_orm(pl) for pl in placements],
        facilities=[FacilitySchema.from_orm(fa) for fa in facilities],
        research_projects=[ResearchProjectSchema.from_orm(rp) for rp in research],
        notifications=[NotificationSchema.from_orm(n) for n in notifications],
        contacts=[ContactSchema.from_orm(c) for c in contacts],
        traceable_facts=traceable_facts
    )

@router.get("/{univ_id}/admissions", response_model=List[AdmissionSchema])
def get_university_admissions(univ_id: str, db: Session = Depends(get_db)):
    return db.query(Admission).filter(Admission.university_id == univ_id).all()

@router.get("/{univ_id}/programs", response_model=List[ProgramSchema])
def get_university_programs(univ_id: str, db: Session = Depends(get_db)):
    return db.query(Program).filter(Program.university_id == univ_id).all()

@router.get("/{univ_id}/scholarships", response_model=List[ScholarshipSchema])
def get_university_scholarships(univ_id: str, db: Session = Depends(get_db)):
    return db.query(Scholarship).filter(Scholarship.university_id == univ_id).all()

@router.get("/{univ_id}/faculty", response_model=List[FacultySchema])
def get_university_faculty(univ_id: str, db: Session = Depends(get_db)):
    return db.query(Faculty).filter(Faculty.university_id == univ_id).all()

@router.get("/{univ_id}/placements", response_model=List[PlacementSchema])
def get_university_placements(univ_id: str, db: Session = Depends(get_db)):
    return db.query(Placement).filter(Placement.university_id == univ_id).all()

@router.get("/{univ_id}/notifications", response_model=List[NotificationSchema])
def get_university_notifications(univ_id: str, db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.university_id == univ_id).all()

@router.post("/{univ_id}/rescan")
def rescan_university(univ_id: str, db: Session = Depends(get_db)):
    """
    Triggers an immediate re-crawl and verification pass for an existing institution.
    """
    u = db.query(University).filter(or_(University.id == univ_id, University.slug == univ_id)).first()
    if not u:
        raise HTTPException(status_code=404, detail="University not found")

    job_mgr = BackgroundJobManager()
    job_id = job_mgr.start_crawl_job(
        seed_url=u.official_website,
        max_depth=2,
        max_pages=30,
        university_name=u.name
    )

    return {
        "status": "QUEUED",
        "job_id": job_id,
        "university_id": u.id,
        "message": f"Rescan initiated for {u.name}"
    }
