import re
from typing import Dict, List, Any

# Multi-disciplinary degree catalog across Engineering, Healthcare, Sciences, Management, Law & Humanities
DEGREE_MAPPINGS = [
    # Engineering & Technology
    (r"\b(b\.?tech(?:\.|\b)(?:\s*\([a-z\s\.]+\))?|bachelor of technology|b\.e\.|b\.e\b|b\.eng\b)", "Undergraduate", "B.Tech", 4.0),
    (r"\b(m\.?tech(?:\.|\b)(?:\s*\([a-z\s\.]+\))?|master of technology|m\.e\.|m\.e\b|m\.eng\b)", "Postgraduate", "M.Tech", 2.0),
    (r"\b(diploma in engineering|polytechnic diploma|diploma in\s+[a-z]+)", "Diploma", "Diploma", 3.0),

    # Computing & IT
    (r"\b(bca\b|bachelor of computer applications)", "Undergraduate", "BCA", 3.0),
    (r"\b(mca\b|master of computer applications)", "Postgraduate", "MCA", 2.0),

    # Medical, Dental & Surgical
    (r"\b(mbbs\b|bachelor of medicine and bachelor of surgery)", "Undergraduate", "MBBS", 5.5),
    (r"\b(bds\b|bachelor of dental surgery)", "Undergraduate", "BDS", 5.0),
    (r"\b(mds\b|master of dental surgery)", "Postgraduate", "MDS", 3.0),
    (r"\b(m\.d\.?|doctor of medicine\b)", "Postgraduate", "MD", 3.0),
    (r"\b(m\.s\.?|master of surgery\b)", "Postgraduate", "MS", 3.0),
    (r"\b(bams\b|bachelor of ayurvedic medicine and surgery)", "Undergraduate", "BAMS", 5.5),
    (r"\b(bhms\b|bachelor of homeopathic medicine and surgery)", "Undergraduate", "BHMS", 5.5),

    # Pharmacy
    (r"\b(b\.?pharm(?:\.|\b)|bachelor of pharmacy)", "Undergraduate", "B.Pharm", 4.0),
    (r"\b(m\.?pharm(?:\.|\b)|master of pharmacy)", "Postgraduate", "M.Pharm", 2.0),
    (r"\b(pharm\.?d(?:\.|\b)|doctor of pharmacy)", "Doctorate", "Pharm.D", 6.0),

    # Allied Healthcare & Paramedical Sciences
    (r"\b(bpt\b|bachelor in physiotherapy|bachelor of physiotherapy)", "Undergraduate", "BPT", 4.5),
    (r"\b(mpt\b|master in physiotherapy|master of physiotherapy)", "Postgraduate", "MPT", 2.0),
    (r"\b(b\.?mls\b|bachelor of medical laboratory science)", "Undergraduate", "B.MLS", 3.0),
    (r"\b(m\.?mls\b|master of medical laboratory science)", "Postgraduate", "M.MLS", 2.0),
    (r"\b(b\.?aott\b|baccalaureate in anesthesia & operation theatre technology|bachelor in anesthesia)", "Undergraduate", "B.AOTT", 3.0),
    (r"\b(m\.?aott\b|master in anesthesia & operation theatre technology)", "Postgraduate", "M.AOTT", 2.0),
    (r"\b(b\.?mrit\b|bachelor in medical radiology and imaging technology)", "Undergraduate", "B.MRIT", 3.0),
    (r"\b(mmrit\b|master of medical radiology and imaging technology)", "Postgraduate", "MMRIT", 2.0),
    (r"\b(b\.?optom\b|bachelor in optometry|bachelor of optometry)", "Undergraduate", "B.Optom", 4.0),
    (r"\b(m\.?optom\b|masters in optometry|master of optometry)", "Postgraduate", "M.Optom", 2.0),
    (r"\b(b\.?sc\s+nursing|bachelor of science in nursing)", "Undergraduate", "B.Sc Nursing", 4.0),
    (r"\b(m\.?sc\s+nursing|master of science in nursing)", "Postgraduate", "M.Sc Nursing", 2.0),

    # Sciences & Mathematics
    (r"\b(b\.?sc(?:\.|\b)(?:\s*\([a-z\s\.]+\))?|bachelor of science)", "Undergraduate", "B.Sc", 3.0),
    (r"\b(m\.?sc(?:\.|\b)(?:\s*\([a-z\s\.]+\))?|master of science)", "Postgraduate", "M.Sc", 2.0),

    # Management & Commerce
    (r"\b(mba\b|master of business administration|pgdm\b)", "Postgraduate", "MBA", 2.0),
    (r"\b(bba\b|bachelor of business administration|bbm\b)", "Undergraduate", "BBA", 3.0),
    (r"\b(b\.?com(?:\.|\b)|bachelor of commerce)", "Undergraduate", "B.Com", 3.0),
    (r"\b(m\.?com(?:\.|\b)|master of commerce)", "Postgraduate", "M.Com", 2.0),

    # Law & Humanities
    (r"\b(b\.?a\.?\s*ll\.?b|bba\s*ll\.?b)", "Undergraduate", "BA LL.B", 5.0),
    (r"\b(ll\.?b\b|bachelor of laws)", "Undergraduate", "LL.B", 3.0),
    (r"\b(ll\.?m\b|master of laws)", "Postgraduate", "LL.M", 2.0),
    (r"\b(b\.a\.?|bachelor of arts\b)", "Undergraduate", "B.A", 3.0),
    (r"\b(m\.a\.?|master of arts\b)", "Postgraduate", "M.A", 2.0),
    (r"\b(b\.ed\.?|bachelor of education\b)", "Undergraduate", "B.Ed", 2.0),
    (r"\b(m\.ed\.?|master of education\b)", "Postgraduate", "M.Ed", 2.0),

    # Design & Architecture
    (r"\b(b\.?arch\b|bachelor of architecture)", "Undergraduate", "B.Arch", 5.0),
    (r"\b(b\.?des\b|bachelor of design)", "Undergraduate", "B.Des", 4.0),

    # Doctoral & Research Programs
    (r"\b(ph\.?d(?:\.|\b)|doctor of philosophy)", "PhD", "Ph.D", 3.0),
]

DISALLOWED_PREFIXES = [
    "dr.", "prof.", "professor", "dean", "director", "chancellor", "vice-chancellor",
    "registrar", "mr.", "ms.", "mrs.", "faculty", "hod", "lecturer", "guest"
]

DISALLOWED_PHRASES = [
    "admission", "admissions", "apply now", "admission procedure", "admission process",
    "syllabus", "curriculum pdf", "fee refund", "anti-ragging", "rules and regulations",
    "examination schedule", "hall ticket", "calendar", "committee", "annual report"
]

class CourseExtractor:
    @staticmethod
    def extract_courses(page: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts structured degrees, specializations, durations, and fee details
        from institutional tables, program cards, headers, and bullet listings.
        """
        url = page.get("url", "")
        headings = [h for h_list in page.get("headings", {}).values() for h in h_list]
        lists = page.get("lists", [])
        tables = page.get("tables", [])
        paragraphs = page.get("paragraphs", [])

        discovered_courses: List[Dict[str, Any]] = []
        seen_keys = set()

        # 1. Structured Tables Extraction
        for tbl in tables:
            headers = [h.lower() for h in tbl.get("headers", [])]
            for row in tbl.get("rows", []):
                row_str = " ".join(row).strip()
                if len(row_str) < 4:
                    continue

                for pat, deg_type, norm_deg, default_dur in DEGREE_MAPPINGS:
                    m = re.search(pat, row_str, re.I)
                    if m:
                        # Extract specialization or course title
                        spec = CourseExtractor._extract_specialization(row_str)
                        course_name = f"{norm_deg} in {spec}" if spec else CourseExtractor._clean_program_name(row_str, norm_deg)
                        
                        fee_match = re.search(r"(?:₹|Rs\.?|INR)\s*([0-9,]+)", row_str)
                        fee = f"₹{fee_match.group(1)}" if fee_match else "Refer official fee matrix"

                        dur_match = re.search(r"\b([1-6](?:\.5)?)\s*(?:years?|yrs)\b", row_str, re.I)
                        duration = float(dur_match.group(1)) if dur_match else default_dur

                        key = CourseExtractor._build_key(course_name, deg_type)
                        if key not in seen_keys and CourseExtractor._is_valid_course(course_name):
                            seen_keys.add(key)
                            discovered_courses.append({
                                "name": course_name,
                                "degree_type": deg_type,
                                "specialization": spec,
                                "duration_years": duration,
                                "tuition_fees_annual": fee,
                                "source_url": url,
                                "description": f"Extracted from official curriculum matrix. Source: {url}"
                            })

        # 2. Program Cards, Headings, List Items, and Highlight Paragraphs
        all_text_candidates = []
        for h in headings:
            all_text_candidates.append(h)
        for sublist in lists:
            all_text_candidates.extend(sublist)
        for p in paragraphs:
            if len(p) < 220:
                all_text_candidates.append(p)

        for text_item in all_text_candidates:
            clean_item = text_item.strip()
            if len(clean_item) < 3 or len(clean_item) > 160:
                continue

            # Skip lines describing faculty or administrative actions
            item_lower = clean_item.lower()
            if any(item_lower.startswith(prefix) for prefix in DISALLOWED_PREFIXES):
                continue
            if any(dis in item_lower for dis in ["professor,", "ph.d. admission", "admission 20", "admissions open", "apply now"]):
                continue

            for pat, deg_type, norm_deg, default_dur in DEGREE_MAPPINGS:
                m = re.search(pat, clean_item, re.I)
                if m:
                    spec = CourseExtractor._extract_specialization(clean_item)
                    course_name = CourseExtractor._clean_program_name(clean_item, norm_deg, spec)

                    dur_match = re.search(r"\b([1-6](?:\.5)?)\s*(?:years?|yrs)\b", clean_item, re.I)
                    duration = float(dur_match.group(1)) if dur_match else default_dur

                    fee_match = re.search(r"(?:₹|Rs\.?|INR)\s*([0-9,]+)", clean_item)
                    fee = f"₹{fee_match.group(1)}" if fee_match else "Refer official fee matrix"

                    key = CourseExtractor._build_key(course_name, deg_type)
                    if key not in seen_keys and CourseExtractor._is_valid_course(course_name):
                        seen_keys.add(key)
                        discovered_courses.append({
                            "name": course_name,
                            "degree_type": deg_type,
                            "specialization": spec,
                            "duration_years": duration,
                            "tuition_fees_annual": fee,
                            "source_url": url,
                            "description": f"Verified degree program offered at {url}"
                        })

        return discovered_courses

    @staticmethod
    def _extract_specialization(text: str) -> str:
        """
        Extracts branch/specialization from phrases like 'Specialization: AI & ML'
        or 'in Computer Science and Engineering'.
        """
        spec_match = re.search(r"(?:specialization|speciality|stream|branch)[\s:]+([A-Za-z0-9\s&/\(\)-]+?)(?:\.|$|,|;)", text, re.I)
        if spec_match:
            spec = spec_match.group(1).strip()
            if 2 < len(spec) < 70 and not any(p in spec.lower() for p in DISALLOWED_PHRASES):
                return spec

        in_match = re.search(r"\b(?:in|of)\s+([A-Za-z0-9\s&/\(\)-]+?)(?:\.|$|,|;|\()", text, re.I)
        if in_match:
            spec = in_match.group(1).strip()
            if 2 < len(spec) < 70 and not any(p in spec.lower() for p in DISALLOWED_PHRASES):
                return spec

        return ""

    @staticmethod
    def _clean_program_name(raw_text: str, norm_deg: str, spec: str = "") -> str:
        """
        Normalizes program name into a clean canonical representation.
        """
        cleaned = raw_text.split("|")[0].split("-")[0].strip()
        # Remove trailing colon or dots
        cleaned = re.sub(r"[\.:,]+$", "", cleaned).strip()

        # If specialization was detected and not in the raw degree name
        if spec and spec.lower() not in cleaned.lower():
            return f"{cleaned} in {spec}"

        if len(cleaned) < 5 or cleaned.lower() == norm_deg.lower():
            if spec:
                return f"{norm_deg} in {spec}"
            return f"{norm_deg} Program"

        # Truncate if too long
        if len(cleaned) > 80:
            cleaned = cleaned[:80].strip()

        return cleaned

    @staticmethod
    def _is_valid_course(name: str) -> bool:
        """
        Filters out junk phrases and non-course elements.
        """
        n_low = name.lower()
        if len(name) < 4 or len(name) > 100:
            return False
        if any(p in n_low for p in ["chancellor", "vice chancellor", "registrar", "governing body", "dr."]):
            return False
        if any(p in n_low for p in ["prospectus", "admission enquiry", "apply online", "fee refund", "hall ticket"]):
            return False
        return True

    @staticmethod
    def _build_key(name: str, deg_type: str) -> str:
        norm = re.sub(r"[^a-zA-Z0-9]", "", name.lower())
        return f"{norm}_{deg_type.lower()}"
