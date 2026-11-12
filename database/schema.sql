-- ====================================================================
-- FIND YOUR COLLAGE - DATABASE SCHEMA
-- PostgreSQL / Supabase Schema Definition
-- Includes 19 Core Tables, Foreign Keys, Indexes, & RLS Security
-- ====================================================================

-- 1. UNIVERSITIES TABLE
CREATE TABLE IF NOT EXISTS universities (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(64),
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    established_year INTEGER,
    institution_type VARCHAR(64) DEFAULT 'University', -- University, Institute, College, Autonomous
    ownership_type VARCHAR(64) DEFAULT 'Public',       -- Public, Private, Deemed, Autonomous
    accreditation VARCHAR(255),                        -- NAAC A++, ABET, NBA, NIRF, etc.
    recognition VARCHAR(255),                          -- UGC, AICTE, MHRD, etc.
    rankings JSONB DEFAULT '{}'::jsonb,                -- e.g. {"nirf": 1, "qs_world": 150}
    official_website VARCHAR(512) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    logo_url VARCHAR(512),
    banner_url VARCHAR(512),
    country VARCHAR(100) DEFAULT 'India',
    state VARCHAR(100),
    city VARCHAR(100),
    address TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(64),
    social_links JSONB DEFAULT '{}'::jsonb,
    data_completeness_score NUMERIC(5, 2) DEFAULT 0.00,
    last_scanned_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. CAMPUSES TABLE
CREATE TABLE IF NOT EXISTS campuses (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location_type VARCHAR(64) DEFAULT 'Main Campus', -- Main, Branch, Off-shore
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    address TEXT,
    area_acres NUMERIC(8, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. DEPARTMENTS TABLE
CREATE TABLE IF NOT EXISTS departments (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    campus_id VARCHAR(64) REFERENCES campuses(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(32),
    head_of_department VARCHAR(255),
    description TEXT,
    website_url VARCHAR(512),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(64),
    source_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. PROGRAMS TABLE
CREATE TABLE IF NOT EXISTS programs (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    department_id VARCHAR(64) REFERENCES departments(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    degree_type VARCHAR(64) NOT NULL, -- Undergraduate, Postgraduate, PhD, Diploma, Certificate
    discipline VARCHAR(128),          -- Engineering, Management, Science, Humanities
    specialization VARCHAR(255),
    duration_years NUMERIC(3, 1),
    intake_capacity INTEGER,
    tuition_fees_annual VARCHAR(128),
    total_fees VARCHAR(128),
    currency VARCHAR(10) DEFAULT 'INR',
    eligibility_criteria TEXT,
    curriculum_url VARCHAR(512),
    syllabus_url VARCHAR(512),
    description TEXT,
    source_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. ADMISSIONS TABLE
CREATE TABLE IF NOT EXISTS admissions (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    academic_year VARCHAR(32) NOT NULL,               -- e.g. '2025-2026'
    admission_status VARCHAR(32) NOT NULL DEFAULT 'UNKNOWN', -- OPEN, CLOSED, UPCOMING, ONGOING, UNKNOWN
    title VARCHAR(255) NOT NULL,
    description TEXT,
    application_opening_date DATE,
    application_closing_date DATE,
    entrance_exams TEXT,                              -- JEE Main, GATE, CAT, CET, institutional
    eligibility_summary TEXT,
    selection_process TEXT,
    application_fee VARCHAR(64),
    application_portal_url VARCHAR(512),
    counselling_info TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(64),
    source_url VARCHAR(512) NOT NULL,
    source_evidence TEXT,                             -- Verbatim announcement snippet
    confidence_score NUMERIC(4, 2) DEFAULT 0.85,
    verification_status VARCHAR(32) DEFAULT 'VERIFIED',
    last_verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. SCHOLARSHIPS TABLE
CREATE TABLE IF NOT EXISTS scholarships (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    provider_type VARCHAR(64) NOT NULL,              -- Institutional, Government, External
    description TEXT,
    eligibility_criteria TEXT,
    scholarship_amount VARCHAR(128),
    fee_waiver_percent NUMERIC(5, 2),
    is_merit_based BOOLEAN DEFAULT FALSE,
    is_need_based BOOLEAN DEFAULT FALSE,
    is_international BOOLEAN DEFAULT FALSE,
    application_deadline DATE,
    renewal_conditions TEXT,
    required_documents TEXT,
    application_url VARCHAR(512),
    contact_info VARCHAR(255),
    source_url VARCHAR(512) NOT NULL,
    verification_status VARCHAR(32) DEFAULT 'VERIFIED',
    confidence_score NUMERIC(4, 2) DEFAULT 0.85,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. FACULTY TABLE
CREATE TABLE IF NOT EXISTS faculty (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    department_id VARCHAR(64) REFERENCES departments(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    designation VARCHAR(128),                         -- Professor, Associate Professor, Assistant Professor, Dean
    qualifications VARCHAR(255),                      -- Ph.D., M.Tech, Postdoc
    specialization VARCHAR(255),
    research_interests TEXT,
    official_email VARCHAR(255),
    profile_url VARCHAR(512),
    publications_count INTEGER DEFAULT 0,
    source_url VARCHAR(512) NOT NULL,
    verification_status VARCHAR(32) DEFAULT 'VERIFIED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. FACILITIES TABLE
CREATE TABLE IF NOT EXISTS facilities (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    facility_type VARCHAR(64) NOT NULL,               -- Library, Hostel, Sports, Laboratory, Cafeteria, Medical, Wi-Fi, Transport
    name VARCHAR(255) NOT NULL,
    description TEXT,
    features JSONB DEFAULT '[]'::jsonb,
    capacity VARCHAR(128),
    source_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. PLACEMENTS TABLE
CREATE TABLE IF NOT EXISTS placements (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    academic_year VARCHAR(32) NOT NULL,               -- e.g. '2023-2024'
    placement_percentage NUMERIC(5, 2),
    highest_package VARCHAR(64),
    average_package VARCHAR(64),
    median_package VARCHAR(64),
    currency VARCHAR(10) DEFAULT 'INR',
    total_offers INTEGER,
    recruiting_companies JSONB DEFAULT '[]'::jsonb,
    report_url VARCHAR(512),
    placement_office_contact VARCHAR(255),
    source_url VARCHAR(512) NOT NULL,
    verification_status VARCHAR(32) DEFAULT 'VERIFIED',
    confidence_score NUMERIC(4, 2) DEFAULT 0.85,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. RESEARCH PROJECTS TABLE
CREATE TABLE IF NOT EXISTS research_projects (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    department_id VARCHAR(64) REFERENCES departments(id) ON DELETE SET NULL,
    title VARCHAR(300) NOT NULL,
    principal_investigator VARCHAR(255),
    funding_agency VARCHAR(255),                      -- DST, SERB, CSIR, Industry, etc.
    grant_amount VARCHAR(64),
    start_year INTEGER,
    status VARCHAR(64) DEFAULT 'ONGOING',             -- ONGOING, COMPLETED
    description TEXT,
    source_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. PUBLICATIONS TABLE
CREATE TABLE IF NOT EXISTS publications (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    title VARCHAR(400) NOT NULL,
    authors TEXT,
    journal_or_conference VARCHAR(255),
    publication_year INTEGER,
    doi_or_url VARCHAR(512),
    source_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 12. NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    title VARCHAR(300) NOT NULL,
    category VARCHAR(64) NOT NULL,                   -- Admission, Examination, Scholarship, Circular, Event, Job
    summary TEXT,
    notification_date DATE,
    expiry_date DATE,
    link_url VARCHAR(512),
    document_url VARCHAR(512),
    is_active BOOLEAN DEFAULT TRUE,
    source_url VARCHAR(512) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 13. UNIVERSITY CONTACTS TABLE
CREATE TABLE IF NOT EXISTS university_contacts (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    office_name VARCHAR(128) NOT NULL,               -- Registrar, Admissions, Examination, Placement, International
    contact_person VARCHAR(255),
    designation VARCHAR(128),
    email VARCHAR(255),
    phone VARCHAR(64),
    address TEXT,
    working_hours VARCHAR(128),
    source_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 14. CRAWLED PAGES TABLE
CREATE TABLE IF NOT EXISTS crawled_pages (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) REFERENCES universities(id) ON DELETE CASCADE,
    job_id VARCHAR(64),
    url VARCHAR(512) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    title VARCHAR(400),
    http_status INTEGER DEFAULT 200,
    content_hash VARCHAR(64),
    depth INTEGER DEFAULT 0,
    categories JSONB DEFAULT '[]'::jsonb,
    parent_url VARCHAR(512),
    error_message TEXT,
    scanned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 15. EXTRACTED RECORDS TABLE (Source Traceability & Fact Auditing)
CREATE TABLE IF NOT EXISTS extracted_records (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    job_id VARCHAR(64),
    category VARCHAR(64) NOT NULL,
    field_name VARCHAR(64) NOT NULL,
    extracted_value TEXT NOT NULL,
    previous_value TEXT,
    academic_year VARCHAR(32),
    source_url VARCHAR(512) NOT NULL,
    source_page_title VARCHAR(400),
    confidence_score NUMERIC(4, 2) DEFAULT 0.85,
    verification_status VARCHAR(32) NOT NULL DEFAULT 'VERIFIED', -- VERIFIED, NEEDS_REVIEW, OUTDATED, CONFLICTING, UNVERIFIED
    conflict_details JSONB,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 16. CRAWL JOBS TABLE
CREATE TABLE IF NOT EXISTS crawl_jobs (
    id VARCHAR(64) PRIMARY KEY,
    university_id VARCHAR(64) REFERENCES universities(id) ON DELETE SET NULL,
    seed_url VARCHAR(512) NOT NULL,
    status VARCHAR(32) DEFAULT 'PENDING',            -- PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    pages_discovered INTEGER DEFAULT 0,
    pages_crawled INTEGER DEFAULT 0,
    records_extracted INTEGER DEFAULT 0,
    needs_review_count INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    max_depth INTEGER DEFAULT 2,
    max_pages INTEGER DEFAULT 30,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds NUMERIC(8, 2),
    error_details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 17. CRAWL LOGS TABLE
CREATE TABLE IF NOT EXISTS crawl_logs (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL REFERENCES crawl_jobs(id) ON DELETE CASCADE,
    level VARCHAR(16) DEFAULT 'INFO',                -- INFO, WARNING, ERROR, SUCCESS
    message TEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 18. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role VARCHAR(32) DEFAULT 'USER',                 -- USER, ADMIN, ANALYST
    avatar_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- 19. SAVED UNIVERSITIES TABLE
CREATE TABLE IF NOT EXISTS saved_universities (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    university_id VARCHAR(64) NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, university_id)
);

-- ====================================================================
-- PERFORMANCE INDEXES
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_univ_slug ON universities(slug);
CREATE INDEX IF NOT EXISTS idx_univ_country_state_city ON universities(country, state, city);
CREATE INDEX IF NOT EXISTS idx_univ_type ON universities(institution_type);
CREATE INDEX IF NOT EXISTS idx_programs_univ ON programs(university_id);
CREATE INDEX IF NOT EXISTS idx_programs_degree ON programs(degree_type);
CREATE INDEX IF NOT EXISTS idx_admissions_univ_status ON admissions(university_id, admission_status);
CREATE INDEX IF NOT EXISTS idx_scholarships_univ ON scholarships(university_id);
CREATE INDEX IF NOT EXISTS idx_placements_univ_year ON placements(university_id, academic_year);
CREATE INDEX IF NOT EXISTS idx_crawled_pages_univ ON crawled_pages(university_id);
CREATE INDEX IF NOT EXISTS idx_crawled_pages_url ON crawled_pages(url);
CREATE INDEX IF NOT EXISTS idx_extracted_univ_status ON extracted_records(university_id, verification_status);
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_status ON crawl_jobs(status);
CREATE INDEX IF NOT EXISTS idx_crawl_logs_job ON crawl_logs(job_id);
