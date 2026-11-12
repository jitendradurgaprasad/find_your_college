from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database.session import get_db
from app.models.models import SavedUniversity, University, User
from app.schemas.schemas import UniversitySummary

router = APIRouter()

class SaveCollegeRequest(BaseModel):
    university_id: str
    user_id: Optional[str] = "demo-user-123"
    notes: Optional[str] = None

class SavedCollegeItem(BaseModel):
    id: str
    university: UniversitySummary
    notes: Optional[str] = None
    created_at: datetime

@router.get("", response_model=List[SavedCollegeItem])
def get_saved_colleges(user_id: str = "demo-user-123", db: Session = Depends(get_db)):
    """
    Returns colleges bookmarked/saved by user.
    """
    saved = db.query(SavedUniversity).filter(SavedUniversity.user_id == user_id).order_by(desc(SavedUniversity.created_at)).all()
    results = []
    for s in saved:
        u = db.query(University).filter(University.id == s.university_id).first()
        if not u:
            continue
        results.append(SavedCollegeItem(
            id=s.id,
            university=UniversitySummary(
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
                created_at=u.created_at
            ),
            notes=s.notes,
            created_at=s.created_at
        ))
    return results

@router.post("")
def save_college(payload: SaveCollegeRequest, db: Session = Depends(get_db)):
    u = db.query(University).filter(University.id == payload.university_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="University not found")

    existing = db.query(SavedUniversity).filter(
        SavedUniversity.university_id == payload.university_id,
        SavedUniversity.user_id == payload.user_id
    ).first()

    if existing:
        return {"status": "ALREADY_SAVED", "id": existing.id}

    # Ensure user exists
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        user = User(id=payload.user_id, email="demo@find-your-college.edu", name="Student User")
        db.add(user)
        db.commit()

    import uuid
    new_saved = SavedUniversity(
        id=str(uuid.uuid4()),
        user_id=payload.user_id,
        university_id=payload.university_id,
        notes=payload.notes,
        created_at=datetime.utcnow()
    )
    db.add(new_saved)
    db.commit()

    return {"status": "SAVED", "id": new_saved.id}

@router.delete("/{saved_id}")
def remove_saved_college(saved_id: str, db: Session = Depends(get_db)):
    rec = db.query(SavedUniversity).filter(SavedUniversity.id == saved_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Saved college entry not found")
    db.delete(rec)
    db.commit()
    return {"status": "REMOVED"}
