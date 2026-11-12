from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime, timedelta

from app.database.session import get_db
from app.models.models import ExtractedRecord, University
from app.schemas.schemas import MonitoringChange

router = APIRouter()

@router.get("/changes", response_model=List[MonitoringChange])
def get_monitoring_changes(limit: int = 25, db: Session = Depends(get_db)):
    """
    Returns recent changes and updates identified across revisited institutional sites.
    """
    records = db.query(ExtractedRecord)\
                .filter(ExtractedRecord.previous_value.isnot(None))\
                .order_by(desc(ExtractedRecord.last_verified_at))\
                .limit(limit).all()

    changes = []
    for r in records:
        univ = db.query(University).filter(University.id == r.university_id).first()
        changes.append(MonitoringChange(
            university_name=univ.name if univ else "Educational Institution",
            category=r.category,
            field_name=r.field_name,
            change_type="MODIFIED" if r.previous_value else "NEW",
            previous_value=r.previous_value,
            current_value=r.extracted_value,
            detected_at=r.last_verified_at or datetime.utcnow(),
            source_url=r.source_url
        ))

    # If no diff records exist yet, generate audit feed from latest extracted records
    if not changes:
        recent = db.query(ExtractedRecord).order_by(desc(ExtractedRecord.extracted_at)).limit(limit).all()
        for r in recent:
            univ = db.query(University).filter(University.id == r.university_id).first()
            changes.append(MonitoringChange(
                university_name=univ.name if univ else "Educational Institution",
                category=r.category,
                field_name=r.field_name,
                change_type="NEW",
                previous_value=None,
                current_value=r.extracted_value,
                detected_at=r.extracted_at or datetime.utcnow(),
                source_url=r.source_url
            ))

    return changes
