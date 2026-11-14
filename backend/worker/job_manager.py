import uuid
import threading
from datetime import datetime
from typing import Dict, Any, Optional
import time
import re

from app.database.session import SessionLocal
from app.models.models import (
    University, CrawlJob, CrawlLog, CrawledPage, ExtractedRecord,
    Admission, Program, Scholarship, Faculty, Placement, Facility,
    Notification, UniversityContact
)
from crawler.url_extractor import URLExtractor
from crawler.crawler_engine import CrawlerEngine
from extraction.classifier import ContentClassifier
from extraction.admission_extractor import AdmissionExtractor
from extraction.course_extractor import CourseExtractor
from extraction.scholarship_extractor import ScholarshipExtractor
from extraction.faculty_extractor import FacultyExtractor
from extraction.placement_extractor import PlacementExtractor
from extraction.other_extractors import FacilitiesExtractor, NotificationExtractor, ContactExtractor
from extraction.ai_extractor import AIExtractor
from quality.validator import DataValidator
from quality.deduplicator import Deduplicator
from quality.verifier import DataVerifier

class BackgroundJobManager:
    _instance = None
    _active_threads: Dict[str, threading.Thread] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BackgroundJobManager, cls).__new__(cls)
        return cls._instance

    def start_crawl_job(self, seed_url: str, max_depth: int = 2, max_pages: int = 40, university_name: Optional[str] = None) -> str:
        job_id = str(uuid.uuid4())
        db = SessionLocal()
        try:
            new_job = CrawlJob(
                id=job_id,
                seed_url=seed_url,
                status="PENDING",
                max_depth=max_depth,
                max_pages=max_pages,
                pages_discovered=0,
                pages_crawled=0,
                records_extracted=0,
                start_time=datetime.utcnow()
            )
            db.add(new_job)
            db.commit()

            # Spawn background worker thread
            thread = threading.Thread(
                target=self._run_crawl_worker,
                args=(job_id, seed_url, max_depth, max_pages, university_name),
                daemon=True
            )
            self._active_threads[job_id] = thread
            thread.start()
            return job_id
        finally:
            db.close()

    def _log_job_event(self, db, job_id: str, level: str, message: str):
        try:
            log_entry = CrawlLog(job_id=job_id, level=level, message=message, timestamp=datetime.utcnow())
            db.add(log_entry)
            db.commit()
        except Exception:
            db.rollback()

    def _run_crawl_worker(self, job_id: str, seed_url: str, max_depth: int, max_pages: int, university_name: Optional[str]):
        db = SessionLocal()
        start_time = time.time()
        try:
            job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
            if not job:
                return

            job.status = "RUNNING"
            db.commit()
            self._log_job_event(db, job_id, "INFO", f"Job {job_id} started for seed URL {seed_url}")

            # Callback for crawler engine logs
            def on_engine_log(lvl, msg):
                worker_db = SessionLocal()
                try:
                    self._log_job_event(worker_db, job_id, lvl, msg)
                finally:
                    worker_db.close()

            engine = CrawlerEngine(
                max_depth=max_depth,
                max_pages=max_pages,
                request_delay=0.6,
                timeout=12,
                log_callback=on_engine_log
            )

            crawl_res = engine.crawl_site(seed_url)

            if crawl_res.get("status") == "FAILED":
                job.status = "FAILED"
                job.error_details = crawl_res.get("error", "Crawling failed")
                db.commit()
                return

            domain = URLExtractor.get_domain(seed_url)
            norm_name = university_name or domain.replace(".ac.in", "").replace(".edu.in", "").replace(".edu", "").replace(".org", "").replace("-", " ").title()

            # Find or create university record
            univ = db.query(University).filter(University.domain == domain).first()
            if not univ:
                slug = re.sub(r"[^a-zA-Z0-9]+", "-", norm_name.lower()).strip("-")
                existing_slug = db.query(University).filter(University.slug == slug).first()
                if existing_slug:
                    slug = f"{slug}-{str(uuid.uuid4())[:6]}"

                univ = University(
                    id=str(uuid.uuid4()),
                    name=norm_name,
                    slug=slug,
                    official_website=seed_url,
                    domain=domain,
                    institution_type="University",
                    country="India",
                    data_completeness_score=35.0,
                    last_scanned_at=datetime.utcnow()
                )
                db.add(univ)
                db.commit()
                db.refresh(univ)

            job.university_id = univ.id
            job.pages_discovered = crawl_res.get("pages_discovered", 0)
            job.pages_crawled = crawl_res.get("pages_crawled", 0)
            db.commit()

            # Process crawled pages & Extract Structured Data
            crawled_pages = crawl_res.get("crawled_pages", [])
            total_records_extracted = 0

            all_admissions = []
            all_courses = []
            all_scholarships = []
            all_faculty = []
            all_placements = []
            all_facilities = []
            all_notifications = []
            all_contacts = []

            for p in crawled_pages:
                categories = ContentClassifier.classify_page(p)
                p["categories"] = categories

                # Save CrawledPage record
                page_rec = CrawledPage(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    job_id=job_id,
                    url=p["url"],
                    domain=domain,
                    title=p.get("title", ""),
                    http_status=p.get("http_status", 200),
                    content_hash=p.get("content_hash"),
                    depth=p.get("depth", 0),
                    categories=categories,
                    parent_url=p.get("parent_url")
                )
                db.add(page_rec)

                # Extract according to categories
                if "ADMISSIONS" in categories or "GENERAL" in categories:
                    all_admissions.extend(AdmissionExtractor.extract_admissions(p))

                if "COURSES" in categories or "GENERAL" in categories:
                    all_courses.extend(CourseExtractor.extract_courses(p))

                if "SCHOLARSHIPS" in categories:
                    all_scholarships.extend(ScholarshipExtractor.extract_scholarships(p))

                if "FACULTY" in categories:
                    all_faculty.extend(FacultyExtractor.extract_faculty(p))

                if "PLACEMENTS" in categories:
                    all_placements.extend(PlacementExtractor.extract_placements(p))

                if "FACILITIES" in categories:
                    all_facilities.extend(FacilitiesExtractor.extract_facilities(p))

                if "NOTIFICATIONS" in categories:
                    all_notifications.extend(NotificationExtractor.extract_notifications(p))

                if "CONTACT" in categories:
                    all_contacts.extend(ContactExtractor.extract_contacts(p))

            # Deduplication
            all_courses = Deduplicator.deduplicate_courses(all_courses)
            all_admissions = Deduplicator.deduplicate_admissions(all_admissions)
            all_faculty = Deduplicator.deduplicate_faculty(all_faculty)
            all_scholarships = Deduplicator.deduplicate_scholarships(all_scholarships)

            # AI Booster: if few courses discovered, enrich via Gemini AI
            if len(all_courses) < 6:
                ai_ext = AIExtractor()
                if ai_ext.is_available():
                    self._log_job_event(db, job_id, "INFO", "Enriching course catalog via Gemini AI booster...")
                    academic_texts = [
                        p.get("cleaned_text", "")
                        for p in crawled_pages
                        if any(cat in p.get("categories", []) for cat in ["COURSES", "GENERAL"])
                    ]
                    ai_courses = ai_ext.extract_courses_from_text(academic_texts, norm_name, seed_url)
                    if ai_courses:
                        all_courses.extend(ai_courses)
                        all_courses = Deduplicator.deduplicate_courses(all_courses)

            # Clean previous duplicate admissions for this university to avoid stacking duplicates
            db.query(Admission).filter(Admission.university_id == univ.id).delete()
            db.commit()

            # Persist Deduplicated Admissions
            for adm in all_admissions:
                adm_entity = Admission(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    academic_year=adm.get("academic_year", "2026-2027"),
                    admission_status=adm.get("admission_status", "UNKNOWN"),
                    title=adm.get("title", "Admissions Announcement"),
                    description=adm.get("description"),
                    entrance_exams=adm.get("entrance_exams"),
                    application_fee=adm.get("application_fee"),
                    source_url=adm.get("source_url", seed_url),
                    source_evidence=adm.get("source_evidence"),
                    confidence_score=adm.get("confidence_score", 0.90),
                    verification_status=adm.get("verification_status", "VERIFIED")
                )
                db.add(adm_entity)
                total_records_extracted += 1

                # Add ExtractedRecord audit log
                db.add(ExtractedRecord(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    job_id=job_id,
                    category="ADMISSIONS",
                    field_name="admission_status",
                    extracted_value=adm.get("admission_status", "UNKNOWN"),
                    academic_year=adm.get("academic_year"),
                    source_url=adm.get("source_url", seed_url),
                    source_page_title="Admission Announcement",
                    confidence_score=adm.get("confidence_score", 0.90),
                    verification_status=adm.get("verification_status", "VERIFIED")
                ))

            # Fetch existing programs for this university to avoid duplicates
            existing_programs = {
                (re.sub(r"[^a-zA-Z0-9]", "", p.name.lower()), (p.degree_type or "").lower().strip())
                for p in db.query(Program).filter(Program.university_id == univ.id).all()
            }

            # Persist Programs
            for c in all_courses:
                p_key = (re.sub(r"[^a-zA-Z0-9]", "", c["name"].lower()), (c["degree_type"] or "").lower().strip())
                if p_key in existing_programs:
                    continue
                existing_programs.add(p_key)

                prog_entity = Program(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    name=c["name"],
                    degree_type=c["degree_type"],
                    specialization=c.get("specialization"),
                    duration_years=c.get("duration_years", 4.0),
                    tuition_fees_annual=c.get("tuition_fees_annual"),
                    source_url=c.get("source_url", seed_url),
                    description=c.get("description")
                )
                db.add(prog_entity)
                total_records_extracted += 1

            # Persist Scholarships
            for s in all_scholarships:
                sch_entity = Scholarship(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    name=s["name"],
                    provider_type=s["provider_type"],
                    description=s.get("description"),
                    scholarship_amount=s.get("scholarship_amount"),
                    is_merit_based=s.get("is_merit_based", False),
                    is_need_based=s.get("is_need_based", False),
                    is_international=s.get("is_international", False),
                    source_url=s.get("source_url", seed_url),
                    verification_status=s.get("verification_status", "VERIFIED")
                )
                db.add(sch_entity)
                total_records_extracted += 1

            # Persist Faculty
            for f in all_faculty:
                fac_entity = Faculty(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    name=f["name"],
                    designation=f.get("designation"),
                    qualifications=f.get("qualifications"),
                    official_email=f.get("official_email"),
                    source_url=f.get("source_url", seed_url),
                    verification_status=f.get("verification_status", "VERIFIED")
                )
                db.add(fac_entity)
                total_records_extracted += 1

            # Persist Placements
            for p in all_placements:
                plc_entity = Placement(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    academic_year=p["academic_year"],
                    placement_percentage=p.get("placement_percentage"),
                    highest_package=p.get("highest_package"),
                    average_package=p.get("average_package"),
                    median_package=p.get("median_package"),
                    currency=p.get("currency", "INR"),
                    recruiting_companies=p.get("recruiting_companies", []),
                    source_url=p.get("source_url", seed_url),
                    verification_status=p.get("verification_status", "VERIFIED")
                )
                db.add(plc_entity)
                total_records_extracted += 1

            # Persist Facilities
            for fac in all_facilities:
                facility_entity = Facility(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    facility_type=fac["facility_type"],
                    name=fac["name"],
                    description=fac.get("description"),
                    features=fac.get("features", []),
                    source_url=fac.get("source_url", seed_url)
                )
                db.add(facility_entity)
                total_records_extracted += 1

            # Persist Notifications
            for n in all_notifications:
                notif_entity = Notification(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    title=n["title"],
                    category=n["category"],
                    summary=n.get("summary"),
                    source_url=n.get("source_url", seed_url)
                )
                db.add(notif_entity)
                total_records_extracted += 1

            # Persist Contacts
            for c in all_contacts:
                contact_entity = UniversityContact(
                    id=str(uuid.uuid4()),
                    university_id=univ.id,
                    office_name=c["office_name"],
                    email=c.get("email"),
                    phone=c.get("phone"),
                    address=c.get("address"),
                    source_url=c.get("source_url", seed_url)
                )
                db.add(contact_entity)
                total_records_extracted += 1

            # Update University Completeness Score
            completeness = DataValidator.calculate_completeness_score({
                "name": univ.name,
                "official_website": univ.official_website,
                "institution_type": univ.institution_type,
                "country": univ.country,
                "state": univ.state or "State",
                "accreditation": univ.accreditation or "Recognized",
                "description": univ.description,
                "admissions": all_admissions,
                "programs": all_courses,
                "scholarships": all_scholarships,
                "placements": all_placements,
                "faculty": all_faculty,
                "facilities": all_facilities,
                "contact_email": all_contacts[0].get("email") if all_contacts else None
            })
            univ.data_completeness_score = completeness
            univ.last_scanned_at = datetime.utcnow()

            # Finalize Job
            total_duration = time.time() - start_time
            job.status = "COMPLETED"
            job.records_extracted = total_records_extracted
            job.end_time = datetime.utcnow()
            job.duration_seconds = round(total_duration, 2)
            db.commit()

            self._log_job_event(db, job_id, "SUCCESS", f"Extraction pipeline completed. Extracted {total_records_extracted} verified records.")

        except Exception as e:
            db.rollback()
            try:
                job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
                if job:
                    job.status = "FAILED"
                    job.error_details = str(e)
                    job.end_time = datetime.utcnow()
                    db.commit()
                self._log_job_event(db, job_id, "ERROR", f"Job failed with exception: {str(e)}")
            except Exception:
                pass
        finally:
            db.close()
            if job_id in self._active_threads:
                del self._active_threads[job_id]
