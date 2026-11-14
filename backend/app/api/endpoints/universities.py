import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, func
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
    FacilitySchema, ContactSchema, TraceableFact, SearchRequest, SearchResponse,
    CollegeSuggestion, URLResolveResponse, AISearchRequest, AISearchResponse, RecommendedInstitution
)
from crawler.discovery import DiscoveryEngine
from extraction.ai_extractor import AIExtractor
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

    has_joins = bool(admission_status or degree_type or has_scholarship)

    if admission_status:
        q = q.join(Admission).filter(Admission.admission_status == admission_status.upper())

    if degree_type:
        q = q.join(Program).filter(Program.degree_type.ilike(f"%{degree_type}%"))

    if has_scholarship:
        q = q.join(Scholarship)

    if has_joins:
        subq = q.with_entities(University.id).distinct().subquery()
        total = db.query(func.count()).select_from(subq).scalar() or 0
        universities = db.query(University).filter(University.id.in_(q.with_entities(University.id)))\
                        .order_by(desc(University.data_completeness_score), University.name)\
                        .offset((page - 1) * page_size)\
                        .limit(page_size)\
                        .all()
    else:
        total = q.count()
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

POPULAR_INSTITUTIONS_CATALOG = [
    {"name": "Indian Institute of Technology Bombay", "short_name": "IIT Bombay", "city": "Mumbai", "state": "Maharashtra", "website": "https://www.iitb.ac.in", "type": "Institute of National Importance"},
    {"name": "Birla Institute of Technology and Science, Pilani", "short_name": "BITS Pilani", "city": "Pilani", "state": "Rajasthan", "website": "https://www.bits-pilani.ac.in", "type": "Deemed University"},
    {"name": "International Institute of Information Technology Hyderabad", "short_name": "IIIT Hyderabad", "city": "Hyderabad", "state": "Telangana", "website": "https://www.iiit.ac.in", "type": "Autonomous University"},
    {"name": "Indian Institute of Technology Delhi", "short_name": "IIT Delhi", "city": "New Delhi", "state": "Delhi", "website": "https://home.iitd.ac.in", "type": "Institute of National Importance"},
    {"name": "Indian Institute of Technology Madras", "short_name": "IIT Madras", "city": "Chennai", "state": "Tamil Nadu", "website": "https://www.iitm.ac.in", "type": "Institute of National Importance"},
    {"name": "Indian Institute of Technology Kharagpur", "short_name": "IIT Kharagpur", "city": "Kharagpur", "state": "West Bengal", "website": "https://www.iitkgp.ac.in", "type": "Institute of National Importance"},
    {"name": "Indian Institute of Science Bangalore", "short_name": "IISc Bangalore", "city": "Bengaluru", "state": "Karnataka", "website": "https://iisc.ac.in", "type": "Deemed University"},
    {"name": "National Institute of Technology Warangal", "short_name": "NIT Warangal", "city": "Warangal", "state": "Telangana", "website": "https://www.nitw.ac.in", "type": "National Institute of Technology"},
    {"name": "National Institute of Technology Tiruchirappalli", "short_name": "NIT Trichy", "city": "Tiruchirappalli", "state": "Tamil Nadu", "website": "https://www.nitt.edu", "type": "National Institute of Technology"},
    {"name": "Vellore Institute of Technology", "short_name": "VIT Vellore", "city": "Vellore", "state": "Tamil Nadu", "website": "https://vit.ac.in", "type": "Deemed University"},
    {"name": "University of Delhi", "short_name": "Delhi University", "city": "New Delhi", "state": "Delhi", "website": "https://www.du.ac.in", "type": "Central University"},
    {"name": "Anna University", "short_name": "Anna University", "city": "Chennai", "state": "Tamil Nadu", "website": "https://www.annauniv.edu", "type": "State University"},
    {"name": "Stanford University", "short_name": "Stanford", "city": "Stanford", "state": "California", "website": "https://www.stanford.edu", "type": "Private University"},
    {"name": "Massachusetts Institute of Technology", "short_name": "MIT", "city": "Cambridge", "state": "Massachusetts", "website": "https://www.mit.edu", "type": "Private University"}
]

@router.get("/suggest", response_model=List[CollegeSuggestion])
def suggest_colleges(
    query: str = Query(..., min_length=1, description="College name or prefix to suggest"),
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Real-time autocomplete and fuzzy suggestion endpoint for college searches.
    Returns matching institutions from database and educational directory.
    """
    clean_q = query.strip()
    search_pattern = f"%{clean_q}%"
    suggestions: List[CollegeSuggestion] = []
    seen_names = set()

    # 1. Search database
    db_matches = db.query(University).filter(
        University.is_active == True,
        or_(
            University.name.ilike(search_pattern),
            University.short_name.ilike(search_pattern),
            University.city.ilike(search_pattern),
            University.state.ilike(search_pattern)
        )
    ).limit(limit).all()

    for u in db_matches:
        seen_names.add(u.name.lower())
        suggestions.append(
            CollegeSuggestion(
                id=u.id,
                name=u.name,
                short_name=u.short_name,
                city=u.city,
                state=u.state,
                official_website=u.official_website,
                slug=u.slug,
                institution_type=u.institution_type,
                data_completeness_score=float(u.data_completeness_score or 0),
                is_in_database=True
            )
        )

    # 2. Complement with recognized institution catalog if needed
    if len(suggestions) < limit:
        q_lower = clean_q.lower()
        for cat in POPULAR_INSTITUTIONS_CATALOG:
            if len(suggestions) >= limit:
                break
            if cat["name"].lower() in seen_names:
                continue
            if (
                q_lower in cat["name"].lower() or 
                q_lower in cat["short_name"].lower() or 
                q_lower in cat["city"].lower()
            ):
                seen_names.add(cat["name"].lower())
                suggestions.append(
                    CollegeSuggestion(
                        id=None,
                        name=cat["name"],
                        short_name=cat["short_name"],
                        city=cat["city"],
                        state=cat["state"],
                        official_website=cat["website"],
                        slug=cat["short_name"].lower().replace(" ", "-"),
                        institution_type=cat["type"],
                        data_completeness_score=0.0,
                        is_in_database=False
                    )
                )

    return suggestions

@router.get("/resolve-url", response_model=URLResolveResponse)
def resolve_college_url(
    name: str = Query(..., min_length=2, description="College or university name"),
    api_key: Optional[str] = Query(None, description="Optional custom Gemini API key"),
    db: Session = Depends(get_db)
):
    """
    Auto-fetches the genuine, official institutional website URL and domain given a college name.
    Prioritizes verified database records, then Gemini AI intelligence, then discovery engine.
    """
    clean_name = name.strip()

    # 1. Check existing database
    existing = db.query(University).filter(
        or_(
            University.name.ilike(f"%{clean_name}%"),
            University.short_name.ilike(f"%{clean_name}%")
        )
    ).first()

    if existing:
        return URLResolveResponse(
            name=existing.name,
            official_website=existing.official_website,
            domain=existing.domain,
            confidence=1.0,
            source="Verified Database",
            is_accessible=True,
            note="Official website retrieved from verified institutional dataset."
        )

    # 2. Check catalog
    for cat in POPULAR_INSTITUTIONS_CATALOG:
        if (
            clean_name.lower() in cat["name"].lower() or 
            clean_name.lower() in cat["short_name"].lower()
        ):
            domain = cat["website"].replace("https://", "").replace("http://", "").split("/")[0].replace("www.", "")
            return URLResolveResponse(
                name=cat["name"],
                official_website=cat["website"],
                domain=domain,
                confidence=0.98,
                source="Institutional Catalog",
                is_accessible=True,
                note="Official institutional domain resolved from recognized directory."
            )

    # 3. Use Gemini AI Resolver
    ai_extractor = AIExtractor(api_key=api_key)
    ai_result = ai_extractor.resolve_official_url(clean_name, api_key=api_key)
    if ai_result.get("official_website"):
        return URLResolveResponse(
            name=ai_result.get("name", clean_name),
            official_website=ai_result["official_website"],
            domain=ai_result.get("domain", ""),
            confidence=ai_result.get("confidence", 0.90),
            source=ai_result.get("source", "Gemini AI"),
            is_accessible=ai_result.get("is_accessible", True),
            note=ai_result.get("note", "Resolved via Gemini AI")
        )

    # 4. Fallback: Discovery Engine
    discovery = DiscoveryEngine()
    disc_results = discovery.discover_institutions(clean_name, max_results=1)
    if disc_results:
        top_disc = disc_results[0]
        return URLResolveResponse(
            name=top_disc.get("name", clean_name),
            official_website=top_disc["official_website"],
            domain=top_disc.get("domain", ""),
            confidence=0.80,
            source="Discovery Engine",
            is_accessible=True,
            note="Discovered official domain via search crawler."
        )

    raise HTTPException(
        status_code=404,
        detail=f"Could not automatically resolve official website for '{clean_name}'. Please enter the URL manually or supply a Gemini API key."
    )

@router.post("/ai-search", response_model=AISearchResponse)
def ai_smart_search(
    payload: AISearchRequest,
    db: Session = Depends(get_db)
):
    """
    AI-powered natural language college discovery using Gemini.
    Understands conversational criteria (placements, open admissions, tuition budget, degree programs).
    """
    db_unis = db.query(University).filter(University.is_active == True).all()
    db_context = [
        {
            "id": u.id,
            "name": u.name,
            "city": u.city,
            "state": u.state,
            "institution_type": u.institution_type,
            "official_website": u.official_website,
            "data_completeness_score": float(u.data_completeness_score or 0)
        }
        for u in db_unis
    ]

    ai_extractor = AIExtractor(api_key=payload.api_key)
    result = ai_extractor.smart_search(
        query=payload.query,
        db_colleges=db_context,
        api_key=payload.api_key
    )

    # Link recommended institutions with any matching database IDs
    recommended = []
    for rec in result.get("recommended_institutions", []):
        r_name = rec.get("name", "").lower()
        matched_id = None
        for u in db_unis:
            if u.name.lower() in r_name or r_name in u.name.lower() or (u.short_name and u.short_name.lower() in r_name):
                matched_id = u.id
                break
        recommended.append(
            RecommendedInstitution(
                name=rec.get("name", ""),
                location=rec.get("location"),
                official_website=rec.get("official_website"),
                key_highlights=rec.get("key_highlights"),
                why_recommended=rec.get("why_recommended"),
                matched_id=matched_id
            )
        )

    # Convert matching DB universities to UniversitySummary
    matched_colleges: List[UniversitySummary] = []
    for u in db_unis:
        u_lower = u.name.lower()
        if any(w in u_lower for w in payload.query.lower().split() if len(w) > 3):
            matched_colleges.append(UniversitySummary.from_orm(u))

    return AISearchResponse(
        query=payload.query,
        ai_answer=result.get("ai_answer", "AI Search analysis complete."),
        recommended_institutions=recommended,
        matched_colleges=matched_colleges,
        confidence=result.get("confidence", 0.95),
        source=result.get("source", "Gemini AI")
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

    # Deduplicate admissions so UI renders clean, distinct admission announcements
    seen_adm_keys = set()
    unique_admissions = []
    for a in admissions:
        adm_key = (a.academic_year, a.admission_status, a.title, a.entrance_exams or "")
        if adm_key not in seen_adm_keys:
            seen_adm_keys.add(adm_key)
            unique_admissions.append(a)

    # Deduplicate programs
    seen_prog_keys = set()
    unique_programs = []
    for p in programs:
        prog_key = (re.sub(r"[^a-zA-Z0-9]", "", p.name.lower()), (p.degree_type or "").lower().strip())
        if prog_key not in seen_prog_keys:
            seen_prog_keys.add(prog_key)
            unique_programs.append(p)

    latest_adm = unique_admissions[0] if unique_admissions else None
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
        programs_count=len(unique_programs),
        faculty_count=len(faculty),
        created_at=u.created_at,
        admissions=[AdmissionSchema.from_orm(a) for a in unique_admissions],
        programs=[ProgramSchema.from_orm(p) for p in unique_programs],
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
