import pytest
from crawler.url_extractor import URLExtractor
from crawler.html_parser import HTMLParser
from crawler.robots_checker import RobotsChecker
from extraction.classifier import ContentClassifier
from extraction.admission_extractor import AdmissionExtractor
from extraction.course_extractor import CourseExtractor
from extraction.scholarship_extractor import ScholarshipExtractor
from extraction.placement_extractor import PlacementExtractor
from quality.validator import DataValidator
from quality.verifier import DataVerifier

MOCK_HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>National Institute of Technology - Admissions 2025-2026</title>
    <meta name="description" content="Official portal for NIT engineering admissions, faculty and placements.">
</head>
<body>
    <h1>National Institute of Technology</h1>
    <h2>Admissions are open for academic session 2025-2026</h2>
    <p>Applications are invited for B.Tech in Computer Science and Engineering and Artificial Intelligence. The last date to apply is 30th June 2025.</p>
    <p>Admission is strictly through JEE Main ranking and centralized seat allocation.</p>
    <p>Application fee is ₹1500 for general category.</p>

    <h3>Scholarships and Financial Aid</h3>
    <p>The Merit-cum-Means Scholarship offers up to ₹50,000 per annum for deserving candidates with parental income below 5 LPA.</p>

    <h3>Training and Placements</h3>
    <p>For the batch 2023-2024, the placement percentage reached 94.5%. Highest package was 54 LPA and average package was 18.2 LPA.</p>
    <p>Top recruiters included Google, Microsoft, Amazon, and Qualcomm.</p>

    <h3>Faculty Directory</h3>
    <table>
        <tr><th>Name</th><th>Designation</th><th>Email</th></tr>
        <tr><td>Dr. Rajesh Sharma</td><td>Professor</td><td>rajesh@nit.edu</td></tr>
        <tr><td>Prof. Sunita Verma</td><td>Associate Professor</td><td>sunita@nit.edu</td></tr>
    </table>
</body>
</html>
"""

def test_ssrf_protection():
    # Loopback & private IPs should be blocked
    assert URLExtractor.is_ssrf_safe("http://127.0.0.1:8080/admin") is False
    assert URLExtractor.is_ssrf_safe("http://localhost:3000") is False
    assert URLExtractor.is_ssrf_safe("http://169.254.169.254/latest/meta-data/") is False
    # Public domain should pass
    assert URLExtractor.is_ssrf_safe("https://www.iitb.ac.in") is True

def test_url_normalization():
    norm = URLExtractor.normalize_url("/admissions/btech#apply", "https://www.nit.edu/about/")
    assert norm == "https://www.nit.edu/admissions/btech"
    # PDF detection
    assert URLExtractor.is_pdf("https://nit.edu/brochure.pdf") is True
    assert URLExtractor.is_pdf("https://nit.edu/admissions") is False

def test_html_parser():
    parsed = HTMLParser.parse_page(MOCK_HTML_PAGE, "https://www.nit.edu/admissions")
    assert "National Institute of Technology" in parsed["title"]
    assert len(parsed["headings"]["h1"]) >= 1
    assert len(parsed["headings"]["h2"]) >= 1
    assert len(parsed["tables"]) == 1

def test_page_classifier():
    page = HTMLParser.parse_page(MOCK_HTML_PAGE, "https://www.nit.edu/admissions/btech")
    categories = ContentClassifier.classify_page(page)
    assert "ADMISSIONS" in categories
    assert "COURSES" in categories
    assert "PLACEMENTS" in categories

def test_admission_extractor():
    page = HTMLParser.parse_page(MOCK_HTML_PAGE, "https://www.nit.edu/admissions")
    admissions = AdmissionExtractor.extract_admissions(page)
    assert len(admissions) == 1
    adm = admissions[0]
    assert adm["admission_status"] == "OPEN"
    assert "2025" in adm["academic_year"]
    assert "JEE Main" in adm["entrance_exams"]
    assert adm["verification_status"] == "VERIFIED"

def test_course_extractor():
    page = HTMLParser.parse_page(MOCK_HTML_PAGE, "https://www.nit.edu/courses")
    courses = CourseExtractor.extract_courses(page)
    assert len(courses) >= 1
    course_names = [c["name"] for c in courses]
    assert any("Computer Science" in name or "B.Tech" in name for name in course_names)

def test_scholarship_extractor():
    page = HTMLParser.parse_page(MOCK_HTML_PAGE, "https://www.nit.edu/scholarships")
    scholarships = ScholarshipExtractor.extract_scholarships(page)
    assert len(scholarships) >= 1
    assert scholarships[0]["verification_status"] == "VERIFIED"

def test_placement_extractor():
    page = HTMLParser.parse_page(MOCK_HTML_PAGE, "https://www.nit.edu/placements")
    placements = PlacementExtractor.extract_placements(page)
    assert len(placements) == 1
    plc = placements[0]
    assert plc["placement_percentage"] == 94.5
    assert "54" in plc["highest_package"]
    assert "18.2" in plc["average_package"]
    assert "Google" in plc["recruiting_companies"]

def test_data_validator():
    assert DataValidator.is_valid_email("admissions@iitb.ac.in") is True
    assert DataValidator.is_valid_email("invalid-email") is False
    assert DataValidator.is_valid_url("https://www.iiit.ac.in") is True
    assert DataValidator.is_valid_url("not_a_url") is False

def test_data_verifier_and_conflict_detection():
    # Verifying single fact
    eval_res = DataVerifier.evaluate_record(
        category="ADMISSIONS",
        field_name="status",
        value="OPEN",
        source_url="https://nit.edu/admissions",
        academic_year="2025-2026",
        confidence_score=0.95
    )
    assert eval_res["status"] == "VERIFIED"

    # Conflicting records across two URLs
    records = [
        {"category": "ADMISSIONS", "field_name": "status", "academic_year": "2025-2026", "extracted_value": "OPEN", "source_url": "https://nit.edu/notice1"},
        {"category": "ADMISSIONS", "field_name": "status", "academic_year": "2025-2026", "extracted_value": "CLOSED", "source_url": "https://nit.edu/notice2"}
    ]
    detected = DataVerifier.detect_conflicts(records)
    assert detected[0]["verification_status"] == "CONFLICTING"
    assert detected[1]["verification_status"] == "CONFLICTING"
