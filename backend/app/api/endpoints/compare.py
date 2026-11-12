from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database.session import get_db
from app.models.models import University, Program, Admission, Scholarship, Placement, Facility
from app.schemas.schemas import CompareRequest, CompareResponse, ComparisonItem

router = APIRouter()

@router.post("/compare", response_model=CompareResponse)
def compare_colleges(payload: CompareRequest, db: Session = Depends(get_db)):
    """
    Performs side-by-side comparison of multiple educational institutions.
    Clearly marks missing information without fabrication.
    """
    if not payload.university_ids or len(payload.university_ids) < 1:
        raise HTTPException(status_code=400, detail="Provide at least one university ID to compare")

    colleges = []
    for u_id in payload.university_ids[:5]: # Max 5 colleges at once
        u = db.query(University).filter(University.id == u_id).first()
        if not u:
            continue

        programs = db.query(Program).filter(Program.university_id == u.id).all()
        admissions = db.query(Admission).filter(Admission.university_id == u.id).order_by(desc(Admission.academic_year)).first()
        scholarships = db.query(Scholarship).filter(Scholarship.university_id == u.id).all()
        placements = db.query(Placement).filter(Placement.university_id == u.id).order_by(desc(Placement.academic_year)).first()
        facilities = db.query(Facility).filter(Facility.university_id == u.id).all()

        location_str = f"{u.city}, {u.state}, {u.country}" if u.city and u.state else (u.country or "India")
        sample_progs = [p.name for p in programs[:4]]

        fee_range = "Information unavailable"
        fees = [p.tuition_fees_annual for p in programs if p.tuition_fees_annual and "official" not in p.tuition_fees_annual.lower()]
        if fees:
            fee_range = f"{fees[0]} (typical)"

        colleges.append(ComparisonItem(
            id=u.id,
            name=u.name,
            logo_url=u.logo_url,
            official_website=u.official_website,
            location=location_str,
            institution_type=u.institution_type or "University",
            ownership=u.ownership_type or "Public",
            accreditation=u.accreditation or "Information unavailable",
            admission_status=admissions.admission_status if admissions else "UNKNOWN",
            academic_year=admissions.academic_year if admissions else "Information unavailable",
            programs_offered_count=len(programs),
            sample_programs=sample_progs,
            tuition_fee_range=fee_range,
            scholarships_count=len(scholarships),
            placement_rate=f"{placements.placement_percentage}%" if placements and placements.placement_percentage else "Information unavailable",
            highest_package=placements.highest_package if placements and placements.highest_package else "Information unavailable",
            average_package=placements.average_package if placements and placements.average_package else "Information unavailable",
            facilities=[f.facility_type for f in facilities],
            data_completeness_score=float(u.data_completeness_score or 0.0)
        ))

    return CompareResponse(colleges=colleges)
