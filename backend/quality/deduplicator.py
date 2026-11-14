from typing import List, Dict, Any
import re

class Deduplicator:
    @staticmethod
    def deduplicate_courses(courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique = {}
        for c in courses:
            norm_name = re.sub(r"[^a-zA-Z0-9]", "", c.get("name", "").lower())
            deg = (c.get("degree_type") or "").lower()
            key = f"{norm_name}_{deg}"
            if key not in unique:
                unique[key] = c
            else:
                # Merge richer info
                curr = unique[key]
                if (not curr.get("tuition_fees_annual") or "refer" in str(curr.get("tuition_fees_annual")).lower()) and c.get("tuition_fees_annual"):
                    curr["tuition_fees_annual"] = c["tuition_fees_annual"]
                if not curr.get("specialization") and c.get("specialization"):
                    curr["specialization"] = c["specialization"]
                if not curr.get("duration_years") and c.get("duration_years"):
                    curr["duration_years"] = c["duration_years"]

        return list(unique.values())

    @staticmethod
    def deduplicate_admissions(admissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicates admission announcements by academic year and category (UG/PG/PhD/General),
        preserving only the most informative and substantiated records.
        """
        groups: Dict[str, List[Dict[str, Any]]] = {}

        for a in admissions:
            year = a.get("academic_year", "2026-2027")
            title = (a.get("title") or "General").lower()

            # Categorize title
            if "phd" in title or "ph.d" in title:
                cat = "PHD"
            elif "postgraduate" in title or "pg" in title:
                cat = "PG"
            elif "undergraduate" in title or "ug" in title:
                cat = "UG"
            else:
                cat = "GENERAL"

            group_key = f"{year}_{cat}"
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(a)

        def score_admission(adm: Dict[str, Any]) -> int:
            pts = 0
            if adm.get("admission_status") in ("OPEN", "CLOSED", "UPCOMING", "ONGOING"):
                pts += 10
            if adm.get("application_fee"):
                pts += 5
            if adm.get("entrance_exams") and "Merit-based /" not in adm.get("entrance_exams"):
                pts += 5
            if "deadline" in str(adm.get("source_evidence", "")).lower():
                pts += 6
            if "admission" in str(adm.get("source_url", "")).lower():
                pts += 3
            return pts

        deduped = []
        for group_key, items in groups.items():
            # Pick best item in group
            best_item = max(items, key=score_admission)
            deduped.append(best_item)

        return deduped

    @staticmethod
    def deduplicate_faculty(faculty_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique = {}
        for f in faculty_list:
            norm_name = re.sub(r"[^a-zA-Z]", "", f.get("name", "").lower())
            email = f.get("official_email", "")
            key = email if email else norm_name
            if key and key not in unique:
                unique[key] = f
        return list(unique.values())

    @staticmethod
    def deduplicate_scholarships(scholarships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique = {}
        for s in scholarships:
            norm_name = re.sub(r"[^a-zA-Z0-9]", "", s.get("name", "").lower())
            if norm_name not in unique:
                unique[norm_name] = s
        return list(unique.values())
