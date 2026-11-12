from typing import List, Dict, Any
import re

class Deduplicator:
    @staticmethod
    def deduplicate_courses(courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique = {}
        for c in courses:
            norm_name = re.sub(r"[^a-zA-Z0-9]", "", c.get("name", "").lower())
            deg = c.get("degree_type", "").lower()
            key = f"{norm_name}_{deg}"
            if key not in unique:
                unique[key] = c
            else:
                # Merge richer info
                if not unique[key].get("tuition_fees_annual") and c.get("tuition_fees_annual"):
                    unique[key]["tuition_fees_annual"] = c["tuition_fees_annual"]
        return list(unique.values())

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
