import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class AdmissionExtractor:
    @staticmethod
    def extract_admissions(page: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts verified admission announcements, application periods, entrance exams,
        and statuses. Strictly ignores pages that only contain generic banner slogans.
        """
        text = page.get("cleaned_text", "")
        url = page.get("url", "").lower()
        title = page.get("title", "").lower()

        # Is this an admission-relevant page?
        is_admission_page = any(k in url for k in ["admission", "apply", "counselling", "intake", "eligibility", "prospectus"]) or \
                            any(k in title for k in ["admission", "apply", "eligibility", "counselling"])

        # Academic year detection (e.g., 2026-2027, 2025-26, 2025-2026)
        current_year = datetime.now().year
        year_match = re.search(r"\b(202[3-8])\s*[-/–]\s*(202[4-9]|[2-3][0-9])\b", text)
        if year_match:
            academic_year = f"{year_match.group(1)}-{year_match.group(2)}"
        else:
            academic_year = f"{current_year}-{current_year + 1}"

        # Status determination rules
        status = "UNKNOWN"
        evidence = ""

        open_pattern = re.search(r"(admissions?\s+(?:are\s+)?open|apply\s+online\s+for\s+admission|applications?\s+invited\s+for|admissions?\s+open\s+for\s+academic\s+session)", text, re.I)
        closed_pattern = re.search(r"(admissions?\s+(?:are\s+)?closed|last\s+date\s+has\s+passed|admissions?\s+concluded|application\s+window\s+is\s+closed)", text, re.I)
        upcoming_pattern = re.search(r"(admissions?\s+will\s+commence|applications?\s+will\s+open\s+from|upcoming\s+admission\s+cycle)", text, re.I)
        ongoing_pattern = re.search(r"(counselling\s+in\s+progress|interview\s+rounds\s+ongoing|seat\s+allotment\s+process\s+underway)", text, re.I)

        if open_pattern:
            status = "OPEN"
            evidence = open_pattern.group(0)
        elif closed_pattern:
            status = "CLOSED"
            evidence = closed_pattern.group(0)
        elif upcoming_pattern:
            status = "UPCOMING"
            evidence = upcoming_pattern.group(0)
        elif ongoing_pattern:
            status = "ONGOING"
            evidence = ongoing_pattern.group(0)

        # Entrance exams identification
        exams = []
        exam_keywords = [
            "JEE Main", "JEE Advanced", "GATE", "CAT", "MAT", "NEET", "NEET-UG", "NEET-PG",
            "CUET", "CLAT", "BITSAT", "State CET", "EAPCET", "TS EAMCET", "AP EAMCET", "NATA"
        ]
        for ex in exam_keywords:
            if re.search(r"\b" + re.escape(ex) + r"\b", text, re.I):
                exams.append(ex)

        # Dates / Deadline extraction
        deadline = None
        date_matches = re.findall(r"(?:last\s+date|deadline|opening\s+date|closing\s+date)[\s:]+([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+202[4-8]|[0-9]{1,2}[-/][0-9]{1,2}[-/]202[4-8])", text, re.I)
        if date_matches:
            deadline = date_matches[0]
            evidence += f" | Deadline: {deadline}"

        # Application fee
        fee_match = re.search(r"(?:application\s+fee|registration\s+fee)[\s:]+(?:INR|Rs\.?|₹)?\s*([0-9]+(?:\.[0-9]{2})?)", text, re.I)
        app_fee = f"₹{fee_match.group(1)}" if fee_match else None

        # Qualification check:
        # If this is NOT an admission page and has no specific deadline, exams, or fee,
        # DO NOT produce a duplicate trivial record.
        has_substantive_admission_info = bool(deadline or exams or app_fee or is_admission_page)
        if not has_substantive_admission_info and status == "UNKNOWN":
            return []

        # Determine title
        if "phd" in url or "ph.d" in title:
            title_text = f"Ph.D. Admissions {academic_year}"
        elif "pg" in url or "postgraduate" in title:
            title_text = f"Postgraduate Admissions {academic_year}"
        elif "ug" in url or "undergraduate" in title:
            title_text = f"Undergraduate Admissions {academic_year}"
        else:
            title_text = f"Admissions {academic_year} Announcement"

        return [{
            "academic_year": academic_year,
            "admission_status": status,
            "title": title_text,
            "description": f"Admission cycle details for {academic_year}. Status: {status}. Source: {page.get('url')}",
            "entrance_exams": ", ".join(exams) if exams else "Merit-based / University Entrance Exam",
            "application_fee": app_fee,
            "source_url": page.get("url", ""),
            "source_evidence": evidence or f"Extracted from {page.get('url')}",
            "confidence_score": 0.92 if has_substantive_admission_info else 0.70,
            "verification_status": "VERIFIED" if (status != "UNKNOWN" and has_substantive_admission_info) else "NEEDS_REVIEW"
        }]
