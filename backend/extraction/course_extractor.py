import re
from typing import Dict, List, Any

DEGREE_MAPPINGS = [
    (r"\b(b\.?tech|bachelor of technology|b\.?e\b)", "Undergraduate", "B.Tech"),
    (r"\b(m\.?tech|master of technology|m\.?e\b)", "Postgraduate", "M.Tech"),
    (r"\b(b\.?sc|bachelor of science)", "Undergraduate", "B.Sc"),
    (r"\b(m\.?sc|master of science)", "Postgraduate", "M.Sc"),
    (r"\b(mba|master of business administration)", "Postgraduate", "MBA"),
    (r"\b(bba|bachelor of business administration)", "Undergraduate", "BBA"),
    (r"\b(bca|bachelor of computer applications)", "Undergraduate", "BCA"),
    (r"\b(mca|master of computer applications)", "Postgraduate", "MCA"),
    (r"\b(ph\.?d|doctor of philosophy)", "PhD", "Ph.D"),
    (r"\b(diploma in|post graduate diploma)", "Diploma", "Diploma")
]

SPECIALIZATIONS = [
    "Computer Science and Engineering", "Artificial Intelligence and Machine Learning",
    "Data Science", "Electronics and Communication Engineering",
    "Electrical and Electronics Engineering", "Mechanical Engineering",
    "Civil Engineering", "Biotechnology", "Information Technology",
    "Robotics and Automation", "Aerospace Engineering", "Cybersecurity",
    "Finance", "Marketing", "Human Resources", "Physics", "Chemistry", "Mathematics"
]

class CourseExtractor:
    @staticmethod
    def extract_courses(page: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts structured courses, degrees, specializations, and fee details from page.
        """
        text = page.get("cleaned_text", "")
        url = page.get("url", "")
        headings = [h for h_list in page.get("headings", {}).values() for h in h_list]
        lists = page.get("lists", [])
        tables = page.get("tables", [])

        discovered_courses: List[Dict[str, Any]] = []
        seen_keys = set()

        # 1. Look in tables (often universities provide structured course tables)
        for tbl in tables:
            headers = [h.lower() for h in tbl.get("headers", [])]
            for row in tbl.get("rows", []):
                row_str = " ".join(row)
                for pat, deg_type, norm_deg in DEGREE_MAPPINGS:
                    if re.search(pat, row_str, re.I):
                        # Find matching specialization
                        spec = None
                        for s in SPECIALIZATIONS:
                            if re.search(r"\b" + re.escape(s) + r"\b", row_str, re.I):
                                spec = s
                                break

                        # Find tuition fees if mentioned in row
                        fee_match = re.search(r"(?:₹|Rs\.?|INR)\s*([0-9,]+)", row_str)
                        fee = f"₹{fee_match.group(1)}" if fee_match else "Published in official prospectus"

                        course_name = f"{norm_deg} in {spec}" if spec else f"{norm_deg} Program"
                        key = f"{course_name}_{deg_type}"
                        if key not in seen_keys:
                            seen_keys.add(key)
                            discovered_courses.append({
                                "name": course_name,
                                "degree_type": deg_type,
                                "specialization": spec,
                                "duration_years": 4.0 if deg_type == "Undergraduate" and "tech" in norm_deg.lower() else (2.0 if deg_type == "Postgraduate" else 3.0),
                                "tuition_fees_annual": fee,
                                "source_url": url,
                                "description": f"Offered as part of institutional programs. Source: {url}"
                            })

        # 2. Look in headings, bullet lists, and paragraphs
        paragraphs = page.get("paragraphs", [])
        combined_items = headings + [item for sublist in lists for item in sublist] + paragraphs
        for item in combined_items:
            for pat, deg_type, norm_deg in DEGREE_MAPPINGS:
                if re.search(pat, item, re.I):
                    for s in SPECIALIZATIONS:
                        if re.search(r"\b" + re.escape(s) + r"\b", item, re.I):
                            course_name = f"{norm_deg} in {s}"
                            key = f"{course_name}_{deg_type}"
                            if key not in seen_keys:
                                seen_keys.add(key)
                                discovered_courses.append({
                                    "name": course_name,
                                    "degree_type": deg_type,
                                    "specialization": s,
                                    "duration_years": 4.0 if "tech" in norm_deg.lower() else 2.0,
                                    "tuition_fees_annual": "Refer official fee matrix",
                                    "source_url": url,
                                    "description": f"Curriculum and specialization details verified from {url}"
                                })

        return discovered_courses
