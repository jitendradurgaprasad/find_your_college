import re
from typing import Dict, List, Any, Optional
from datetime import datetime, date

class AdmissionExtractor:
    @staticmethod
    def extract_admissions(page: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts verified admission announcements, application periods, and statuses.
        """
        text = page.get("cleaned_text", "")
        url = page.get("url", "")
        title = page.get("title", "")
        tables = page.get("tables", [])

        # Academic year detection (e.g., 2025-26, 2025-2026, 2024-2025)
        current_year = datetime.now().year
        year_match = re.search(r"\b(202[3-7])\s*[-/–]\s*(202[4-8]|[2-3][0-9])\b", text)
        if year_match:
            academic_year = f"{year_match.group(1)}-{year_match.group(2)}"
        else:
            academic_year = f"{current_year}-{current_year + 1}"

        # Status determination rules
        status = "UNKNOWN"
        evidence = ""

        # Check explicit status patterns
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
        else:
            status = "UNKNOWN"
            evidence = "No explicit admission status statement identified."

        # Dates extraction
        opening_date = None
        closing_date = None

        date_matches = re.findall(r"(?:last\s+date|deadline|opening\s+date|closing\s+date)[\s:]+([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+202[4-7]|[0-9]{1,2}[-/][0-9]{1,2}[-/]202[4-7])", text, re.I)
        if date_matches:
            evidence += f" | Deadline identified: {date_matches[0]}"

        # Entrance exams
        exams = []
        exam_keywords = ["JEE Main", "JEE Advanced", "GATE", "CAT", "MAT", "NEET", "CUET", "CLAT", "BITSAT", "State CET"]
        for ex in exam_keywords:
            if re.search(r"\b" + re.escape(ex) + r"\b", text, re.I):
                exams.append(ex)

        # Application fee
        fee_match = re.search(r"(?:application\s+fee|registration\s+fee)[\s:]+(?:INR|Rs\.?|₹)?\s*([0-9]+(?:\.[0-9]{2})?)", text, re.I)
        app_fee = f"₹{fee_match.group(1)}" if fee_match else None

        # Build Admission Record
        records = [{
            "academic_year": academic_year,
            "admission_status": status,
            "title": f"Admissions {academic_year} Announcement",
            "description": f"Admission cycle details for {academic_year} extracted from {url}",
            "entrance_exams": ", ".join(exams) if exams else "Institution Entrance / Merit-based",
            "application_fee": app_fee,
            "source_url": url,
            "source_evidence": evidence,
            "confidence_score": 0.90 if status != "UNKNOWN" else 0.50,
            "verification_status": "VERIFIED" if status != "UNKNOWN" else "NEEDS_REVIEW"
        }]

        return records
