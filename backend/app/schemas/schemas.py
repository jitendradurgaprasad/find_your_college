from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# University Schemas
class UniversityBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    official_website: str
    institution_type: Optional[str] = "University"
    ownership_type: Optional[str] = "Public"
    country: Optional[str] = "India"
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    accreditation: Optional[str] = None
    recognition: Optional[str] = None
    description: Optional[str] = None
    established_year: Optional[int] = None
    logo_url: Optional[str] = None

class UniversityCreate(UniversityBase):
    slug: Optional[str] = None

class UniversitySummary(UniversityBase):
    id: str
    slug: str
    data_completeness_score: float
    last_scanned_at: Optional[datetime] = None
    admission_status: Optional[str] = "UNKNOWN"
    has_scholarships: bool = False
    programs_count: int = 0
    faculty_count: int = 0
    created_at: datetime
    model_config = {"from_attributes": True}

# Fact with Source Traceability
class TraceableFact(BaseModel):
    category: str
    field_name: str
    value: str
    source_url: str
    source_page_title: Optional[str] = None
    confidence_score: float = 0.85
    verification_status: str = "VERIFIED"
    academic_year: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

# Admission Schema
class AdmissionSchema(BaseModel):
    id: str
    academic_year: str
    admission_status: str
    title: str
    description: Optional[str] = None
    application_opening_date: Optional[date] = None
    application_closing_date: Optional[date] = None
    entrance_exams: Optional[str] = None
    eligibility_summary: Optional[str] = None
    selection_process: Optional[str] = None
    application_fee: Optional[str] = None
    application_portal_url: Optional[str] = None
    counselling_info: Optional[str] = None
    source_url: str
    source_evidence: Optional[str] = None
    confidence_score: float
    verification_status: str
    last_verified_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

# Program Schema
class ProgramSchema(BaseModel):
    id: str
    name: str
    degree_type: str
    discipline: Optional[str] = None
    specialization: Optional[str] = None
    duration_years: Optional[float] = None
    intake_capacity: Optional[int] = None
    tuition_fees_annual: Optional[str] = None
    total_fees: Optional[str] = None
    currency: Optional[str] = "INR"
    eligibility_criteria: Optional[str] = None
    curriculum_url: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    model_config = {"from_attributes": True}

# Scholarship Schema
class ScholarshipSchema(BaseModel):
    id: str
    name: str
    provider_type: str
    description: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    scholarship_amount: Optional[str] = None
    fee_waiver_percent: Optional[float] = None
    is_merit_based: bool = False
    is_need_based: bool = False
    is_international: bool = False
    application_deadline: Optional[date] = None
    application_url: Optional[str] = None
    source_url: str
    verification_status: str
    model_config = {"from_attributes": True}

# Faculty Schema
class FacultySchema(BaseModel):
    id: str
    name: str
    designation: Optional[str] = None
    qualifications: Optional[str] = None
    specialization: Optional[str] = None
    research_interests: Optional[str] = None
    official_email: Optional[str] = None
    profile_url: Optional[str] = None
    department_name: Optional[str] = None
    source_url: str
    verification_status: str
    model_config = {"from_attributes": True}

# Placement Schema
class PlacementSchema(BaseModel):
    id: str
    academic_year: str
    placement_percentage: Optional[float] = None
    highest_package: Optional[str] = None
    average_package: Optional[str] = None
    median_package: Optional[str] = None
    currency: Optional[str] = "INR"
    total_offers: Optional[int] = None
    recruiting_companies: List[str] = []
    report_url: Optional[str] = None
    source_url: str
    verification_status: str
    model_config = {"from_attributes": True}

# Facility Schema
class FacilitySchema(BaseModel):
    id: str
    facility_type: str
    name: str
    description: Optional[str] = None
    features: List[str] = []
    source_url: Optional[str] = None
    model_config = {"from_attributes": True}

# Research Project Schema
class ResearchProjectSchema(BaseModel):
    id: str
    title: str
    principal_investigator: Optional[str] = None
    funding_agency: Optional[str] = None
    grant_amount: Optional[str] = None
    start_year: Optional[int] = None
    status: str = "ONGOING"
    description: Optional[str] = None
    source_url: Optional[str] = None
    model_config = {"from_attributes": True}

# Notification Schema
class NotificationSchema(BaseModel):
    id: str
    title: str
    category: str
    summary: Optional[str] = None
    notification_date: Optional[date] = None
    expiry_date: Optional[date] = None
    link_url: Optional[str] = None
    document_url: Optional[str] = None
    source_url: str
    model_config = {"from_attributes": True}

# Contact Schema
class ContactSchema(BaseModel):
    id: str
    office_name: str
    contact_person: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    source_url: Optional[str] = None
    model_config = {"from_attributes": True}

# Detailed University Profile
class UniversityProfile(UniversitySummary):
    admissions: List[AdmissionSchema] = []
    programs: List[ProgramSchema] = []
    scholarships: List[ScholarshipSchema] = []
    faculty: List[FacultySchema] = []
    placements: List[PlacementSchema] = []
    facilities: List[FacilitySchema] = []
    research_projects: List[ResearchProjectSchema] = []
    notifications: List[NotificationSchema] = []
    contacts: List[ContactSchema] = []
    traceable_facts: List[TraceableFact] = []
    model_config = {"from_attributes": True}

# Crawl Job Schemas
class CrawlStartRequest(BaseModel):
    url: str
    max_depth: Optional[int] = 2
    max_pages: Optional[int] = 25
    university_name: Optional[str] = None

class CrawlLogSchema(BaseModel):
    level: str
    message: str
    timestamp: datetime
    model_config = {"from_attributes": True}

class CrawlJobStatus(BaseModel):
    job_id: str
    seed_url: str
    status: str
    pages_discovered: int
    pages_crawled: int
    records_extracted: int
    needs_review_count: int
    errors_count: int
    max_depth: int
    max_pages: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    university_id: Optional[str] = None
    university_name: Optional[str] = None
    university_slug: Optional[str] = None
    extracted_summary: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    logs: List[CrawlLogSchema] = []
    model_config = {"from_attributes": True}

# Search Query Request & Response
class SearchRequest(BaseModel):
    query: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    institution_type: Optional[str] = None
    degree_type: Optional[str] = None
    course: Optional[str] = None
    admission_status: Optional[str] = None
    has_scholarship: Optional[bool] = None
    page: int = 1
    page_size: int = 12

class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    results: List[UniversitySummary]

# College Comparison Schema
class CompareRequest(BaseModel):
    university_ids: List[str]

class ComparisonItem(BaseModel):
    id: str
    name: str
    logo_url: Optional[str] = None
    official_website: str
    location: str
    institution_type: str
    ownership: str
    accreditation: Optional[str] = "Information unavailable"
    admission_status: str
    academic_year: Optional[str] = "Information unavailable"
    programs_offered_count: int
    sample_programs: List[str]
    tuition_fee_range: str
    scholarships_count: int
    placement_rate: Optional[str] = "Information unavailable"
    highest_package: Optional[str] = "Information unavailable"
    average_package: Optional[str] = "Information unavailable"
    facilities: List[str]
    data_completeness_score: float

class CompareResponse(BaseModel):
    colleges: List[ComparisonItem]

# Data Quality Metrics Schema
class QualityMetricsResponse(BaseModel):
    total_institutions: int
    total_crawled_pages: int
    total_extracted_records: int
    verified_records: int
    needs_review_records: int
    outdated_records: int
    conflicting_records: int
    duplicate_records_detected: int
    average_completeness_score: float
    category_breakdown: Dict[str, int]
    recent_conflicts: List[Dict[str, Any]] = []

# Monitoring Change History
class MonitoringChange(BaseModel):
    university_name: str
    category: str
    field_name: str
    change_type: str # NEW, MODIFIED, REMOVED
    previous_value: Optional[str] = None
    current_value: Optional[str] = None
    detected_at: datetime
    source_url: str

# Auto-Suggestion & Autocomplete Schema
class CollegeSuggestion(BaseModel):
    id: Optional[str] = None
    name: str
    short_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    official_website: Optional[str] = None
    slug: Optional[str] = None
    institution_type: Optional[str] = None
    data_completeness_score: Optional[float] = None
    is_in_database: bool = True
    model_config = {"from_attributes": True}

# Auto URL Resolution Schema
class URLResolveResponse(BaseModel):
    name: str
    official_website: str
    domain: str
    confidence: float
    source: str
    is_accessible: bool
    note: Optional[str] = None

# AI Smart Search Schemas
class AISearchRequest(BaseModel):
    query: str
    api_key: Optional[str] = None

class RecommendedInstitution(BaseModel):
    name: str
    location: Optional[str] = None
    official_website: Optional[str] = None
    key_highlights: Optional[str] = None
    why_recommended: Optional[str] = None
    matched_id: Optional[str] = None

class AISearchResponse(BaseModel):
    query: str
    ai_answer: str
    recommended_institutions: List[RecommendedInstitution] = []
    matched_colleges: List[UniversitySummary] = []
    confidence: float = 0.95
    source: str = "Gemini AI"
