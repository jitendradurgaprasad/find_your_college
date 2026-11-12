from datetime import datetime
import uuid
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    Date, ForeignKey, Numeric, JSON
)
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class University(Base):
    __tablename__ = "universities"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    short_name = Column(String(64), nullable=True)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    established_year = Column(Integer, nullable=True)
    institution_type = Column(String(64), default="University") # University, Institute, College
    ownership_type = Column(String(64), default="Public")       # Public, Private, Deemed
    accreditation = Column(String(255), nullable=True)
    recognition = Column(String(255), nullable=True)
    rankings = Column(JSON, default=dict)
    official_website = Column(String(512), nullable=False)
    domain = Column(String(255), nullable=False)
    logo_url = Column(String(512), nullable=True)
    banner_url = Column(String(512), nullable=True)
    country = Column(String(100), default="India")
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(64), nullable=True)
    social_links = Column(JSON, default=dict)
    data_completeness_score = Column(Numeric(5, 2), default=0.00)
    last_scanned_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campuses = relationship("Campus", back_populates="university", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="university", cascade="all, delete-orphan")
    programs = relationship("Program", back_populates="university", cascade="all, delete-orphan")
    admissions = relationship("Admission", back_populates="university", cascade="all, delete-orphan")
    scholarships = relationship("Scholarship", back_populates="university", cascade="all, delete-orphan")
    faculty_members = relationship("Faculty", back_populates="university", cascade="all, delete-orphan")
    facilities = relationship("Facility", back_populates="university", cascade="all, delete-orphan")
    placements = relationship("Placement", back_populates="university", cascade="all, delete-orphan")
    research_projects = relationship("ResearchProject", back_populates="university", cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="university", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="university", cascade="all, delete-orphan")
    contacts = relationship("UniversityContact", back_populates="university", cascade="all, delete-orphan")
    crawled_pages = relationship("CrawledPage", back_populates="university", cascade="all, delete-orphan")
    extracted_records = relationship("ExtractedRecord", back_populates="university", cascade="all, delete-orphan")

class Campus(Base):
    __tablename__ = "campuses"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    location_type = Column(String(64), default="Main Campus")
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    address = Column(Text, nullable=True)
    area_acres = Column(Numeric(8, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="campuses")

class Department(Base):
    __tablename__ = "departments"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    campus_id = Column(String(64), ForeignKey("campuses.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(32), nullable=True)
    head_of_department = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    website_url = Column(String(512), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(64), nullable=True)
    source_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="departments")
    programs = relationship("Program", back_populates="department")
    faculty_members = relationship("Faculty", back_populates="department")

class Program(Base):
    __tablename__ = "programs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(String(64), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    degree_type = Column(String(64), nullable=False) # Undergraduate, Postgraduate, PhD, Diploma
    discipline = Column(String(128), nullable=True)
    specialization = Column(String(255), nullable=True)
    duration_years = Column(Numeric(3, 1), nullable=True)
    intake_capacity = Column(Integer, nullable=True)
    tuition_fees_annual = Column(String(128), nullable=True)
    total_fees = Column(String(128), nullable=True)
    currency = Column(String(10), default="INR")
    eligibility_criteria = Column(Text, nullable=True)
    curriculum_url = Column(String(512), nullable=True)
    syllabus_url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    source_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    university = relationship("University", back_populates="programs")
    department = relationship("Department", back_populates="programs")

class Admission(Base):
    __tablename__ = "admissions"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    academic_year = Column(String(32), nullable=False)
    admission_status = Column(String(32), nullable=False, default="UNKNOWN") # OPEN, CLOSED, UPCOMING, ONGOING, UNKNOWN
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    application_opening_date = Column(Date, nullable=True)
    application_closing_date = Column(Date, nullable=True)
    entrance_exams = Column(Text, nullable=True)
    eligibility_summary = Column(Text, nullable=True)
    selection_process = Column(Text, nullable=True)
    application_fee = Column(String(64), nullable=True)
    application_portal_url = Column(String(512), nullable=True)
    counselling_info = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(64), nullable=True)
    source_url = Column(String(512), nullable=False)
    source_evidence = Column(Text, nullable=True)
    confidence_score = Column(Numeric(4, 2), default=0.85)
    verification_status = Column(String(32), default="VERIFIED") # VERIFIED, NEEDS_REVIEW, etc.
    last_verified_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    university = relationship("University", back_populates="admissions")

class Scholarship(Base):
    __tablename__ = "scholarships"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    provider_type = Column(String(64), nullable=False) # Institutional, Government, External
    description = Column(Text, nullable=True)
    eligibility_criteria = Column(Text, nullable=True)
    scholarship_amount = Column(String(128), nullable=True)
    fee_waiver_percent = Column(Numeric(5, 2), nullable=True)
    is_merit_based = Column(Boolean, default=False)
    is_need_based = Column(Boolean, default=False)
    is_international = Column(Boolean, default=False)
    application_deadline = Column(Date, nullable=True)
    renewal_conditions = Column(Text, nullable=True)
    required_documents = Column(Text, nullable=True)
    application_url = Column(String(512), nullable=True)
    contact_info = Column(String(255), nullable=True)
    source_url = Column(String(512), nullable=False)
    verification_status = Column(String(32), default="VERIFIED")
    confidence_score = Column(Numeric(4, 2), default=0.85)
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="scholarships")

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(String(64), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    designation = Column(String(128), nullable=True)
    qualifications = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    research_interests = Column(Text, nullable=True)
    official_email = Column(String(255), nullable=True)
    profile_url = Column(String(512), nullable=True)
    publications_count = Column(Integer, default=0)
    source_url = Column(String(512), nullable=False)
    verification_status = Column(String(32), default="VERIFIED")
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="faculty_members")
    department = relationship("Department", back_populates="faculty_members")

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    facility_type = Column(String(64), nullable=False) # Library, Hostel, Sports, Laboratory, etc.
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    features = Column(JSON, default=list)
    capacity = Column(String(128), nullable=True)
    source_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="facilities")

class Placement(Base):
    __tablename__ = "placements"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    academic_year = Column(String(32), nullable=False)
    placement_percentage = Column(Numeric(5, 2), nullable=True)
    highest_package = Column(String(64), nullable=True)
    average_package = Column(String(64), nullable=True)
    median_package = Column(String(64), nullable=True)
    currency = Column(String(10), default="INR")
    total_offers = Column(Integer, nullable=True)
    recruiting_companies = Column(JSON, default=list)
    report_url = Column(String(512), nullable=True)
    placement_office_contact = Column(String(255), nullable=True)
    source_url = Column(String(512), nullable=False)
    verification_status = Column(String(32), default="VERIFIED")
    confidence_score = Column(Numeric(4, 2), default=0.85)
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="placements")

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(String(64), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(300), nullable=False)
    principal_investigator = Column(String(255), nullable=True)
    funding_agency = Column(String(255), nullable=True)
    grant_amount = Column(String(64), nullable=True)
    start_year = Column(Integer, nullable=True)
    status = Column(String(64), default="ONGOING")
    description = Column(Text, nullable=True)
    source_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="research_projects")

class Publication(Base):
    __tablename__ = "publications"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(400), nullable=False)
    authors = Column(Text, nullable=True)
    journal_or_conference = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True)
    doi_or_url = Column(String(512), nullable=True)
    source_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="publications")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(300), nullable=False)
    category = Column(String(64), nullable=False) # Admission, Examination, Scholarship, Circular, Event
    summary = Column(Text, nullable=True)
    notification_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    link_url = Column(String(512), nullable=True)
    document_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)
    source_url = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="notifications")

class UniversityContact(Base):
    __tablename__ = "university_contacts"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    office_name = Column(String(128), nullable=False)
    contact_person = Column(String(255), nullable=True)
    designation = Column(String(128), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    address = Column(Text, nullable=True)
    working_hours = Column(String(128), nullable=True)
    source_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="contacts")

class CrawledPage(Base):
    __tablename__ = "crawled_pages"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=True)
    job_id = Column(String(64), nullable=True)
    url = Column(String(512), nullable=False)
    domain = Column(String(255), nullable=False)
    title = Column(String(400), nullable=True)
    http_status = Column(Integer, default=200)
    content_hash = Column(String(64), nullable=True)
    depth = Column(Integer, default=0)
    categories = Column(JSON, default=list)
    parent_url = Column(String(512), nullable=True)
    error_message = Column(Text, nullable=True)
    scanned_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="crawled_pages")

class ExtractedRecord(Base):
    __tablename__ = "extracted_records"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(64), nullable=True)
    category = Column(String(64), nullable=False)
    field_name = Column(String(64), nullable=False)
    extracted_value = Column(Text, nullable=False)
    previous_value = Column(Text, nullable=True)
    academic_year = Column(String(32), nullable=True)
    source_url = Column(String(512), nullable=False)
    source_page_title = Column(String(400), nullable=True)
    confidence_score = Column(Numeric(4, 2), default=0.85)
    verification_status = Column(String(32), nullable=False, default="VERIFIED")
    conflict_details = Column(JSON, nullable=True)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="extracted_records")

class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="SET NULL"), nullable=True)
    seed_url = Column(String(512), nullable=False)
    status = Column(String(32), default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    pages_discovered = Column(Integer, default=0)
    pages_crawled = Column(Integer, default=0)
    records_extracted = Column(Integer, default=0)
    needs_review_count = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    max_depth = Column(Integer, default=2)
    max_pages = Column(Integer, default=30)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Numeric(8, 2), nullable=True)
    error_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    logs = relationship("CrawlLog", back_populates="job", cascade="all, delete-orphan")

class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    job_id = Column(String(64), ForeignKey("crawl_jobs.id", ondelete="CASCADE"), nullable=False)
    level = Column(String(16), default="INFO")
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    job = relationship("CrawlJob", back_populates="logs")

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    role = Column(String(32), default="USER") # USER, ADMIN
    avatar_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

class SavedUniversity(Base):
    __tablename__ = "saved_universities"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    university_id = Column(String(64), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
